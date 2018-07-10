import logging
import threading

import zmq

from force_wfmanager.server.event_deserializer import (
    EventDeserializer, DeserializerError)

log = logging.getLogger(__name__)


class ZMQServer(threading.Thread):
    """ZeroMQ based server. It is a state machine with different
    handlers. New behavior is added by adding or modifying the current
    handle methods.

    Handler methods have the form

    _handle_[STATE]_[socket].

    where [STATE] is the string associated to the state (see STATE_* enum
    in class) and [socket] is "pub" for handling data from the pubsub socket,
    "sync" for handling data from the synchronization (req/rep) socket.
    Handlers receive a single parameter `data` (a list) that contains the
    multipart message received. Note that each individual entry of the list
    has already been decoded from utf-8 (our transfer encoding), and is
    therefore a unicode string.
    """

    STATE_STOPPED = "STOPPED"
    STATE_WAITING = "WAITING"
    STATE_RECEIVING = "RECEIVING"

    #: Error types.
    #: Critical: when an error of this category is raised, the server will stop
    #: and then the callback will be invoked
    ERROR_TYPE_CRITICAL = 1

    #: Warning: the server will stay alive and keep processing.
    ERROR_TYPE_WARNING = 2

    def __init__(self, on_event_callback, on_error_callback):
        """Sets up the server with the appropriate configuration.
        When the event is detected, on_event_callback will be called
        _in_the_secondary_thread_.

        Parameters
        ----------
        on_event_callback: function
            A function or method to call when a new event is received.
            This function will be called by the secondary thread
            (this thread).
        on_error_callback: function(error_type, error_message)
            A function or method to call when an error occurs.
            This function will be called by the secondary thread, and will
            accept the error type and the error message arguments.
        """
        super(ZMQServer, self).__init__(name="ZMQServer")
        self.daemon = True
        self.state = ZMQServer.STATE_STOPPED
        self._on_event_callback = on_event_callback
        self._on_error_callback = on_error_callback

        self._context = self._get_context()
        self._pub_socket = None
        self._sync_socket = None
        self._inproc_socket = None
        self._deserializer = EventDeserializer()
        self.ports = None

    def run(self):
        if self.state != ZMQServer.STATE_STOPPED:
            return

        # Socket to talk to server
        log.info("Server started")

        try:
            (self._pub_socket,
             pub_port,
             self._sync_socket,
             sync_port,
             self._inproc_socket) = self._setup_sockets()
        except Exception as e:
            log.exception("Unable to setup sockets")
            self._close_all_sockets_noerror()
            self.state = ZMQServer.STATE_STOPPED
            self._on_error_callback(
                self.ERROR_TYPE_CRITICAL,
                "Unable to setup server sockets: {}.\n"
                "The server is now stopped. You will be unable to "
                "receive progress information from the BDSS.".format(
                    str(e)))
            return

        self.ports = (pub_port, sync_port)

        try:
            poller = self._get_poller()
            poller.register(self._pub_socket)
            poller.register(self._sync_socket)
            poller.register(self._inproc_socket)
        except Exception as e:
            log.exception("Unable to setup sockets")
            self._close_all_sockets_noerror()
            self.state = ZMQServer.STATE_STOPPED
            self._on_error_callback(
                self.ERROR_TYPE_CRITICAL,
                "Unable to register sockets to poller: {}.\n"
                "The server is now stopped. You will be unable to "
                "receive progress information from the BDSS.".format(
                    str(e)))
            return

        self.state = ZMQServer.STATE_WAITING

        while True:
            try:
                events = dict(poller.poll())
            except Exception as e:
                log.exception("Unable to poll")
                self._close_all_sockets_noerror()
                self.state = ZMQServer.STATE_STOPPED
                self._on_error_callback(
                    self.ERROR_TYPE_CRITICAL,
                    "Unable to poll sockets: {}.\n"
                    "The server is now stopped. You will be unable to "
                    "receive progress information from the BDSS.".format(
                        str(e)))
                return

            for socket_name, socket in [
                    ("pub", self._pub_socket),
                    ("sync", self._sync_socket),
                    ]:

                if socket not in events:
                    continue

                try:
                    data = [x.decode('utf-8') for x in socket.recv_multipart()]
                except Exception as e:
                    log.exception("Unable to retrieve data")
                    self._on_error_callback(
                        self.ERROR_TYPE_WARNING,
                        "Unable to retrieve data from socket: {}.".format(
                            str(e)))

                try:
                    handle = getattr(
                        self,
                        "_handle_"+self.state+"_"+socket_name)
                except AttributeError:
                    log.error("State {} cannot handle {} data. "
                              "Discarding.".format(self.state, socket_name))
                    continue

                try:
                    handle(data)
                except Exception as e:
                    log.exception("Handler {} raised exception.".format(
                        handle))
                    self._close_all_sockets_noerror()
                    self.state = ZMQServer.STATE_STOPPED
                    self._on_error_callback(
                        self.ERROR_TYPE_CRITICAL,
                        "Handler {} raised exception {}\n"
                        "The server is now stopped. You will be unable to "
                        "receive progress information from the BDSS.".format(
                            handle, str(e)))
                    return

            if self._inproc_socket in events:
                self._inproc_socket.recv()
                self._close_network_sockets_noerror()
                self.state = ZMQServer.STATE_STOPPED
                self._inproc_socket.send(''.encode('utf-8'))
                self._inproc_socket.close()
                return

    def stop(self):
        """Stops the server. This method is synchronous.
        It stops until the server acknowledges that it
        stopped. It does however give up after a second if
        the stop sequence is not respected.
        """
        if self.state == ZMQServer.STATE_STOPPED:
            return

        socket = None
        try:
            socket = self._context.socket(zmq.PAIR)
            socket.setsockopt(zmq.RCVTIMEO, 1000)
            socket.setsockopt(zmq.SNDTIMEO, 1000)
            socket.setsockopt(zmq.LINGER, 0)
            socket.connect("inproc://stop")
            socket.send("".encode("utf-8"))
            socket.recv()
        except Exception:
            # If anything goes wrong at this stage, just log it and
            # ignore
            log.exception("Error while attempting to stop server")
        finally:
            if socket:
                socket.close()

    def _setup_sockets(self):
        """Sets up the sockets."""
        context = self._context
        pub_socket = context.socket(zmq.SUB)
        pub_socket.setsockopt(zmq.SUBSCRIBE, "".encode("utf-8"))
        pub_socket.setsockopt(zmq.LINGER, 0)
        pub_port = pub_socket.bind_to_random_port("tcp://*")

        sync_socket = context.socket(zmq.REP)
        sync_socket.setsockopt(zmq.LINGER, 0)
        sync_port = sync_socket.bind_to_random_port("tcp://*")

        inproc_socket = context.socket(zmq.PAIR)
        inproc_socket.bind("inproc://stop")
        return pub_socket, pub_port, sync_socket, sync_port, inproc_socket

    def _close_network_sockets_noerror(self):
        self.ports = None
        try:
            self._pub_socket.close()
        except:
            pass
        self._pub_socket = None

        try:
            self._sync_socket.close()
        except:
            pass
        self._sync_socket = None

    def _close_all_sockets_noerror(self):
        self._close_network_sockets_noerror()
        try:
            self._inproc_socket.close()
        except:
            pass

        self._inproc_socket = None

    def _get_context(self):
        return zmq.Context()

    def _get_poller(self):
        return zmq.Poller()

    # Handlers. Check format in class docstring.

    def _handle_WAITING_sync(self, data):
        if len(data) != 3:
            log.error("Unknown request received {}".format(data))
            return

        msg, identifier, protocol = data
        if msg != "HELLO":
            log.error("Unknown msg request received {}".format(msg))
            return

        if protocol != "1":
            log.error("Unknown protocol received {}".format(protocol))
            return

        self._sync_socket.send_multipart([x.encode('utf-8') for x in data])

        self.state = ZMQServer.STATE_RECEIVING

    def _handle_RECEIVING_sync(self, data):
        if len(data) != 2:
            log.error("Unknown request received {}".format(data))
            return

        msg, identifier = data

        if msg != "GOODBYE":
            log.error("Unknown msg request received {}".format(msg))
            return

        self._sync_socket.send_multipart([x.encode('utf-8') for x in data])

        self.state = ZMQServer.STATE_WAITING

    def _handle_RECEIVING_pub(self, data):
        if len(data) != 3:
            log.error("Unknown request received {}".format(data))
            return

        msg, identifier, serialized_data = data

        if msg != "MESSAGE":
            log.error("Unknown msg request received {}".format(msg))
            return

        try:
            event = self._deserializer.deserialize(serialized_data)
        except DeserializerError:
            log.error("Received invalid data. Discarding")
            return

        try:
            self._on_event_callback(event)
        except Exception:
            log.exception("on_event_callback raised exception")

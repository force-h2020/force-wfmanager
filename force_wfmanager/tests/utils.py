import time


class TimeoutError(Exception):
    pass


def wait_condition(condition, seconds=5):
    count = 0
    while True:
        if condition():
            break
        time.sleep(1)
        count += 1
        if count == seconds:
            raise TimeoutError("timeout")

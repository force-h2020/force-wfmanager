import unittest
import subprocess


class TestExecution(unittest.TestCase):

    def test_command_line_invocation(self):
        """Test if the workflow manager can be loaded from the command line"""

        # Does the command exist?
        available_commands = subprocess.check_output(['/bin/bash', '-c', 'compgen -c'])
        available_commands = available_commands.splitlines()
        command_found = False

        # available_commands is a list with elements of type: 'bytes'
        for command in available_commands:
            if command == b'force_wfmanager':
                command_found = True
        if command_found is False:
            self.fail("Command \'force_wfmanager\' does not exist in the list of available bash commands")

        # Does it execute correctly?
        print("Close the workflow manager to complete the test!")
        try:
            subprocess.check_output(["force_wfmanager"])
        except subprocess.CalledProcessError:
            self.fail("Couldn't load workflow manager")


if __name__ == "__main__":
    unittest.main()
import subprocess
import unittest


class TestUtils(unittest.TestCase):

    def test_server(self):
        # Comando para enviar un mensaje al servidor usando netcat.
        # Envío el mensaje "Testing server"
        test_msg = "Testing server"
        NC_COMMAND = f"echo '{test_msg}' | nc server 12345"
        output = subprocess.check_output(["docker", "run", 
                                        "--network=tp0_testing_net", "busybox",
                                        "sh", "-c", NC_COMMAND])


        output = output.decode().strip()
        self.assertEqual(test_msg, output)

if __name__ == '__main__':
    unittest.main()

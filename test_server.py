import subprocess

# Comando para enviar un mensaje al servidor usando netcat.
# Envío el mensaje "Testing server"
NC_COMMAND = "echo 'Testing server' | nc server 12345"
output = subprocess.check_output(["docker", "run", 
                                "--network=tp0_testing_net", "busybox",
                                "sh", "-c", NC_COMMAND])

if output.decode().strip() == "Testing server":
    print("EchoServer: SUCCESS.")
else:
    print("EchoServer: FAILURE.")

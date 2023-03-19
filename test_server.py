import subprocess

# Comando para enviar un mensaje al servidor usando netcat
NC_COMMAND = "echo 'hello world' | nc server 12345"

# Ejecutar el comando en un contenedor Docker en la misma red que el servidor
output = subprocess.check_output(["docker", "run", "--network=tp0_testing_net", "busybox", "sh", "-c", NC_COMMAND])

# Verificar si el mensaje recibido es igual al mensaje enviado
if output.decode().strip() == "hello world":
    print("El servidor está funcionando correctamente.")
else:
    print("Hubo un problema al interactuar con el servidor.")

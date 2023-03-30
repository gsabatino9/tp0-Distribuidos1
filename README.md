# Ejercicio 4

El flag `-t` del comando `docker compose down` setea un timeout de 10 segundos (por default) para esperar a que el contenedor finalice de forma graceful.

Es decir, envía la señal SIGTERM al contenedor y espera 10 segundos a que este cierre los file descriptors que necesite. Si pasados los 10 segundos no se liberan, envía la señal SIGKILL indicándole al sistema operativo que termine el proceso inmediatamente.

En el makefile se utiliza 1 segundo como tiempo máximo.

Puesto que ambas aplicaciones (como se verá en cada subsección) liberan una pequeña cantidad de recursos, se sigue manteniendo en 1 segundo el tiempo de espera antes de matar al proceso de forma inmediata.

En las dos siguientes subsecciones se especifica qué se modificó del cliente y del servidor.


## Servidor
Se modifica la inicialización del servidor (en `server.py`) para que comience a registrar si se recibe la señal SIGTERM en el hilo principal de la aplicación.

Se setea un flag interno del servidor que, una vez se recibe la señal, indica que debe finalizar el loop en la función `run()`.

Cuando se recibe una señal, se llama a la función `stop()` que cierra el file descriptor del socket del servidor, antes de que el thread de la aplicación principal muera.

A su vez, se guarda el socket de conexión con el cliente. Si llega la señal SIGTERM, se cierra directamente el socket (no hace un cierre polite de recursos, sino un cierre graceful).

## Cliente
Se modifica también la inicialización en el cliente (en `client.go`) para que escuche si ocurre SIGTERM en un canal.

En la función `StartClientLoop` se realizan dos verificaciones:
1. Si se recibe SIGTERM adentro del loop (quiere decir que el cliente no está durmiendo), se destruye el socket conectado con el servidor y se loguea dicha operación.
2. Si el cliente estaba ejecutando un `sleep`, entonces se vuelve a chequear si se recibe SIGTERM y el programa finaliza.

Sin (2), como los tiempos que espera docker por cada cliente se suma, si hago muchos clientes que están ejecutando `sleep`, el timeout ocurriría y se enviaría la señal SIGKILL. De esta manera, se está bajando la probabilidad.
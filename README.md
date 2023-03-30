# Parte 1
## Ejercicio 1
El cliente fue agregado al archivo `docker-compose-dev.yaml`.

Se agregó al archivo:
```yaml
client2:
    container_name: client2
    image: client:latest
    entrypoint: /client
    environment:
      - CLI_ID=2
      - CLI_LOG_LEVEL=DEBUG
    networks:
      - testing_net
    depends_on:
      - server
```

## Ejercicio 1.1

El script se realizó en python, llamado `create_docker_compose.py`.

Se ejecuta con la siguiente línea de comando:
```python
python3 create_docker_compose.py num_clientes
```

donde `num_clientes` es la cantidad de clientes que se quiere tener levantados.

**Nota 1**: El script modifica directamente el archivo `docker-compose-dev.yaml` para poder seguir utilizando el makefile.

**Nota 2**: Se utilizó la librería pyyaml para que el código quede más simple. Si existe algún error: `pip install pyyaml`.

## Ejercicio 2
Se creó un volumen en el cliente y en el servidor para lograr que realizar cambios en el archivo de configuración no requiera un nuevo build de las imágenes de Docker para que los mismos sean efectivos.

Se agregó, en el `docker-compose-dev.yaml`:
En el servidor:
```yaml
volumes:
      - server_data:/data
```

Y en cada cliente que se crea:
```yaml
volumes:
      - ./client/config:/config
```

### Línea de ejecución
```shell
python3 create_docker_compose.py num_clients
make docker-compose-up && make docker-compose-logs
```

## Ejercicio 3
El script se llama `test_server.sh`, que se levanta con la siguiente línea:
```shell
./testing.sh
```
**Nota:** En Mac es necesario darle permiso al script, se puede realizar ejecutando:
```shell
chmod 775 ./testing.sh
```

El scrip realiza las siguientes operaciones:
* Construyo una imagen con la última distribución de alpine y descarga el programa `netcat`.
* Levanto el servidor utilizando `make docker-compose-up`. Lo realizo en modo silencioso para no que la terminal no quede con muchos mensajes.
* Ejecuto la línea:
```shell
docker run --rm --network=tp0_testing_net netcat-container sh -c 'echo PING | nc server 12345'
```
es decir, me contecto a la misma red que el servidor y le envío un ping con netcat.
* Me fijo si el servidor retorna correctamete e imprimo por pantalla.
* Cierro recursos en modo silencioso.

### Output
```shell
$ ./testing.sh

Construyendo imagen con netcat.
Imagen con netcat construida.
Levantando EchoServer.
EchoServer listo.
SUCCESS: EchoServer retorna correctamente.
EchoServer cerrado.
```

## Ejercicio 4

El flag `-t` del comando `docker compose down` setea un timeout de 10 segundos (por default) para esperar a que el contenedor finalice de forma graceful.

Es decir, envía la señal SIGTERM al contenedor y espera 10 segundos a que este cierre los file descriptors que necesite. Si pasados los 10 segundos no se liberan, envía la señal SIGKILL indicándole al sistema operativo que termine el proceso inmediatamente.

En el makefile se utiliza 1 segundo como tiempo máximo.

Puesto que ambas aplicaciones (como se verá en cada subsección) liberan una pequeña cantidad de recursos, se sigue manteniendo en 1 segundo el tiempo de espera antes de matar al proceso de forma inmediata.

En las dos siguientes subsecciones se especifica qué se modificó del cliente y del servidor.


### Servidor
Se modifica la inicialización del servidor (en `server.py`) para que comience a registrar si se recibe la señal SIGTERM en el hilo principal de la aplicación.

Se setea un flag interno del servidor que, una vez se recibe la señal, indica que debe finalizar el loop en la función `run()`.

Cuando se recibe una señal, se llama a la función `stop()` que cierra el file descriptor del socket del servidor, antes de que el thread de la aplicación principal muera.

A su vez, se guarda el socket de conexión con el cliente. Si llega la señal SIGTERM, se cierra directamente el socket (no hace un cierre polite de recursos, sino un cierre graceful).

### Cliente
Se modifica también la inicialización en el cliente (en `client.go`) para que escuche si ocurre SIGTERM en un canal.

En la función `StartClientLoop` se realizan dos verificaciones:
1. Si se recibe SIGTERM adentro del loop (quiere decir que el cliente no está durmiendo), se destruye el socket conectado con el servidor y se loguea dicha operación.
2. Si el cliente estaba ejecutando un `sleep`, entonces se vuelve a chequear si se recibe SIGTERM y el programa finaliza.

Sin (2), como los tiempos que espera docker por cada cliente se suma, si hago muchos clientes que están ejecutando `sleep`, el timeout ocurriría y se enviaría la señal SIGKILL. De esta manera, se está bajando la probabilidad.


---
# Parte 2
## Protocolo de comunicación
## Tipo de protocolo
Se cuenta con un protocolo híbrido:
* En primera instancia se manda la cantidad de bytes que se van a enviar a continuación del mensaje.
* Luego, se cuenta con un protocolo de texto, utilizando la librería json.

Se utilizó un protocolo de texto por sus facilidades para codificar de forma rápida y poder debuggear en la terminal (que cobró mayor importancia en el ejercicio 8 de concurrencia).

A su vez, puesto que (como se explica a continuación), la cantidad de campos no es elevada, no se pierde una gran cantidad de Bytes con este protocolo. Por lo tanto, se decidió mantenerlo pese a que un protocolo binario es más eficiente.

## Formato
### Cliente a servidor
El protocolo consta de 3 campos:
* `type_message`: SEND_CHUNK, SEND_LAST_CHUNK, CONSULT_AGENCY_WINNERS. Se utiliza el concepto de "chunk" para mantener el protocolo coherente con el resto de los ejercicios, aunque en el 5 el "chunk" esté compuesto únicamente de un paquete.
* `agency`: Se indica el número de agencia que quiere realizar la operación.
* `payload` (opcional): En el caso de mandar un paquete/chunk de paquetes, se especifica una lista con los mismos.

### Servidor a cliente
El protocolo consta de 2 campos:
* `type_message`: CHUNK_PROCESSED (todos los paquetes en un chunk fueron almacenados con éxito), INFORM_AGENCY_WINNERS (informar a la agencia quiénes son *sus* ganadores).
* `payload` (opcional): En el caso de mandar los ganadores a una agencia, se especifica una lista con los documentos de los mismos.

## Limitación del tamaño de los paquetes
Para no enviar paquetes de más de 8KB (en total, incluyendo headers TCP), se realiza:
1. Se define una constante `MAX_SIZE` que es menor a 8KB contando el header TCP.
2. Se construye el paquete entero con todos los campos del protocolo.
3. Se obtiene el tamaño de dicho paquete.
4. Si el paquete supera la cantidad máxima, se divide en N paquetes que tengan todo como capacidad máxima `MAX_SIZE`. Ejemplo: Si `MAX_SIZE=8` y el tamaño del paquete es de 21, se envían tres paquetes de tamaños [8, 8, 5].

## Evitar short reads
1. El extremo de emisión envía la cantidad de bytes totales que va a enviar. (utilizando 4 bytes).
2. El extremo de recepción calcula todos los sub-paquetes (en caso de que el tamaño recibido supere `MAX_SIZE`).
3. Por cada tamaño de los sub-paquetes, intenta recibir ese tamaño. En caso de que se lea una menor cantidad de bytes, se utiliza un loop donde en cada iteración se resta al tamaño original el tamaño leído en el buffer. Esta lógica se encuentra condensada en la función `__recv_all()` del protocolo, intentando emular `sendall()` de python.
4. Se construye el paquete entero (que puede tener una cantidad de bytes mayor al permitido) concatenando todos los bytes leídos.

## Evitar short writes
Para esto se utiliza la función `sendall` de python que se encarga de verificar que se mandaron todos los bytes y, en caso contrario, lanza una excepción.

---

## Ejercicio 5

Se realizaron tanto el cliente como el servidor en python.

Cada cliente se conecta de forma secuencial al servidor y envía una sola apuesta (esperando que haya sido realizado correctamente).

La secuencia lógica es:
1. Cliente envía un paquete del tipo SEND_LAST_CHUNK al servidor, con la agencia como su número de id. El cliente se queda esperando la respuesta exitosa por parte del servidor.
2. El servidor recibe el paquete (utilizando el protocolo para deserializar y recibir todos los bytes evitando un short read).
3. Almacena la apuesta.
4. Loguea con éxito que la apuesta fue almacenada.
5. Envía un paquete al cliente del tipo CHUNK_PROCESSED al cliente.
6. El cliente lo recibe (de forma análoga al servidor) y loguea el éxito.

### Ejecución

Se cuenta con un script `server_up.sh` que genera el `docker-compose-dev.yaml` con datos randomizados (a cada cliente le genera nombres, apellidos, etc), realiza un `make docker-compose-up` y un `make docker-compose-logs`.

La línea de ejecución es:
```shell
./server_up.sh | tee output.txt
```
De esta manera, se levanta el servidor, se pueden visualizar los logs en la terminal y se duplican los logs en el archivo "output.txt" para poder realizar, por ejemplo, un `cat` de la salida.

Y para cerrar el servidor y los 5 clientes se utiliza el comando
```shell
make docker-compose-down
```

### Output
Ejecutando con la anterior línea, se obtiene:

**Clientes:**
```shell
cat output.txt | grep 'action: apuesta_enviada'

client3  | 2023-03-30 21:50:49 INFO     action: apuesta_enviada | result: success | dni: 66423202 | numero: 2979
client2  | 2023-03-30 21:50:49 INFO     action: apuesta_enviada | result: success | dni: 56461140 | numero: 8587
client5  | 2023-03-30 21:50:49 INFO     action: apuesta_enviada | result: success | dni: 83451263 | numero: 5747
client4  | 2023-03-30 21:50:49 INFO     action: apuesta_enviada | result: success | dni: 67493119 | numero: 1292
client1  | 2023-03-30 21:50:49 INFO     action: apuesta_enviada | result: success | dni: 61448203 | numero: 6081
```

**Servidor:**
```shell
cat output.txt | grep 'action: apuesta_almacenada'

server   | 2023-03-30 21:50:49 INFO     action: apuesta_almacenada | result: success | dni: 83451263 | numero: 5747
server   | 2023-03-30 21:50:49 INFO     action: apuesta_almacenada | result: success | dni: 56461140 | numero: 8587
server   | 2023-03-30 21:50:49 INFO     action: apuesta_almacenada | result: success | dni: 66423202 | numero: 2979
server   | 2023-03-30 21:50:49 INFO     action: apuesta_almacenada | result: success | dni: 67493119 | numero: 1292
server   | 2023-03-30 21:50:49 INFO     action: apuesta_almacenada | result: success | dni: 61448203 | numero: 6081
```

Verificando que la información es la misma en ambos casos.

## Ejercicio 6

La modificación con respecto al ejercicio anterior es la posibilidad de que el cliente mande chunks de apuestas, en lugar de una sola.

Se define una constante `CHUNK_SIZE` como variable de entorno del cliente, y se setea en 1000 para que sean menos corridas.

La única diferencia con el ejercicio 5, utilizando el protocolo especificado anteriormente, es ir procesando cada chunk del archivo de cada cliente (definido por 'agency-id_cliente.csv') y entender cuándo se llega al último chunk de paquetes para notificar al servidor.

De esta manera:
1. El cliente abre el archivo y va leyendo de a `CHUNK_SIZE` apuestas.
2. Si no se llega al final luego de ese chunk, se le envía al servidor un paquete del tipo SEND_CHUNK.
3. Si se llega al final luego de ese chunk, se envía al servidor un paquete del tipo SEND_LAST_CHUNK.
4. En (2) y (3) el cliente se queda esperando que el servidor le notifique que todos los paquetes fueron procesados con éxito.
5. El servidor procede igual que en el ejercicio 5, a excepción de ir tomando nota de cuántas agencias finalizaron su ejecución. Cuando llega a la cantidad de clientes seteada en el archivo de configuración (5 para este tp0), el servidor finaliza.

### Output
En este caso, para hacer un chequeo rápido de que los clientes y el servidor funcionan de forma correcta, se proveen las siguientes dos líneas de ejecución, con sus outputs.

**Servidor:**
```shell
$ ./server_up.sh | tee output.txt
$ cat output.txt | grep 'action: apuestas_almacenadas' | grep 'agencia: 1' | wc -l

      27
```

Se aprecia que se muestran cuántos chunks de paquetes fueron almacenados de la agencia 1.

**Cliente 1:**
```shell
$cat output.txt | grep 'action: apuestas_enviadas' | grep 'agencia: 1' | wc -l

      27
```

Se aprecia que, en ambos casos, se enviaron y almacenaron la misma cantidad de chunks de paquetes.

## Ejercicio 7
La modificación respecto de los ejercicios anteriores es que ahora el servidor debe realizar acciones luego de que le hayan llegado todas las apuestas de las 5 agencias.

Para esto:
1. Los clientes le envían al servidor los chunks de paquetes como en el ejercicio anterior.
2. Cada cliente, luego de enviar el último chunk, quiere recibir ahora la notificación de cuántos ganadores tiene su agencia. Para esto, le envía un mensaje del tipo CONSULT_AGENCY_WINNERS, con su número de agencia al servidor.
3. Cada cliente, luego de enviar ese último mensaje, se queda esperando por un mensaje del tipo INFORM_AGENCY_WINNERS por parte del servidor.
4. Cuando el servidor termina de procesar todos los clientes de forma correcta, procede a realizar el sorteo.
5. Luego de realizar el sorteo, obtiene todos los ganadores con la función `has_won` por cada apuesta que tiene (cabe destacar que cuenta con todas las apuestas posibles puesto que finalizó la primera etapa).
6. El servidor le envía a cada agencia un mensaje del tipo INFORM_AGENCY_WINNERS, con una lista de documentos de los ganadores de esa agencia.

### Output
**Servidor:**
```shell
$ ./system_up.sh | tee output.txt
$ cat output.txt | grep 'action: sorteo'

server   | 2023-03-30 22:13:58 INFO     action: sorteo | result: success
```

**Clientes:**
```shell
$ cat output.txt | grep 'action: consulta_ganadores'

client3  | 2023-03-30 22:13:58 INFO     action: consulta_ganadores | result: success | cant_ganadores: 3
client2  | 2023-03-30 22:13:58 INFO     action: consulta_ganadores | result: success | cant_ganadores: 3
client1  | 2023-03-30 22:13:58 INFO     action: consulta_ganadores | result: success | cant_ganadores: 2
client4  | 2023-03-30 22:13:58 INFO     action: consulta_ganadores | result: success | cant_ganadores: 2
client5  | 2023-03-30 22:13:58 INFO     action: consulta_ganadores | result: success | cant_ganadores: 0
```

Verificando en cada archivo buscando por las apuestas que coinciden con la definida en `server/common/utils.py`, se verifica que esas son las cantidades correctas de ganadores por cada agencia.

---

# Parte 3 - Ejercicio 8
## Mecanismos de concurrencia utilizados
### Dos servidores
Como primera medida, se decidió contar con dos procesos aceptadores diferentes (dos sockets distintos) para el servidor:
* Un proceso que acepta conexiones de clientes para procesar apuestas.
* Otro proceso que acepta conexiones de clientes que quieren consultar sus ganadores.

De esta manera, cada cliente abre dos conexiones con el servidor (ambas direcciones del servidor se definen en el `config.yaml` del cliente).

### Procesamiento de apuestas
Para procesar apuestas de forma paralela se utiliza:
* Un pool de procesos para procesar los mensajes de los clientes: en este pool, se define una cola de conexiones (`communications_queue`) que sirve para extraer una comunicación con un cliente, procesar un chunk de apuestas (que puede o no ser el último) y volver a insertar en la queue la conexión con el cliente. De esta manera, cada cliente abre solo una conexión, pero sus chunks de apuestas pueden ser procesados por distintos procesos. Así, se evita que, si se cuentan con 4 procesos y 5 clientes, uno siempre quede en espera.
* Un flag atómico entre procesos para indicar cuando todos los clientes procesaron todas sus apuestas: Este flag es pasado entre procesos y, cuando se llega a la cantidad de clientes, se setea este flag para que finalice tanto el proceso aceptador como el pool de procesos.
* Un lock de archivo para que cada proceso dentro del pool pueda realizar un `store_bets` de forma que sea process_safe (puesto que la función no realiza ningún lock ni se puede modificar).
* Un lock sobre la cantidad de procesos finalizados para que, cuando se llegue al máximo (la cantidad de clientes, 5 en este caso), se setee el flag atómico. 
* El proceso principal para realizar la apuesta: Una vez que el pool de procesos finaliza, todos los clientes procesaron todas sus apuestas. De esta manera, procede a realizar las apuestas (cargarlas con `load_bets`) sin realizar lock puesto que los anteriores procesos fueron finalizados.
* Un último proceso para informar a los ganadores de cada agencia: El proceso aceptador realiza un push en una cola de agencias que consultan (`consults_queue`) con las conexiones establecidas. Este proceso se lanza una vez que el sorteo fue realizado de forma exitosa, por lo tanto, ya se cuenta con los ganadores de cada agencia. Para este proceso, se obtiene una conexión con un cliente (realizando un pop de `consults_queue`), se recibe un mensaje del tipo CONSULT_AGENCY_WINNERS, y se le envía a esa agencia una lista con todos sus ganadores.
* Las queues utilizadas son colas bloqueantes a nivel de procesos.

Cabe destacar que se utilizó la librería `Multiprocessing`, para contar con todas las abstracciones para sincronizar procesos mencionadas en los ítems anteriores.

## Ventajas del enfoque utilizado
Este enfoque permite contar con un alto grado de paralelismo para la cantidad de clientes planteada. Cada cliente abre solo una conexión para procesar sus apuestas, que las pueden procesar procesos distintos, aunque no pueden ser paralelas puesto que cada cliente espera por la confirmación del servidor de todo el chunk procesado.

A su vez, contar con dos conexiones dedicadas para cada tipo de procesamiento disminuyó la lógica de sincronización entre distintos procesos, y permitió que el pool de procesos sea dedicado únicamente a procesar chunks (lo que maximiza el paralelismo para procesar grandes volúmenes de apuestas).

Así, el procesamiento y la información de los ganadores se pueden ver como dos módulos separados.

## Desventajas
Para este tp0, mi solución no presenta mayores inconvenientes en lo relativo al paralelismo. Pero, si se quiere escalar para millones de clientes, se puede contar con un inconveniente si cada uno se queda bloqueado esperando a que le notifiquen el resultado de sus chunks y de los ganadores de su agencia.

Se podría utilizar un algoritmo de pooling usando un exponential backoff (aleatorio) para realizar consultas y obtener respuestas del servidor en el momento por los ganadores de cada agencia. Si no están listos, se retorna un tipo de mensaje especializado para ello.

## Mejoras de este ejercicio
Este ejercicio no cuenta con el mismo graceful shutdown que el resto de los ejercicios, puesto que intenté realizar el cierre de recursos a nivel procesos pero me quedé sin tiempo.

Este apartado resulta clave para un correcto funcionamiento del tp. En este caso, si se da de baja al programa con `make docker-compose-down`, el programa puede presentar bugs para su liberación de recursos-
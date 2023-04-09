# Protocolo de comunicación
## Tipo de protocolo
Se cuenta con un protocolo binario que tiene:
* Un header (que contiene el tipo de mensaje entre otros campos).
* Un payload (que contiene la información a enviar al otro extremo).

## Formato
### Cliente a servidor
El header consta de 3 campos:
* `code`: SEND_BET, SEND_LAST_BET.
* `agency`: Se indica el número de agencia que quiere realizar la operación.
* `len`: El largo del payload (en bytes) a enviar.

El payload contiene únicamente la apuesta en formato de string.

### Servidor a cliente
El header consta de 2 campos:
* `code`: BET_PROCESSED (indicando que la apuesta fue almacenada).
* `len`: Para los puntos siguientes, en el caso de querer enviar quiénes son los ganadores de la agencia.

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

# Ejercicio 5

Se realizaron tanto el cliente como el servidor en python.

Cada cliente se conecta de forma secuencial al servidor y envía una sola apuesta (esperando que haya sido realizado correctamente).

La secuencia lógica es:
1. Cliente envía un paquete del tipo SEND_LAST_BET al servidor, con la agencia como su número de id. El cliente se queda esperando la respuesta exitosa por parte del servidor.
2. El servidor recibe el paquete (utilizando el protocolo para deserializar y recibir todos los bytes evitando un short read).
3. Almacena la apuesta.
4. Loguea con éxito que la apuesta fue almacenada.
5. Envía un paquete al cliente del tipo BET_PROCESSED al cliente.
6. El cliente lo recibe (de forma análoga al servidor) y loguea el éxito.

## Ejecución

La línea de ejecución es:
```shell
make docker-compose-up && make docker-compose-logs | tee output.txt
```
De esta manera, se levanta el servidor, se pueden visualizar los logs en la terminal y se duplican los logs en el archivo "output.txt" para poder realizar, por ejemplo, un `cat` de la salida.

Y para cerrar el servidor y los 5 clientes se utiliza el comando
```shell
make docker-compose-down
```

## Output
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
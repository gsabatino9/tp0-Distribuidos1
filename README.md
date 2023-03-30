# Mecanismos de concurrencia utilizados
## Dos servidores
Como primera medida, se decidió contar con dos procesos aceptadores diferentes (dos sockets distintos) para el servidor:
* Un proceso que acepta conexiones de clientes para procesar apuestas.
* Otro proceso que acepta conexiones de clientes que quieren consultar sus ganadores.

De esta manera, cada cliente abre dos conexiones con el servidor (ambas direcciones del servidor se definen en el `config.yaml` del cliente).

## Procesamiento de apuestas
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

Este apartado resulta clave para un correcto funcionamiento del tp. En este caso, si se da de baja al programa con `make docker-compose-down`, el programa puede presentar bugs para la liberación de recursos.
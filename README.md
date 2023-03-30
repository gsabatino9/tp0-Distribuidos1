# Ejercicio 7
La modificación respecto de los ejercicios anteriores es que ahora el servidor debe realizar acciones luego de que le hayan llegado todas las apuestas de las 5 agencias.

Para esto:
1. Los clientes le envían al servidor los chunks de paquetes como en el ejercicio anterior.
2. Cada cliente, luego de enviar el último chunk, quiere recibir ahora la notificación de cuántos ganadores tiene su agencia. Para esto, le envía un mensaje del tipo CONSULT_AGENCY_WINNERS, con su número de agencia al servidor.
3. Cada cliente, luego de enviar ese último mensaje, se queda esperando por un mensaje del tipo INFORM_AGENCY_WINNERS por parte del servidor.
4. Cuando el servidor termina de procesar todos los clientes de forma correcta, procede a realizar el sorteo.
5. Luego de realizar el sorteo, obtiene todos los ganadores con la función `has_won` por cada apuesta que tiene (cabe destacar que cuenta con todas las apuestas posibles puesto que finalizó la primera etapa).
6. El servidor le envía a cada agencia un mensaje del tipo INFORM_AGENCY_WINNERS, con una lista de documentos de los ganadores de esa agencia.

## Output
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
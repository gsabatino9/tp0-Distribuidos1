# Ejercicio 6

La modificación con respecto al ejercicio anterior es la posibilidad de que el cliente mande chunks de apuestas, en lugar de una sola.

Se define una constante `CHUNK_SIZE` como variable de entorno del cliente, y se setea en 1000 para que sean menos corridas.

La única diferencia con el ejercicio 5, utilizando el protocolo especificado anteriormente, es ir procesando cada chunk del archivo de cada cliente (definido por 'agency-id_cliente.csv') y entender cuándo se llega al último chunk de paquetes para notificar al servidor.

De esta manera:
1. El cliente abre el archivo y va leyendo de a `CHUNK_SIZE` apuestas.
2. Si no se llega al final luego de ese chunk, se le envía al servidor un paquete del tipo SEND_CHUNK.
3. Si se llega al final luego de ese chunk, se envía al servidor un paquete del tipo SEND_LAST_CHUNK.
4. En (2) y (3) el cliente se queda esperando que el servidor le notifique que todos los paquetes fueron procesados con éxito.
5. El servidor procede igual que en el ejercicio 5, a excepción de ir tomando nota de cuántas agencias finalizaron su ejecución. Cuando llega a la cantidad de clientes seteada en el archivo de configuración (5 para este tp0), el servidor finaliza.

## Output
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
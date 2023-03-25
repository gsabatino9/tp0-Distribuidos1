# Ejercicio 5

## Ejecución

Se cuenta con un script `server_up.sh` que genera el `docker-compose-dev.yaml` con datos randomizados (a cada cliente le genera nombres, apellidos, etc), realiza un `make docker-compose-up` y un `make docker-compose-logs`.

La línea de ejecución es:
```shell
./server_up.sh
```
Y para cerrar el servidor y los 5 clientes se utiliza el comando
```shell
make docker-compose-down
```
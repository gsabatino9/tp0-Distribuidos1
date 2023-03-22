# Ejercicio 3
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
#!/bin/bash

# Creo un Dockerfile temporal para agregarle netcat a alpine
echo "FROM alpine:latest" >> Dockerfile
echo "RUN apk add --no-cache netcat-openbsd" >> Dockerfile

# Construyo la imagen y la llamo 'netcat-container'
echo "Construyendo imagen con netcat."
docker build -t netcat-container . &> /dev/null
rm Dockerfile
echo "Imagen con netcat construida."

echo "Levantando EchoServer."

make docker-compose-up &> /dev/null

echo "EchoServer listo."

docker run --rm --network=tp0_testing_net netcat-container sh -c 'echo PING | nc server 12345' > output.txt

if diff -q output.txt <(echo 'PING') >/dev/null; then
  echo "SUCCESS: EchoServer retorna correctamente."
else
  echo "ERROR: EchoServer no retorna el mismo mensaje."
fi

make docker-compose-down &> /dev/null
echo "EchoServer cerrado."

rm output.txt
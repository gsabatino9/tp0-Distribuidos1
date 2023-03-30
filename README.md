# Ejercicio 1

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

# Ejercicio 2

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

## Línea de ejecución
```shell
python3 create_docker_compose.py num_clients
make docker-compose-up && make docker-compose-logs
```
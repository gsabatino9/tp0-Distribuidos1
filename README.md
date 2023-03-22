# Ejercicio 1.1

El script se realizó en python, llamado `create_docker_compose.py`.

Se ejecuta con la siguiente línea de comando:
```python
python3 create_docker_compose.py num_clientes
```

donde `num_clientes` es la cantidad de clientes que se quiere tener levantados.

**Nota 1**: El script modifica directamente el archivo `docker-compose-dev.yaml` para poder seguir utilizando el makefile.

**Nota 2**: Se utilizó la librería pyyaml para que el código quede más simple. Si existe algún error: `pip install pyyaml`.
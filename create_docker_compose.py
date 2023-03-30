import yaml
import random

def set_num_clients(num_clients):
    num_clients = 1
    with open('docker-compose-dev.yaml', 'r') as file:
        docker_compose = yaml.safe_load(file)

    for service_name in list(docker_compose['services']):
        if 'client' in service_name:
            del docker_compose['services'][service_name]

    for i in range(num_clients):
        client_name = f'client{i+1}'
        docker_compose['services'][client_name] = {
            'container_name': client_name,
            'image': 'client:latest',
            'entrypoint': 'python3 /main.py',
            'environment': [
                f'CLI_ID={i+1}',
                'CLI_LOG_LEVEL=DEBUG',
                'CHUNK_SIZE=1000',
            ],
            'networks': ['testing_net'],
            'depends_on': ['server'],
            'volumes': ['./client/config:/config', './protocol:/protocol', './.data/dataset:/data']
        }

    # Guardar el archivo de Docker Compose actualizado
    with open('docker-compose-dev.yaml', 'w') as file:
        yaml.dump(docker_compose, file)

if __name__ == '__main__':
    set_num_clients(5)
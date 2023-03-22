import yaml
import argparse

def set_num_clients(num_clients):
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
            'entrypoint': '/client',
            'environment': [
                f'CLI_ID={i+1}',
                'CLI_LOG_LEVEL=DEBUG'
            ],
            'networks': ['testing_net'],
            'depends_on': ['server']
        }

    with open('docker-compose-dev.yaml', 'w') as file:
        yaml.dump(docker_compose, file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('num_clients', type=int, help='Cantidad de clientes')
    args = parser.parse_args()

    set_num_clients(args.num_clients)

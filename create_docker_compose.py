#pip install yaml
import yaml
import random

def gen_document():
    a = str(random.choice(list(range(42,89))))
    b = str(random.choice(list(range(389,500))))
    c = str(random.choice(list(range(100,300))))
    return a+b+c

def gen_name():
    names = ["Lucas", "Marta", "Lionel", "Carla", "Gonzalo", "Manolo", "Paula"]
    a = random.choice(names)
    b = random.choice(names)

    return a + ' ' + b

def gen_last_name():
    last_names = ["Garcia", "Martinez", "Perez", "Rodriguez", "Fernandez", "De Paul", "Paredes"]
    return random.choice(last_names)

def gen_birthday():
    return f"{random.randint(1900, 2022)}-{random.randint(10, 12)}-{random.randint(10, 28)}"

def gen_number(numbers):
    return random.choice(numbers)

def set_num_clients(num_clients):
    with open('docker-compose-dev.yaml', 'r') as file:
        docker_compose = yaml.safe_load(file)

    for service_name in list(docker_compose['services']):
        if 'client' in service_name:
            del docker_compose['services'][service_name]

    numbers = list(range(1000, 9999))

    for i in range(num_clients):
        client_name = f'client{i+1}'
        docker_compose['services'][client_name] = {
            'container_name': client_name,
            'image': 'client:latest',
            'entrypoint': 'python3 /main.py',
            'environment': [
                f'CLI_ID={i+1}',
                'CLI_LOG_LEVEL=DEBUG',
                f'NOMBRE={gen_name()}',
                f'APELLIDO={gen_last_name()}',
                f'DOCUMENTO={gen_document()}',
                f'NACIMIENTO={gen_birthday()}',
                f'NUMERO={gen_number(numbers)}',
            ],
            'networks': ['testing_net'],
            'depends_on': ['server'],
            'volumes': ['./client/config:/config', './protocol:/protocol']
        }

    # Guardar el archivo de Docker Compose actualizado
    with open('docker-compose-dev.yaml', 'w') as file:
        yaml.dump(docker_compose, file)

if __name__ == '__main__':
    set_num_clients(5)

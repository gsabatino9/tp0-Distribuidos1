#!/usr/bin/env python3

from configparser import ConfigParser
from common.client import Client
import logging
import os
import yaml
from protocol.protocol import Packet

def initialize_config():
    """ Parse env variables or config file to find program config params

    Function that search and parse program configuration parameters in the
    program environment variables first and the in a config file. 
    If at least one of the config parameters is not found a KeyError exception 
    is thrown. If a parameter could not be parsed, a ValueError is thrown. 
    If parsing succeeded, the function returns a ConfigParser object 
    with config parameters
    """

    with open("config/config.yaml", "r") as config_file:
        config_data = yaml.safe_load(config_file)

    client_id = os.environ.get("CLI_ID")
    config_data["client_id"] = client_id

    name = os.environ.get("NOMBRE")
    config_data["name"] = name
    last_name = os.environ.get("APELLIDO")
    config_data["last_name"] = last_name
    document = os.environ.get("DOCUMENTO")
    config_data["document"] = document
    birthday = os.environ.get("NACIMIENTO")
    config_data["birthday"] = birthday
    number_bet = os.environ.get("NUMERO")
    config_data["number_bet"] = number_bet

    return config_data


def main():
    config_params = initialize_config()
    logging_level = config_params["log"]["level"]
    client_id = config_params["client_id"]
    server_addr = config_params["server"]["address"]
    bet = Packet(client_id, config_params["name"], config_params["last_name"], config_params["document"],
        config_params["birthday"], config_params["number_bet"])

    initialize_log(logging_level)

    # Log config parameters at the beginning of the program to verify the configuration
    # of the component
    logging.debug(f"action: config | result: success | server_addr: {server_addr} | "
                  f"logging_level: {logging_level}")

    # Initialize server and start server loop
    client = Client(client_id, server_addr)
    client.send_bet(bet)

def initialize_log(logging_level):
    """
    Python custom logging initialization

    Current timestamp is added to be able to identify in docker
    compose logs the date when the log has arrived
    """
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging_level,
        datefmt='%Y-%m-%d %H:%M:%S',
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

from configparser import ConfigParser
from common.client import Client
import logging
import os
import yaml

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

	config_data["client_id"] = os.environ.get("CLI_ID")
	config_data["chunk_size"] = os.environ.get("CHUNK_SIZE")

	return config_data


def main():
	config_params = initialize_config()
	logging_level = config_params["log"]["level"]
	client_id = config_params["client_id"]
	server_addr = config_params["server"]["address"]
	chunk_size = int(config_params["chunk_size"])

	initialize_log(logging_level)

	# Log config parameters at the beginning of the program to verify the configuration
	# of the component
	logging.debug(f"action: config | result: success | server_addr: {server_addr} | "
				  f"chunk_size: {chunk_size} | logging_level: {logging_level}")

	# Initialize client and start server loop
	client = Client(client_id, server_addr)
	filepath = f'data/agency-{client_id}.csv'
	client.send_bets_for_chunks(filepath, chunk_size)

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

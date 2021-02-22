import json
import os


def main():
	binary_name = 'K-trading-bot'
	program_id = 'krypto-trading-bot'
	exchange_id = os.environ.get('exchange', 'binance')
	pair_id = os.environ.get('pair', 'btc/usdt')
	shared_folder = os.environ.get('shared_folder', '/root/shared')
	configuration_path = os.environ.get('configuration_path', '/root/configuration/configuration.json')

	with open(configuration_path) as file:
		configuration = json.load(file)

	database_folder = f'{shared_folder}/database/{exchange_id.lower()}'
	os.system(f'mkir -p {database_folder}')

	exchange = configuration['exchanges'][exchange_id]
	if exchange['status'] != 'enabled':
		raise Exception(f'The exchange "{exchange_id}" is not enabled and cannot be configured.')

	pair = exchange['pairs'][pair_id]
	if pair['status'] != 'enabled':
		raise Exception(f'The pair "{pair_id}" from the exchange "{exchange_id}" is not enabled and cannot be configured.')

	formatted_pair_id = pair_id.lower().replace('/', '_')

	parameters = configuration['exchanges']['parameters'][program_id]
	parameters = exchange['parameters'][program_id].update(parameters)
	parameters = pair['parameters'][program_id].update(parameters)

	# Removing the extra argument, since it is not a common parameter
	extra = parameters['extra']
	parameters.pop('extra', None)

	parameters['title'] = parameters.get('title', f'{exchange} - {pair}')
	parameters['port'] = parameters.get('port', 10001)
	parameters['exchange'] = parameters.get('exchange', exchange_id.upper())
	parameters['currency'] = parameters.get('currency', pair_id.upper())
	parameters['database'] = parameters.get('database', f'{database_folder}/{formatted_pair_id}.db')

	if (exchange['api']['authentication']['key']):
		parameters['apikey'] = exchange['api']['authentication']['key']
		parameters['secret'] = exchange['api']['authentication']['secret']
		parameters['passphrase'] = 'NULL'
	elif (exchange['api']['authentication']['passphrase']):
		parameters['apikey'] = 'NULL'
		parameters['secret'] = 'NULL'
		parameters['passphrase'] = exchange['api']['authentication']['passphrase']

	final_parameters = ""
	for key, value in parameters.items():
		final_parameters += f' --{key} {value}'

	final_parameters += ' ' + extra if extra else '--colors --naked'

	command = f'''{binary_name} {final_parameters} "$@"'''

	print(f'parameters:\n{parameters}')
	print(f'command:\n{command}')

	os.system(command)

if __name__ == '__main__':
	main()

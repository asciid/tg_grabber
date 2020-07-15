#!/usr/bin/env python3
from pyrogram import Client, errors
from termcolor import colored
from time import localtime, strftime
import sys
import os
import re

count = False
get_names = False

def get_channels(argv):
	channels = []
	for x in argv:
		if not x.startswith('-'):
			if x.startswith('@'): channels.append(x[1:])
			else: channels.append(x)
	return channels

def process_flags(argv):
	if '--help' in argv or '-h' in argv:
		help_msg = '''USAGE: ./download.py channel(s) [FLAGS]

FLAGS:
--help    | -h -- Print this message and exit.
--count   | -c -- Simply count up all the chat/channel's documents.
--names   | -n -- Iterate through the chat/channel and print file names with no downloads.
--nocolor -- Disable colored output.
--cleanup -- Clear the vault and exit.


GETTING AN API DATA:
1. Go to <my.telegram.org> ang log in;
2. Register new app in "API development tools" section;
3. Copy values from first and second fields;

ISSUES: <github.com/asciid/tg_grabber/issues>'''

		print(help_msg)
		sys.exit()

	elif '--cleanup' in argv:
		r = input('This action wipes all stored data. Are you sure? [y/n]: ')
		if r.lower() == 'y':
			os.system('rm -rf vault/ amount.txt output.txt')
		sys.exit()

	elif '--nocolor' in argv:
		def colored(a, b, **attrs): return a

	elif '--count' in argv or '-c' in argv:
		global count
		count = True

	elif '--names' in argv or '-n' in argv:
		global get_names
		get_names = True

# Error handling

args = sys.argv[1:]
process_flags(args)
channels = get_channels(args)

if len(channels) == 0:
	print('Error: Chat or channel to download is omitting.\nRun ./download.py -h for some info.')
	sys.exit()

# Getting data to start
if os.path.exists('grabber.ini'):
	app = Client(session_name='grabber', config_file='grabber.ini')
else:
	api_id = input('Enter your API ID: ')
	api_hash = input('Enter your API hash: ')

	with open('grabber.ini', 'w') as config:
		ini = """[pyrogram]
api_id = {0}
api_hash = {1}""".format(api_id, api_hash)
		config.writelines(ini)
	print('grabber.ini config file has been created.')

	app = Client(session_name='grabber', api_id=api_id, api_hash=api_hash)

app.start()

for entity in channels:
	try:
		data = app.get_chat(entity)
		if data.type not in ('group', 'channel', 'supergroup'):
			app.stop()
			print('Error: Given link refers to a user or a bot.')
			sys.exit()
	except (errors.exceptions.bad_request_400.UsernameNotOccupied, errors.exceptions.bad_request_400.UsernameInvalid):
		app.stop()
		print('Error: Given chat/channel does not exist.')
		sys.exit()

	downloaded = 0
	amount = 0
	path = os.getcwd() + '/vault/' + entity + '/'

	if not count and not get_names:
		if not os.path.exists('vault'): os.mkdir('vault')
		if not os.path.exists('vault/' + entity): os.mkdir('vault/' + entity)

		files = os.listdir(path)

	if not count:
		if data.description == None:
			print(colored('{} ({})'.format(entity, data.title), 'magenta', attrs=['bold']))
		else:
			print(colored('{} ({}): {}'.format(entity, data.title, data.description), 'magenta', attrs=['bold']))

	prev_date = 0
	curr_date = 0
	copies = 1

	for message in app.iter_history(entity):
		if message.media and message.document:

			curr_date = message.date
			date_string = strftime('%Y-%m-%d (%H:%M)', localtime(curr_date))

			if count:
				amount += 1

			elif get_names:
				file_name = message.document.file_name
				print(file_name)

			else:
				file_name = message.document.file_name
				date = message.date

				lenght = message.document.file_size

				os.chdir(path)

				skip = False

				for file in files:
					if file.startswith(file_name+'(COPY'): skip = True

				if not skip:
					if os.path.exists(file_name):
						if os.path.getsize(file_name) == lenght:
							print(colored("File already exists: {};".format(file_name), 'yellow'))
						elif curr_date != prev_date:
							print(colored("[{}]".format(date_string), 'yellow'), colored('Downloading:', 'green'), file_name + ' -- COPY')
							app.download_media(message, file_name=path+file_name+'(COPY {})'.format(copies))
							copies += 1
							downloaded += 1
					else:
						print(colored("[{}]".format(date_string), 'yellow'), colored('Downloading:', 'green'), file_name)
						app.download_media(message, file_name=path + file_name)
						downloaded += 1
						copies = 1

			prev_date = curr_date

	if count:
		print('Total file amount:', amount)
	elif not get_names:
		if downloaded == 0:
			print('Resource is already stored.')
		else:
			print('Files proceed:', downloaded)

	os.chdir('../../')

app.stop()

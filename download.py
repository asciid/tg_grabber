#!/usr/bin/env python3
from pyrogram import Client, errors
from termcolor import colored
from time import localtime, strftime
from mimetypes import guess_extension
import sys
import os
import re

"""
                [   TODO   ]
[ 1. DIFFERENT DATA TYPES                   ]
[ 2. CODE PRETTIFYING                       ]
[ 3. REGISTERED PROFILES // PROFILE FARMING ]
"""

get_names = False
count     = False

media_types = {
	'animation'   : False,
	'audio'       : False,
	'document'    : False,
	'photo'       : False,
	'sticker'     : False,
	'text'        : False,
	'video'       : False,
	'video_note'  : False,
	'voice'       : False
}

def auth():
	if os.path.exists('grabber.ini'):
		return Client(session_name='grabber', config_file='grabber.ini')
	else:
		api_id   = input('Enter your API ID: ')
		api_hash = input('Enter your API hash: ')

		with open('grabber.ini', 'w') as config:
			# Whether the man can face such an ugly indent?
			ini = """[pyrogram]
	api_id = {0}
	api_hash = {1}""".format(api_id, api_hash)
			config.writelines(ini)

		print('grabber.ini config file has been created.')
		return Client(session_name='grabber', api_id=api_id, api_hash=api_hash)

def get_channels(argv):
	channels = []

	for argument in argv:
		if not argument.startswith('-'):
			if argument.startswith('@'): channels.append(argument[1:])
			else: channels.append(argument)

	if len(channels) == 0:
		sys.exit('Error: Chat or channel to download is omitting.\nRun ./download.py -h for some info.')
	else:
		return channels

def process_flags(argv):

	global media_types
	global count
	global get_names

	if '--help' in argv or '-h' in argv:
		help_msg = '''USAGE: ./download.py channel(s) [FLAGS]

FLAGS:
--help    | -h -- Print this message and exit.
--cleanup | -c -- Clear the vault and exit.
--names   | -n -- Iterate through the chat/channel and print file names with no downloads.
--nocolor -- Disable colored output.
--count   -- Simply count up all the chat/channel's documents.

GETTING AN API DATA:
1. Go to <my.telegram.org> ang log in;
2. Register new app in "API development tools" section;
3. Copy values from first and second fields;

ISSUES: <github.com/asciid/tg_grabber/issues>'''

		sys.exit(help_msg)


	if '--cleanup' in argv:
		confirmation = input('This action wipes all stored data. Are you sure? [y/n]: ')
		if confirmation.lower() == 'y': os.system('rm -rf vault/ amount.txt output.txt')

		sys.exit()


	if '--nocolor' in argv: colored = lambda a, b, **c: a

	if '-c' in argv or '--count'      in argv: media_types['count'      ] = True
	if '-n' in argv or '--names'      in argv: media_types['get_names'  ] = True
	if '-m' in argv or '--animation'  in argv: media_types['animation ' ] = True
	if '-a' in argv or '--audio'      in argv: media_types['audio'      ] = True
	if '-d' in argv or '--documents'  in argv: media_types['document'   ] = True
	if '-p' in argv or '--photo'      in argv: media_types['photo'      ] = True
	if '-s' in argv or '--stickers'   in argv: media_types['sticker'    ] = True
	if '-t' in argv or '--text'       in argv: media_types['text'       ] = True
	if '-v' in argv or '--video'      in argv: media_types['video'      ] = True
	if '-N' in argv or '--videonotes' in argv: media_types['video_note' ] = True
	if '-V' in argv or '--voice'      in argv: media_types['voice'      ] = True
	if '-A' in argv or '--all'        in argv:
		for media_type in media_types: media_type = True

def process_folders (channel_name):
	global media_types

	path = 'vault/' + channel_name

	if not os.path.exists('vault/'): os.mkdir('vault/')
	if not os.path.exists(  path  ): os.mkdir(  path  )

	os.chdir(path)

	for media_type in ('document', 'photo', 'voice', 'audio', 'video', 'text', 'video_note', 'animation', 'sticker'):
		if media_types[media_type] == True and not os.path.exists(media_type):
			os.mkdir(media_type)

	os.chdir('../../')
def get_media       (data_type   ):
	
	global date_string
	global copies
	document = False
	skip     = False

	file_name  = eval('message.{}.file_id'.format(data_type))

	if   data_type == 'photo'   : ext = '.jpg'
	elif data_type == 'document': 
		lenght     = message.document.file_size
		file_name  = message.document.file_name
		ext        = ''
		document   = True

	else: ext = guess_extension(eval('message.{}.mime_type'.format(data_type)))

	full_path = '{}/{}{}'.format(data_type, file_name, ext)

	if document:
		for file in os.listdir('document'):
			if file.startswith(file_name + '(COPY'): skip = True

	if   count     == True: global amount; amount += 1
	elif get_names == True: print(file_name)
	else:
		global downloaded

		if not skip:

			if os.path.exists(full_path):
				if document:
					if lenght == os.path.getsize(full_path): print(colored("File already exists:",'yellow'), file_name)
					else:
						print(colored("[{}]".format(date_string), 'yellow'), colored('Downloading:', 'green'), file_name + ' -- COPY') 
						message.download(file_name=full_path+'(COPY {})'.format(copies))
						copies     += 1
						downloaded += 1
				else:
					print(colored("File already exists:",'yellow'), file_name)

			else:
				print(colored("[{}] [{:10}]".format(date_string, data_type), 'yellow'), colored('Downloading:', 'green'), file_name + ext)
				message.download(file_name=full_path)
				downloaded += 1
def get_text        (message     ):
	# File is open at the root of the chat's media folder
	# Check out the line 

	# Getting type of resource
	global data
	global date_string # To don't fuck with formatting twice
	
	with open('messages.txt', 'w') as file:
		# If message was sent with a document attached
		if message.media and message.caption != None:
			file.write('{0}: {1}\n'.format(date_string, message.caption))
		else:
			file.write('{0}: {1}\n'.format(date_string, message.text))


args     = sys.argv[1:]
process_flags(args)
channels = get_channels(args)

app = auth()
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
	amount     = 0
	path       = os.getcwd() + '/vault/' + entity + '/'

	if not count and not get_names:
		process_folders(entity)

	if not count:
		if data.description == None:
			print(colored('{} ({})'.format(entity, data.title), 'magenta', attrs=['bold']))
		else:
			print(colored('{} ({}): {}'.format(entity, data.title, data.description), 'magenta', attrs=['bold']))

	prev_date = 0
	curr_date = 0
	copies    = 0

	os.chdir(path)

	for message in app.iter_history(entity):
		if message.media:

			curr_date   = message.date
			date_string = strftime('%Y-%m-%d (%H:%M)', localtime(message.date))
		
			if message.animation  and media_types['animation ']: get_media('animation ')
			if message.video_note and media_types['video_note']: get_media('video_note')
			if message.document   and media_types['document'  ]: get_media('document'  )
			if message.sticker    and media_types['sticker'   ]: get_media('sticker'   )			
			if message.photo      and media_types['photo'     ]: get_media('photo'     )
			if message.video      and media_types['video'     ]: get_media('video'     )
			if message.voice      and media_types['voice'     ]: get_media('voice'     )
			if message.audio      and media_types['audio'     ]: get_media('audio'     )

			prev_date = curr_date
		if media_types['text']: get_text(message)


	if count:
		print('Total file amount:', amount)
	elif not get_names:
		if downloaded == 0:
			print('Resource is already stored.')
		else:
			print('Files proceed:', downloaded)

	os.chdir('../../')

app.stop()
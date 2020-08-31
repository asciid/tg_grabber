#!/usr/bin/env python3
from time import localtime, strftime, sleep
from pyrogram.errors import FloodWait
from mimetypes import guess_extension
from progressbar import ProgressBar
from pyrogram import Client, errors
from termcolor import colored
import sys
import re
import os

help_msg = """USAGE: ./download.py channel(s) DATA_TYPES [OPTION(S)]

OPTIONS:
[--help      | -h] => Print this message and exit.
[--count     | -c] => Simply count up all the chat/channel's documents.
[--names     | -n] => Iterate through the chat/channel and print file names with no downloads.
[--resources | -R] => Re-scan all the chats/channels grabber had ever scanned.
[--cleanup       ] => Clear the vault and exit.
[--nocolor       ] => Disable colored output.

CHANNELS:
Resources are specified just by their internal link: @channel
If the resource is private, use: t.me/joinchat/blah_blah_blah

After download resource is stored in .resources file. 

DATA TYPES:
Grabber can download any of following types of data. You can combine them by combining flags.
[--all        | -A] => Download all the types of data
[--animation  | -m] => Animations
[--audio      | -a] => Audio
[--documents  | -d] => Files (in Telegram other types of docs that are not an audio considered as file)
[--photo      | -p] => Images
[--stickers   | -s] => Stickers
[--text       | -t] => Plain text. Includes media captions and simple messages
[--video      | -v] => Videos
[--videonotes | -N] => Video messages
[--voice      | -V] => Voice messages

GETTING AN API DATA:
1. Go to <my.telegram.org> ang log in;
2. Register new app in "API development tools" section;
3. Copy values from first and second fields;

ISSUES: <github.com/asciid/tg_grabber/issues>"""

# Types of media to download. Also pyrogram types
media_types = {
    'animation': False,
    'audio': False,
    'document': False,
    'photo': False,
    'sticker': False,
    'text': False,
    'video': False,
    'video_note': False,
    'voice': False
}

def auth():
    """
    Starting a pyrogram client and making new config if needed.
    """
    if os.path.exists('grabber.ini'):
        return Client(session_name='grabber', config_file='grabber.ini')
    else:
        api_id = input('Enter your API ID: ')
        api_hash = input('Enter your API hash: ')

        with open('grabber.ini', 'w') as config:
            ini = ''
            ini += '[pyrogram]\n'
            ini += 'api_id = {}\n'.format(api_id)
            ini += 'api_hash = {}'.format(api_hash)

            config.writelines(ini)

        print('grabber.ini config file has been created.')
        return Client(session_name='grabber', api_id=api_id, api_hash=api_hash)


def process_flags():
    """Processing command line options

        Available flags:
    --cleanup   -- Clear the vault/
    --nocolor   -- Disable colored output
    --resources -- Update stored chats
    
    -h -- Help message
    -c -- Count up specified entities
    -n -- Print entities's names
    -m -- Download animations
    -a -- Download audios
    -d -- Download documents
    -p -- Download photos
    -s -- Download stickers
    -t -- Get text messages
    -v -- Download videos
    -N -- Download video notes (as known as video messages)
    -V -- Download voice messages
    -A -- Download all types of data mentioned above"""

    global media_types
    global count
    global get_names
    global help_msg
    global colored
    global read_file
    argv = sys.argv[1:]

    def check_choice(media_types):
        """Processing flags: error handling"""
        choice = False
        for media_type in media_types:
            if media_types[media_type]:
                choice = True
        if not choice:
            sys.exit('Error: Types of media to download are omitting.')


    if '--cleanup' in argv:
        confirmation = input('This action wipes all stored data. Are you sure? [y/n]: ')

        if confirmation.lower() == 'y':
            os.system('rm -rf vault/ amount.txt output.txt')
            msg = 'Done!'
        else:
            msg = 'Shutdown'

        sys.exit(msg)
    if '--nocolor' in argv:
        # Function is just overridden to disable the color
        def colored(a, b, **c): return a
    if '-R' in argv or '--resources' in argv:
        read_file = True
    if '-h' in argv or '--help' in argv:
        sys.exit(help_msg)
    if '-c' in argv or '--count' in argv:
        count = True
    if '-n' in argv or '--names' in argv:
        get_names = True
    if '-m' in argv or '--animation' in argv:
        media_types['animation'] = True
    if '-a' in argv or '--audio' in argv:
        media_types['audio'] = True
    if '-d' in argv or '--documents' in argv:
        media_types['document'] = True
    if '-p' in argv or '--photo' in argv:
        media_types['photo'] = True
    if '-s' in argv or '--stickers' in argv:
        media_types['sticker'] = True
    if '-t' in argv or '--text' in argv:
        media_types['text'] = True
    if '-v' in argv or '--video' in argv:
        media_types['video'] = True
    if '-N' in argv or '--videonotes' in argv:
        media_types['video_note'] = True
    if '-V' in argv or '--voice' in argv:
        media_types['voice'] = True
    if '-A' in argv or '--all' in argv:
        for media_type in media_types:
            media_types[media_type] = True

    check_choice(media_types)


def get_channels():
    """Getting resources to scan from file or from the command line"""
    global read_file
    channels = []
    argv = sys.argv[1:]

    if not read_file:
        # Reading command line arguments
        for argument in argv:
            if not argument.startswith('-'):
                if argument.startswith('@'):
                    channels.append(argument[1:])
                else:
                    channels.append(argument)
    else:
        # Reading from the file
        if os.path.exists('.resources'):
            with open('.resources', 'r') as file:
                content = file.readlines()
                for entity in content:
                    channels.append(entity[:-1])  # Ignore '\n' char
        else:
            sys.exit('.resources file is missing! You might be running the script first time.')
        #print(channels)

    if not channels:
        sys.exit('Error: Chat or channel to download is omitting.\nRun ./download.py -h for some info.')
    else:
        return channels


def process_folders(channel_name):
    """Creating folders for each specified media type if needed"""
    global media_types

    path = 'vault/' + channel_name

    if not os.path.exists('vault/'):
        os.mkdir('vault/')
    if not os.path.exists(path):
        os.mkdir(path)

    os.chdir(path)

    for media_type in ('document', 'photo', 'voice', 'audio', 'video', 'video_note', 'animation', 'sticker'):
        if media_types[media_type] and not os.path.exists(media_type):
            os.mkdir(media_type)

    os.chdir('../../')


def get_media(message, data_type):
    global date_string
    global copies
    global count

    def progress(current, total):
        bar = ProgressBar().start()
        bar.update(current * 100 / total)
        if current == total:
            bar.finish()
            # Check out spaces bellow
            # I need to explain it somehow
            print("\033[A                                                                                       \033[A")

    def check_additional_mimes(mimetype):

        if mimetype == 'audio/mp3':
            return '.mp3'
        if mimetype == 'audio/aac':
            return '.aa'
        elif mimetype == 'image/webp':
            return '.webp'
        elif mimetype == 'application/x-tgsticker':
            return '.tgs'
        elif mimetype == 'audio/x-vorbis+ogg':
            return '.ogg'
        elif mimetype == 'audio/x-wav':
            return '.wav'

    document = False
    skip = False
    length = 0

    file_name = eval('message.{}.file_id'.format(data_type))

    if data_type == 'photo':
        ext = '.jpg'
    elif data_type == 'document':
        length = message.document.file_size
        file_name = message.document.file_name
        ext = ''
        document = True
    else:
        # Special cases
        mime = eval('message.{}.mime_type'.format(data_type))

        if guess_extension(mime) is None:
            ext = check_additional_mimes(mime)
        else:
            ext = guess_extension(mime)

    full_path = '{}/{}{}'.format(data_type, file_name, ext)

    if document and not count:
        for file in os.listdir('document'):
            if file.startswith(file_name + '(COPY'):
                skip = True

    if count:
        global amount
        amount += 1
    elif get_names:
        print(file_name)
    else:
        global downloaded

        if not skip:
            if os.path.exists(full_path):
                if document:
                    if length == os.path.getsize(full_path):
                        print(colored("File already exists:", "yellow"), file_name)
                    else:
                        print(colored("[{}]".format(date_string), "yellow"),
                              colored('Downloading:', 'green'), file_name + ' [COPY]')
                        message.download(file_name=full_path + '(COPY {})'.format(copies), progress=progress)
                        copies += 1
                        downloaded += 1
                else:
                    print(colored("File already exists:", "yellow"), file_name + ext)

            else:
                print(colored("[{}] [{:10}]".format(date_string, data_type), "yellow"),
                      colored("Downloading:", "green"), file_name + ext)
                message.download(file_name=full_path, progress=progress)
                downloaded += 1


def get_text(msg):
    """Message processing
    Works slow as it has to iterate through all the messages in the chat from it's start
    """
    global data
    global date_string  # To avoid formatting twice
    global downloaded
    text = ""
    global last_ID  # We get it in get_latest_id()

    if os.path.exists('messages.txt'):
        mode = 'a'
    else:
        mode = 'w'

    with open('messages.txt', mode) as file:
        # Excluding empty messages whether it is an empty caption or whatever
        if msg.media and msg.caption is not None:
            text = msg.caption
        elif not msg.media:
            text = msg.text

        msg_id = msg.message_id

        if text is None or text == '':
            pass
        elif last_ID >= msg_id:  # Skip if current message is older than written
            pass
        else:
            file.write('[{0}] {1}: {2}\n'.format(msg_id, date_string, text))
            downloaded += 1
            print(colored('[{}] [{:10}]'.format(date_string, 'message'), 'yellow'), text)


def get_latest_id():
    """Getting last message's ID to exclude same messages in messages.txt"""
    with open('messages.txt', 'r') as file:
        content = file.readlines()
        content.reverse()
        var = 0
        for line in content:
            # We reverse the file and grab first line that looks like this:
            # [12345] 1970-01-01 (00:00): Hey ho!
            # And grab the integer from square brackets to use it in get_text()
            message_id = re.match(r'\[\d*\]', line)
            if message_id:
                var = message_id.group(0)
                # And there we avoid brackets themselves
                var = int(var[1:-1])
                break
        return var


def store_link(link):
    """Writing current link to the .resources if needed"""

    if os.path.exists('.resources'):
        mode = 'a'
        # We check whether the line with current link is stored
        with open('.resources', 'r') as file:
            content = file.readlines()
            if link + '\n' in content:
                # And, if positive, skip it
                return
    else:
        mode = 'w'

    with open('.resources', mode) as file:
        file.write(link + '\n')


# Global flags to change script's behaviour
count = False
get_names = False
read_file = False
process_flags()
channels = get_channels()

app = auth()
app.start()

for entity in channels:
    """ Well, it's clear enough
    We got some links from get_channels and for all of them we check the resource type, create folders if needed,
    check types to download and store them.
    """
    try:
        data = app.get_chat(entity)

        if data.type not in ('group', 'channel', 'supergroup'):  # Later archiving conversations might me released
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
        process_folders(entity)

    if not count:
        if data.description is None:
            print(colored('{} ({})'.format(entity, data.title), 'magenta', attrs=['bold']))
        else:
            print(colored('{} ({}): {}'.format(entity, data.title, data.description), 'magenta', attrs=['bold']))

        os.chdir(path)

    prev_date = 0
    curr_date = 0
    copies = 0

    last_ID = 0

    if media_types['text'] and os.path.exists('messages.txt'):
        last_ID = get_latest_id()

    offset_id = 1

    if os.path.exists('.offset_id'):
        with open('.offset_id', 'r') as file:
            content = file.readlines()
            offset_id = int(content[0][:-1])

    try:
        for message in app.iter_history(entity, reverse=True, offset_id=offset_id):

            date_string = strftime('%Y-%m-%d (%H:%M)', localtime(message.date))
            curr_date = message.date

            if message.media:
                if message.animation and media_types['animation']:
                    get_media(message, 'animation')
                if message.video_note and media_types['video_note']:
                    get_media(message, 'video_note')
                if message.document and media_types['document']:
                    get_media(message, 'document')
                if message.sticker and media_types['sticker']:
                    get_media(message, 'sticker')
                if message.photo and media_types['photo']:
                    get_media(message, 'photo')
                if message.video and media_types['video']:
                    get_media(message, 'video')
                if message.voice and media_types['voice']:
                    get_media(message, 'voice')
                if message.audio and media_types['audio']:
                    get_media(message, 'audio')

            if media_types['text']:
                get_text(message)

            prev_date = curr_date

    except FloodWait as e:
        sleep(e.x)
    except:
        with open('.offset_id', 'w') as file:
            file.write('{}\n'.format(message.message_id))

    if count:
        if count != 0:
            print('Total: {} entities'.format(amount))
        elif count == 0:
            print('Channel has no specified entities.')

    elif not get_names:
        if downloaded == 0:
            print('Resource is already stored.')
        else:
            print('Entities proceed:', downloaded)

    os.chdir('../../')

    store_link(entity)

app.stop()

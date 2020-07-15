# tg_grabber
File grabber for Telegram.

## DESCRIPTION:
Script for getting documents from Telegram channels/groups.

## AUTH:
Grabber uses MTProto to act like a userbot so you have to:
1. Go to my.telegram.org and login
2. Create new app in 'API development tools'
3. Get `api_id` and `api_hash` and paste in when script asks for them

## USAGE:
`python3 download.py CHANNEL(s) [FLAGS]`

You can make the script executable by:

`chmod +x download.py`

### Available options:

`--help (-h)` -- help message;

`--cleanup` -- clear the `vault/` where the data is stored;

`--names (-n)` -- get only docs's names;

`--nocolor` -- disable colored output (useful in Windows);

`--count (-c)` -- count up channel's/chat's documents;

## DEPENDENCIES:

* `pyrogram`
* `tgcrypto`
* `termcolor`

## TODO:
0. Add modes to download messages and media
1. Unarchive downloaded archives
2. Code a bot for remote downloads
3. Optimize it somehow
4. Pack some binaries
5. Make some profiles to avoid getting private API data 

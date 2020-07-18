# tg_grabber \[development branch\]
File grabber for Telegram.

## TODO:
0. Debug text processing: checking dowlnoaded data, prettifying the output and excluding that annoying `None` (wrong media type I bet);
1. Unarchive downloaded archives: I shall use UNIX tools (fuck porting, huh?);
2. Code a bot for remote downloads: In progress, but tool first;
3. Optimize it somehow
4. Pack some binaries
5. Make some profiles to avoid getting private API data 

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

### Available data types:
`--animation (-m)` -- Animation;

`--audio (-a)` -- Audio tracks;

`--documents (-d)` -- Documents (other files);

`--photo (-p)` -- Images;

`--stickers (-s)` -- Stickers;

`--text (-t)` -- Plain text (whether a caption or a simple message);

`--video (-v)` -- Videos;

`--videonotes (-N)` -- Video messages;

`--voice (-V)` -- Voice messages;

`--all (-A)` -- Everything from specified above;

## DEPENDENCIES:

* `pyrogram`
* `tgcrypto`
* `termcolor`

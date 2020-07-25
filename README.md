# tg_grabber \[development branch\]
Data grabber for Telegram.

## DESCRIPTION:
Script for getting data from Telegram channels or groups.

## AUTH:
Grabber uses MTProto to act like a regular third-party Telegram app so you have to register it as an application:
1. Go to my.telegram.org and login 
2. Create new app in 'API development tools'
3. Get `api_id` and `api_hash` and paste in when script asks for them

Thinking about a method to use one of pre-built API configs. In progress and TODO actually.

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

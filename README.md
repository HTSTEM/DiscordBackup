# DiscordBackup
A simple Python script for backing up discord servers.

Usage for now:

`python3 backup.py <guild_id> <output_file_name>`

You will need a file named token.txt which contains a bot or user token.
You may need to manually change `bot=False` to `bot=True` on line 64.

## Dependencies
You'll need `discord.py` and `sqlite3` to run the script. To install these, run these commands:
```
$ sudo -H python3 -m pip install -U discord.py
$ sudo apt-get install sqlite3
```

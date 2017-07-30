import sqlite3
import sys

import discord

client = discord.Client()

database = sqlite3.connect("{}.sqlite".format(sys.argv[2]))

@client.async_event
async def on_ready():
    print("logged in")
    def scrub(s):
        while "--" in s:
            s = s.replace("--", "-")
        return s
    def check_table_exists(tablename):
        dbcur = database.cursor()
        dbcur.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='{0}';
            """.format(tablename.replace('\'', '\'\'')))
        if dbcur.fetchone():
            dbcur.close()
            return True

        dbcur.close()
        return False
    
    guild = client.get_guild(int(sys.argv[1]))
    for channel in guild.channels:
        if isinstance(channel, discord.TextChannel):
            if channel.permissions_for(guild.get_member(client.user.id)).read_message_history:
                sys.stdout.write("Logging {0}: Counting".format(channel.name))
                sys.stdout.flush()
                
                msg_c = 0
                async for message in channel.history(limit=None):
                    msg_c += 1
            
                print("\rLogging {0}: 0/{1}         ".format(channel.name, msg_c), end="")
                cursor = database.cursor()
                if check_table_exists(scrub(channel.name)):
                    cursor.execute("""DROP TABLE "{0}\"""".format(scrub(channel.name)))
                cursor.execute("""CREATE TABLE "{0}"(uid INTEGER, mid INTEGER, message TEXT, files TEXT, timestamp TEXT)""".format(scrub(channel.name)))
                database.commit()
                count = 0
                async for message in channel.history(limit=None):
                    at = ",".join([i.url for i in message.attachments])
                    cursor.execute("""
                        INSERT INTO "{0}"(uid, mid, message, files, timestamp)
                        VALUES (?, ?, ?, ?, ?)""".format(scrub(channel.name)), (message.author.id, message.id, message.content, at, message.created_at))
                    count += 1
                    if count % 200 == 0:
                        database.commit()
                        print("\rLogging {0}: {1}/{2}".format(channel.name, count, msg_c), end="")
                database.commit()
                print("\rLogging {0}: [DONE]            ".format(channel.name))
    print("LOGS FINISHED!")
    await client.logout()


client.run(open('token.txt','r').read().split('\n')[0])

import unicodedata
import sqlite3
import sys
import re

import discord


class Archiver(discord.Client):
    def __init__(self, guild_id, filename='', token=''):
        discord.Client.__init__(self)
        self.guild_id = guild_id
        self.filename = filename
        self.ready = False

        def scrub(s):
            while '--' in s:
                s = s.replace('--', '-')
            return s
        def check_table_exists(tablename):
            dbcur = self.database.cursor()
            dbcur.execute('''
                SELECT name FROM sqlite_master WHERE type='table' AND name='{0}';
                '''.format(tablename.replace('\'', '\'\'')))
            if dbcur.fetchone():
                dbcur.close()
                return True

            dbcur.close()
            return False

        @self.event
        async def on_message(message):
            if self.ready and message.guild.id == self.guild_id:
                cursor = self.database.cursor()

                if not check_table_exists(scrub(message.channel.name)):
                    cursor.execute('''CREATE TABLE '{0}'(uid INTEGER, mid INTEGER, message TEXT, files TEXT, timestamp TEXT)'''.format(scrub(message.channel.name)))
                    self.database.commit()

                at = ','.join([i.url for i in message.attachments])
                cursor.execute('''
                    INSERT INTO '{0}'(uid, mid, message, files, timestamp)
                    VALUES (?, ?, ?, ?, ?)'''.format(scrub(message.channel.name)), (message.author.id, message.id, message.content, at, message.created_at))

                self.database.commit()

                print(f'{message.channel.name}, {message.author}, {message.content}')

        @self.event
        async def on_ready():
            guild = self.get_guild(self.guild_id)
            if guild is None:
                print('No guild found with ID {}.'.format(self.guild_id))
                self.logout()
                self.close()
                quit()

            if self.filename:
                if not self.filename.endswith('.sqlite'):
                    self.filename += '.sqlite'
            else:
                self.filename = unicodedata.normalize('NFKD', guild.name).encode('ascii', 'ignore').decode('ascii')
                self.filename = re.sub('[^\W\S-]', '', self.filename).strip()
                self.filename = re.sub('[-\s]+', '-', self.filename)
                self.filename += '.sqlite'
                print('No filename provided. Using {}'.format(self.filename))
            self.database = sqlite3.connect(self.filename)

            self.ready = True
            print('Archive Bot Ready!')

        self.run(token, bot=False)


def main():
    filename = ''
    if len(sys.argv) >= 2:
        try:
            g_id = int(sys.argv[1])
        except ValueError:
            print('Usage: python live.py <guild id> [output filename]')
            return
    elif len(sys.argv) < 2:
        print('Usage: python live.py <guild id> [output filename]')
        return

    if len(sys.argv) == 3:
        filename = sys.argv[2]
    if len(sys.argv) > 3:
        print('Usage: python live.py <guild id> [output filename]')
        return

    token = open('token.txt').read().split('\n')[0]
    A = Archiver(g_id, filename, token)


if __name__ == '__main__':
    main()

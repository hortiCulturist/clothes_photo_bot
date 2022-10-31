import asyncio
import random
import re
import sys
import datetime

from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message

import config
import db

db.start_db()
bot = Client("my_account",
             api_id=config.api_id,
             api_hash=config.api_hash)
print("Bot started")


@bot.on_message(filters.regex('^add new pattern'))  # add new pattern *name* *username* *hashtag*
async def new_pattern(_, message: Message):
    text = message.text
    text = text.split()
    db.add_pattern(text)
    await bot.send_message(message.from_user.id, 'Паттерн добавлен')


@bot.on_message(filters.regex('^add channel'))  # add channel *username*
async def new_pattern(_, message: Message):
    text = message.text
    text = text.split('@')
    db.add_my_channel(text[1])
    await bot.send_message(message.from_user.id, 'Канал добавлен')


@bot.on_message(filters.regex('^delete pattern'))  # delete pattern *name*
async def chat_list_downloader(_, message: Message):
    text = message.text
    text = text.split()
    db.delete_pattern(text[2])
    await bot.send_message(message.from_user.id, 'Паттерн удалён')


@bot.on_message(filters.regex('^delete channel'))  # delete channel *username*
async def chat_list_downloader(_, message: Message):
    text = message.text
    text = text.split('@')
    db.delete_channel(text[1])
    await bot.send_message(message.from_user.id, 'Канал удалён')


@bot.on_message(filters.regex('^view all pattern'))
async def chat_list_downloader(_, message: Message):
    for i in db.view_all_pattern():
        await bot.send_message(message.from_user.id, f'Артикул: {i[0]}\n'
                                                     f'Имя: {i[1]}\n'
                                                     f'Канал донор: {i[2]}\n'
                                                     f'Хештег: {i[3]}')


@bot.on_message(filters.regex('^time'))  # time *2000.12.31*
async def time(_, message: Message):
    text = message.text.split(' ')
    time_stamp = datetime.datetime.strptime(text[1], '%Y.%m.%d')
    t = time_stamp.timestamp()
    db.time_set(t)
    await bot.send_message(message.from_user.id, 'Время установлено')


@bot.on_message(filters.regex('^help$'))
async def chat_list_downloader(_, message: Message):
    await bot.send_message(message.from_user.id, f'**Добавить паттерн:**\n'
                                                 f'add new pattern (name) '
                                                 f'(username) '
                                                 f'(hashtag)\n\n'

                                                 f'**Добавить мой канал:**\n'
                                                 f'add channel (username)\n\n'
                                                 
                                                 f'**Заполнить канал постами с (команда указать дату ниже)**\n'
                                                 f'/grab\n\n'

                                                 f'**Удалить паттерн:**\n'
                                                 f'delete pattern (name)\n\n'

                                                 f'**Удалить мой канал:**\n'
                                                 f'delete channel (channel_id)\n\n'
                                                 
                                                 f'**Указать дату**\n'
                                                 f'time 2000.12.31\n\n'

                                                 f'**Посмотреть все паттерны:**\n'
                                                 f'view all pattern\n\n'

                                                 f'<**Важно соблюдать регистр команд и пробелы**>\n')

#  *********************************************************************************************************************


@bot.on_message(filters=(filters.regex(re.compile(r'/grab'))))
async def get_grab_task(_, message: Message):
    print('Начал работу')
    data_list = db.get_channels_data()
    for id, name, username, hashtag in data_list:
        media_groups_used = []
        usrn = username.split('@')[1]
        for messages_numbers in range(0, 999999999, 10):
            async for messages in bot.search_messages(usrn, limit=10, offset=messages_numbers):
                if messages.service is not None:
                    continue
                if messages.media_group_id is None:
                    continue
                if messages.date > config.date:
                    print(messages.date)
                    # TODO проверить есть ли в базе
                    message_in_base = db.old_message_check(messages.chat.id, messages.media_group_id)
                    if message_in_base:
                        continue
                    if messages.media_group_id not in media_groups_used:
                        media_groups_used.append(messages.media_group_id)
                        try:
                            await bot.copy_media_group(db.get_my_channel()[0][0],
                                                           messages.chat.id, messages.id, captions=f'{hashtag}\n'
                                                                                                f'Артикул: {id}')
                            db.add_old_post(messages.chat.id, messages.media_group_id)
                            #TODO добавить сообщение в базу
                            await asyncio.sleep(random.randint(1, 2))
                        except FloodWait:
                            sys.exit(1)

                    await asyncio.sleep(random.randint(1, 2))


@bot.on_message(filters.media_group & filters.channel)
async def get_media_group(_, message: Message):
    data_list = db.get_channels_data()
    for id, name, username, hashtag in data_list:
        usrn = username.split('@')
        if usrn[1] == message.chat.username:
            await bot.copy_media_group(db.get_my_channel()[0][0],
                                       message.chat.id, message.id, captions=f'{hashtag}\n'
                                                                             f'Артикул: {id}')


@bot.on_message(filters.photo & filters.channel)
async def get_one_photo(_, message: Message):
    data_list = db.get_channels_data()
    for id, name, username, hashtag in data_list:
        usrn = username.split('@')
        if usrn[1] == message.chat.username:
            await bot.send_photo(db.get_my_channel()[0][0],
                                 photo=message.photo.file_id,
                                 caption=f'{hashtag}\n'
                                         f'Артикул: {id}')


if __name__ == '__main__':
    bot.run()

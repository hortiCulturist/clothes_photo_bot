import sqlite3 as sqlt
import datetime
db_name = 'clothes_chennel.db'


def start_db():
    base = sqlt.connect(db_name)
    base.execute('CREATE TABLE IF NOT EXISTS "Channels" ("id"	INTEGER NOT NULL UNIQUE,'
                 '"name"            BLOB,'
                 '"username"        BLOB,'
                 '"hashtag"            BLOB,'
                 'PRIMARY KEY("id" AUTOINCREMENT))')
    base.execute('CREATE TABLE IF NOT EXISTS "my_channel" ("username"	BLOB)')
    base.execute('CREATE TABLE IF NOT EXISTS "messages_old" ("chat_id"	INTEGER, "message_id"	INTEGER )')
    base.execute('CREATE TABLE IF NOT EXISTS "times" ("time"	int)')
    base.commit()


def old_message_check(chat_id, message_id):
    base = sqlt.connect(db_name)
    cur = base.cursor()
    cur.execute('SELECT * from messages_old where chat_id = ? and message_id = ?', (chat_id, message_id,))
    result = cur.fetchone()
    base.close()
    return result


def add_old_post(chat_id, message_id):
    base = sqlt.connect(db_name)
    cur = base.cursor()
    cur.execute('INSERT INTO messages_old VALUES (?, ?)', (chat_id, message_id,))
    base.commit()
    base.close()


def time_set(t):
    base = sqlt.connect(db_name)
    cur = base.cursor()
    cur.execute('DELETE FROM times')
    cur.execute('INSERT INTO times VALUES (?)', (t,))
    base.commit()
    base.close()


def select_time():
    base = sqlt.connect(db_name)
    cur = base.cursor()
    all = cur.execute('SELECT * from times').fetchall()
    result = datetime.datetime.fromtimestamp(all[0][0])
    base.close()
    return result


def add_pattern(data):
    base = sqlt.connect(db_name)
    cur = base.cursor()
    name = data[3]
    username = data[4]
    hashtag = data[5]
    cur.execute('INSERT INTO Channels VALUES (null, ?, ?, ?)', (name, username, hashtag))
    base.commit()
    base.close()


def delete_pattern(name):
    base = sqlt.connect(db_name)
    cur = base.cursor()
    cur.execute('DELETE FROM Channels WHERE name = ?', (name,))
    base.commit()
    base.close()


def add_my_channel(username):
    base = sqlt.connect(db_name)
    cur = base.cursor()
    cur.execute('DELETE FROM my_channel')
    cur.execute('INSERT INTO my_channel VALUES (?)', (username,))
    base.commit()
    base.close()


def delete_channel(username):
    base = sqlt.connect(db_name)
    cur = base.cursor()
    cur.execute('DELETE FROM my_channel WHERE username = ?', (username,))
    base.commit()
    base.close()


def get_channels_data():
    base = sqlt.connect(db_name)
    cur = base.cursor()
    data_list = cur.execute('SELECT * from Channels').fetchall()
    base.close()
    return data_list


def get_my_channel():
    base = sqlt.connect(db_name)
    cur = base.cursor()
    data_list = cur.execute('SELECT * from my_channel').fetchall()
    base.close()
    return data_list


def view_all_pattern():
    base = sqlt.connect(db_name)
    cur = base.cursor()
    all = cur.execute('SELECT * from Channels').fetchall()
    base.close()
    return all

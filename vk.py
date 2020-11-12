from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api import VkApi
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from random import randint
import sqlite3
import time
import main
import csv
import time
from threading import Thread


def timetable(msg):
    day = what_today()
    lessons = cur.execute(f'''SELECT {main.WEEK[day]}
FROM timetable_lessons''').fetchall()
    time = cur.execute(f'''SELECT {main.WEEK[day]}
FROM timetable_time''').fetchall()
    text = list()
    for i, item in enumerate(lessons):
        print(item[0])
        if item[0] == None:
            text.append('-----')
        else:
            text.append(str(item[0]) + str(time[i][0]))
    vk_send('\n'.join(text))


def what_today():
    today = main.WEEK[time.localtime(time.time()).tm_wday]
    today = main.WEEK.index(today)
    return today


def new_asked(msg):
    lines = msg.split('\n')
    if len(lines) < 3:
        vk_send('''Повторите запрос в формате
!++        
<Урок>
<Домашнее задание>
''')
    else:
        today = what_today()
        days = main.WEEK[today:] + main.WEEK[:today]
        for day in days:
            lessons = cur.execute(f'''SELECT id
        FROM timetable_lessons
        WHERE {day} = "{lines[1]}"''').fetchall()
            if lessons:
                db_id = lessons[0][0]
                print(day, ' '.join(lines[2:]), db_id)
                cur.execute(f'''UPDATE homrwork
        SET {day} = '{' '.join(lines[2:])}'
        WHERE id = {db_id}''')
                print(f'''UPDATE homrwork
        SET {day} = '{' '.join(lines[2:])}'
        WHERE id = {db_id}''')
                con.commit()
                vk_send('Задание добавлено')
                return
        else:
            vk_send('Урок не найден')
            return



def vk_send(text, keyboard=None, sticker_id=None):
    VK.messages.send(message=text, random_id=randint(-2 ** 63, 2 ** 63 - 1),
                     peer_id=peer_id, keyboard=keyboard, sticker_id=sticker_id)

def what_asked():
    lesson = event.message.text[4:]
    today = what_today()
    days = main.WEEK[today:] + main.WEEK[:today]
    for day in days:
        lessons = cur.execute(f'''SELECT id
    FROM timetable_lessons
    WHERE {day} = "{event.message.text[4:]}"''').fetchall()
        if lessons:
            db_id = lessons[0][0]
            print(db_id)
            homework = cur.execute(f'''SELECT {day}
    FROM homrwork
    WHERE id = {db_id}''').fetchone()[0]
            print(homework)
            if homework:
                vk_send(homework)
                break
            else:
                vk_send('Ничего не задано')
            break
    else:
        vk_send('Такого урока не найдено')


con = sqlite3.connect("расписание.db")
cur = con.cursor()
actions = dict()


try:
    with open('authorize.csv', encoding="utf8") as csvfile:
        reader = \
            list(csv.DictReader(csvfile, delimiter=';', quotechar='"'))[0]
        id = reader['club_id']
        token = reader['token']
        try:
            if int(reader['peer_id']) > 2000000000:
                peer_id = int(reader['peer_id'])
            else:
                peer_id = 0
                print('Проведите инициализацию написав "!homework_start" \
в нужной беседе')
        except:
            peer_id = 0
            print('Проблемы с peer_id, он будет сброшен, \
сделайте инициализацию написав "!homework_start" в нужной беседе заново')
except:
    print('Файл для авторизации испорчен, \
проведите авторизацию используя timetable_bot.exe')
    exit()

VK_SESSION = VkApi(token=token)
VK = VK_SESSION.get_api()
longpoll = VkBotLongPoll(VK_SESSION, id)
if peer_id == 0:
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.message.text == '!homework_start':
                peer_id = int(event.message.peer_id)
                main.write(token, id, peer_id)
for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        if int(event.message.peer_id) == peer_id \
                and event.message.text[0] == '!':
            if '!дз' in event.message.text:
                what_asked()
            if '!++ ' in event.message.text:
                new_asked(event.message.text)
            if '!сегодня' in event.message.text:
                timetable(event.message.text)


# hw_bot.WEEK[

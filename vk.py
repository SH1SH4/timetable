from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api import VkApi
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from random import randint
import sqlite3
import time
import main
import csv
import time
from threading import Timer
import time
from threading import Timer


class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


def check_time():
    time.altzone = 10800
    now = time.localtime(time.time())
    sec = now[3] * 60 * 60 + now[4] * 60
    if sec in times:
        today_homework()


def today_homework():
    con2 = sqlite3.connect("расписание.db")
    cur2 = con2.cursor()
    day = what_today()
    lessons = cur2.execute(f'''SELECT {main.WEEK[(day + 1) % 7]}
FROM timetable_lessons''').fetchall()
    homework = cur2.execute(f'''SELECT {main.WEEK[(day + 1) % 7]}
FROM homrwork''').fetchall()
    text = list()
    for i, item in enumerate(lessons):
        print(item[0])
        if item[0] == None:
            continue
        elif str(homework[i][0]) == '':
            text.append(str(item[0]) + '\n' + 'Ничего не задано')
        else:
            text.append(str(item[0]) + '\n' + str(homework[i][0]))
    vk_send('\n ----- \n'.join(text))


def timetable():
    day = what_today()
    lessons = cur.execute(f'''SELECT {main.WEEK[day]}
FROM timetable_lessons''').fetchall()
    time = cur.execute(f'''SELECT {main.WEEK[day]}
FROM timetable_time''').fetchall()
    text = list()
    for i, item in enumerate(lessons):
        print(item[0])
        if item[0] == None:
            continue
        else:
            text.append(str(item[0]) + '    ' + str(time[i][0]))
    if text:
        text = '\n'.join(text)
    else:
        text = 'свободный день'
    vk_send(text)


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
        for i in lines:
            print(i)
        today = what_today()
        days = main.WEEK[today:] + main.WEEK[:today]
        for day in days:
            lessons = cur.execute(f'''SELECT id
        FROM timetable_lessons
        WHERE {day} = "{lines[1][:-1]}"''').fetchall()
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

def what_asked(msg):
    lesson = msg[4:]
    today = what_today()
    days = main.WEEK[today:] + main.WEEK[:today]
    for day in days:
        lessons = cur.execute(f'''SELECT id
    FROM timetable_lessons
    WHERE {day} = "{lesson}"''').fetchall()
        if lessons:
            db_id = lessons[0][0]
            homework = cur.execute(f'''SELECT {day}
    FROM homrwork
    WHERE id = {db_id}''').fetchone()[0]
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

times = list()
with open('time_message.csv', 'r', newline='',
          encoding='utf8') as f:
    f = f.read().split()
    for hour in f:
        hour = list(map(int, hour.split(':')))
        hour = hour[0] * 60 * 60 + hour[1] * 60
        times.append(hour)


VK_SESSION = VkApi(token=token)
VK = VK_SESSION.get_api()
longpoll = VkBotLongPoll(VK_SESSION, id)
if times:
    tm = RepeatTimer(30, check_time)
    tm.start()
for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        if int(event.message.peer_id) == peer_id \
                and event.message.text[0] == '!':
            if event.message.text == '!homework_start':
                peer_id = int(event.message.peer_id)
                main.write(token, id, peer_id)
                print('написал')
            elif '!дз' in event.message.text:
                what_asked(event.message.text)
            elif '!++' in event.message.text:
                new_asked(event.message.text)
            elif '!сегодня' in event.message.text:
                timetable()
            elif '!помощь' in event.message.text:
                vk_send('''Доступные комманды:
!дз <урок>: Присылает дз на ближайший указанный урок

!++ 
<урок>
<Домашнее задание>: Записывает дз на ближайший указанный урок

!сегодня: Присылает расписание на сегодняшний день''')

        elif event.message.text == '!homework_start':
            peer_id = int(event.message.peer_id)
            main.write(token, id, peer_id)
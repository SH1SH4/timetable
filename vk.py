from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api import VkApi
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from random import randint
import sqlite3
import time
import hw_bot
import csv
import time
from threading import Thread

con = sqlite3.connect("расписание.db")
cur = con.cursor()


def vk_send(text, keyboard=None, sticker_id=None):
    VK.messages.send(message=text, random_id=randint(-2 ** 63, 2 ** 63 - 1),
                     peer_id=peer_id, keyboard=keyboard, sticker_id=sticker_id)


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
                hw_bot.write(token, id, peer_id)
for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        if int(event.message.peer_id) == peer_id \
                and event.message.text[0] == '!':
            print(event.message.text)
            if '!дз' in event.message.text:
                lesson = event.message.text[4:]
                today = hw_bot.WEEK[time.gmtime(time.time()).tm_wday]
                today = hw_bot.WEEK.index(today)
                days = hw_bot.WEEK[today:] + hw_bot.WEEK[:today]
                for day in days:
                    lessons = cur.execute(f'''SELECT id
FROM timetable_lessons
WHERE {day} = "{event.message.text[4:]}"''').fetchall()
                    if lessons:
                        print(lessons)
                        db_id = lessons[0][0]
                        break
                else:
                    vk_send('Такого урока не найдено')

# hw_bot.WEEK[

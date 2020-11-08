import sys
import sqlite3
import csv

WEEK = {1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday',
        6: 'Saturday', 7: 'Sunday'}

con = sqlite3.connect("расписание.db")
cur = con.cursor()
cur_row = 4
cur_coloumn = 1
current_lesson = 'Литература'
cur.execute(f'''UPDATE timetable_lessons
SET {WEEK[cur_row]} = '{current_lesson}'
WHERE id = {cur_coloumn + 1}''')
con.commit()
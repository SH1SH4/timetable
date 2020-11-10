import sys
import sqlite3
import csv

from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QDialog

WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday',
        'Sunday']


class MyWidget(QMainWindow):
    def __init__(self):
        self.current_lesson = None
        super().__init__()
        uic.loadUi('qt.ui', self)
        self.con = sqlite3.connect("расписание.db")
        self.cur = self.con.cursor()
        self.add_lesson.clicked.connect(self.add_less)
        self.db_update.clicked.connect(self.update_db)
        self.add_time_message.clicked.connect(self.add_message_time)
        self.lessons_list.itemClicked.connect(self.cur_lesson)
        self.timetable.itemClicked.connect(self.check_homework)
        self.login_button.clicked.connect(self.ok_login_button)
        self.add_dz_button.clicked.connect(self.dz_add_button)
        self.result = self.cur.execute(
            """SELECT lesson FROM lessons""").fetchall()
        self.timetable_ss()
        for i in range(len(self.result)):
            self.lessons_list.addItem(self.result[i][0])

    def add_less(
            self):  # Тут всё работает, из нижней строки добавляет уроки в базу данных
        self.selected_lesson = self.lesson_line.text()
        self.cur.execute(
            f"""INSERT INTO lessons(lesson) VALUES('{self.selected_lesson}')""")
        self.con.commit()
        result = self.cur.execute("""SELECT lesson FROM lessons""").fetchall()
        print(result)
        self.lessons_list.clear()
        for i in range(len(result)):
            self.lessons_list.addItem(result[i][0])

    def check_homework(self):  # доделать, работа с бд и дз
        print(self.timetable.currentRow(), self.timetable.currentColumn())
        self.cc = self.timetable.currentColumn()
        self.cr = self.timetable.currentRow()
        result = self.cur.execute(f'''SELECT {WEEK[self.cc]}
FROM homrwork
WHERE id = {self.cr + 1}''').fetchall()
        result_lesson = self.cur.execute(f'''SELECT {WEEK[self.cc]}
FROM timetable_lessons
WHERE id = {self.cr + 1}''').fetchall()
        self.result_dz = result[0][0]
        result_lesson = result_lesson[0][0]

        self.dz_widget.setItem(0, 0, QTableWidgetItem(result_lesson))
        self.dz_widget.setItem(0, 1, QTableWidgetItem(self.result_dz))

    def update_db(
            self):  # вот это должно добавлять выбранный урок и время в выбранную ячейку в таблице
        self.cur_row = self.timetable.currentRow()
        self.cur_column = self.timetable.currentColumn()
        self.cur.execute(f'''UPDATE timetable_time
SET {WEEK[self.cur_column]} = '{self.add_time.text()}'
WHERE id = {self.cur_row + 1}''')
        print(self.add_time.text())
        self.cur.execute(f'''UPDATE timetable_lessons
        SET {WEEK[self.cur_column]} = '{self.current_lesson}'
        WHERE id = {self.cur_row + 1}''')
        self.con.commit()
        self.timetable_ss()

    def cur_lesson(self,
                   item):  # считывает какой урок сейчас выбран в списке уроков
        self.current_lesson = item.text()

    def timetable_ss(self):
        result = self.cur.execute("SELECT * FROM timetable_lessons").fetchall()
        t_result = self.cur.execute("SELECT * FROM timetable_time").fetchall()
        self.timetable.setRowCount(len(result))
        self.timetable.setColumnCount(len(result[0]) - 1)
        self.titles = [description[0] for description in self.cur.description]
        self.timetable.setHorizontalHeaderLabels(
            self.titles[1:])  # Вот тут надо написать чтобы заголовки из bd считывались в таблицу
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                if j == 0:
                    continue
                self.time = t_result[i][j]
                if self.time != None:
                    self.timetable.setItem(i, j - 1, QTableWidgetItem(
                        str(val) + '  ' + str(self.time)))
                elif val == None:
                    self.timetable.setItem(i, j - 1, QTableWidgetItem(str(val)))
                else:
                    self.time = ''
                    self.timetable.setItem(i, j - 1, QTableWidgetItem(
                        str(val) + '  ' + str(self.time)))

    def ok_login_button(self):  # авторизация
        with open('authorize.csv', encoding="utf8") as csvfile:
            self.reader = \
                list(csv.DictReader(csvfile, delimiter=';', quotechar='"'))[0]
            self.id = self.reader['club_id']
            self.token = self.reader['token']
        print(self.id, self.token)
        self.token = self.EditToken.text()
        self.id = self.EditId.text()
        self.EditToken.setText(self.token)
        self.EditId.setText(self.id)
        if len(self.id) >= 3 and len(self.token) >= 3:  # проверка на символы(beta)
            with open('authorize.csv', 'w', newline='', encoding='utf=8') as f:
                writer = csv.DictWriter(
                    f, fieldnames=['club_id', 'token'],
                    delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
                writer.writeheader()
                data = {'club_id': self.id, 'token': self.token}
                writer.writerow(data)
                self.EditToken.setStyleSheet("background-color: white; color: black")
                self.EditId.setStyleSheet("background-color: white; color: black")
                self.EditId.setText('ok')
                self.EditToken.setText('ok')
        else:
            if len(self.id) < 3 and len(self.token) < 3:
                self.EditId.setText('мало символов, дебил')
                self.EditToken.setText('мало символов, клоун')
                self.EditToken.setStyleSheet("background-color: red; color: blue")
                self.EditId.setStyleSheet("background-color: red; color: blue")
            elif len(self.id) < 3:
                self.EditId.setText('мало символов, дебил')
                self.EditId.setStyleSheet("background-color: red; color: blue")
            else:
                self.EditToken.setText('мало символов, в мут')
                self.EditToken.setStyleSheet("background-color: red; color: blue")

    def add_message_time(self):
        print(1)

    def dz_add_button(self):
        self.cur.execute(f'''UPDATE homrwork
SET {WEEK[self.cc]} = '{self.dz_widget.item(0, 1).text()}
WHERE id = {self.cr + 1}''')
        self.con.commit()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())

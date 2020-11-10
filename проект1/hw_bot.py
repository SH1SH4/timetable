import sys
import sqlite3
import csv

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QDialog

WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday',
        'Sunday']


def write(token, id, peer_id):
    with open('authorize.csv', 'w', newline='') as f:
        writer = csv.DictWriter(
            f, fieldnames=['club_id', 'token', 'peer_id'],
            delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        data = {'club_id': id,
                'token': token,
                'peer_id': peer_id}
        writer.writerow(data)


class Popup(QDialog):  # авторизация всплывающим окном
    def __init__(self, *args, **kwargs):
        super().__init__()
        try:
            with open('authorize.csv', encoding="utf8") as csvfile:
                self.reader = \
                    csv.DictReader(csvfile, delimiter=';', quotechar='"')
                self.reader = list(self.reader)[0]
                self.id = self.reader['club_id']
                self.token = self.reader['token']
                if 'peer_id' in self.reader:
                    self.peer_id = self.reader['peer_id']
                else:
                    self.peer_id = 0
        except:
            self.id = ''
            self.token = ''
            self.peer_id = 0
        print(self.id, self.token)
        uic.loadUi('untitled.ui', self)
        self.setModal(True)
        self.OkButton.clicked.connect(self.button_ok)
        self.CancelButton.clicked.connect(self.button_cancel)
        self.EditToken.setText(self.token)
        self.EditId.setText(self.id)

    def button_ok(self):
        self.token = self.EditToken.text()
        self.id = self.EditId.text()
        write(self.token, self.id, self.peer_id)
        self.close()

    def button_cancel(self):
        self.close()


class MyWidget(QMainWindow):
    def __init__(self):
        self.current_lesson = None
        super().__init__()
        uic.loadUi('qt.ui', self)
        self.con = sqlite3.connect("расписание.db")
        self.cur = self.con.cursor()
        self.add_lesson.clicked.connect(self.add_less)
        self.db_update.clicked.connect(self.update_db)
        self.lessons_list.itemClicked.connect(self.cur_lesson)
        self.timetable.itemClicked.connect(self.check_homework)
        self.login = Popup(self)
        self.authorize.clicked.connect(self.authorizing)
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
        self.lessons_list.clear()
        for i in range(len(result)):
            self.lessons_list.addItem(result[i][0])

    def check_homework(self):
        print(self.timetable.currentRow(), self.timetable.currentColumn())
        self.cc = self.timetable.currentColumn()
        self.cr = self.timetable.currentRow()
        self.cur.execute('''SELECT ?
FROM homework
WHERE id = ?''', (WEEK[self.cc], self.cr - 1))

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
            self.titles[
            1:])  # Вот тут надо написать чтобы заголовки из bd считывались в таблицу
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

    def authorizing(self):  # кнопка авторизации
        self.login.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())

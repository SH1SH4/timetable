import sys
import sqlite3
import csv

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QDialog

WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday',
        'Sunday']


class Popup(QDialog):  # авторизация всплывающим окном
    def __init__(self, *args, **kwargs):
        super().__init__()
        with open('authorize.csv', encoding="utf8") as csvfile:
            self.reader = \
            list(csv.DictReader(csvfile, delimiter=';', quotechar='"'))[0]
            self.id = self.reader['club_id']
            self.token = self.reader['token']
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
        with open('authorize.csv', 'w', newline='') as f:
            writer = csv.DictWriter(
                f, fieldnames=['club_id', 'token'],
                delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()
            data = {'club_id': self.id, 'token': self.token}
            writer.writerow(data)
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
        self.login = Popup(self)
        self.authorize.clicked.connect(self.authorizing)
        self.result = self.cur.execute(
            """SELECT lesson FROM lessons""").fetchall()
        self.update_result()
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

    def update_db(
            self):  # вот это должно добавлять выбранный урок и время в выбранную ячейку в таблице
        self.cur_row = self.timetable.currentRow()
        self.cur_column = self.timetable.currentColumn()
        print(WEEK[self.cur_row], self.current_lesson, self.cur_column + 1)
        self.cur.execute(f'''UPDATE timetable_lessons
SET {WEEK[self.cur_column - 1]} = '{self.current_lesson}'
WHERE id = {self.cur_row + 1}''')
        self.con.commit()
        self.update_result()

    def cur_lesson(self, item):  # считывает какой урок сейчас выбран в списке уроков
        self.current_lesson = item.text()

    def update_result(self):
        cur = self.con.cursor()
        result = cur.execute("SELECT * FROM timetable_lessons").fetchall()
        self.timetable.setRowCount(len(result))
        self.timetable.setColumnCount(len(result[0]))
        self.titles = [description[0] for description in cur.description]
        self.timetable.setHorizontalHeaderLabels(
            self.titles)  # Вот тут надо написать чтобы заголовки из bd считывались в таблицу
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.timetable.setItem(i, j, QTableWidgetItem(str(val)))

    def authorizing(self):  # кнопка авторизации
        self.login.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())

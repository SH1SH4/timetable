import sys
import sqlite3
import csv

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QDialog

WEEK = {0: 'Понедельник', 1: 'Вторник', 2: 'Среда', 3: 'Четверг', 4: 'Пятница',
        5: 'Суббота', 6: 'Воскресенье'}


class Popup(QDialog):  # авторизация всплывающим окном
    def __init__(self, *args, **kwargs):
        super().__init__()
        with open('authorize.csv', encoding="utf8") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
            for i in reader:
                self.id_token = i
            self.id = self.id_token['club_id']
            self.token = self.id_token['token']
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
        print(self.id_group, self.token)
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
        self.lessons_list.itemClicked.connect(self.cur_lesson)
        self.login = Popup(self)
        self.avtorizacia.clicked.connect(self.avtorization)
        result = self.cur.execute("""SELECT Урок FROM lessons""").fetchall()
        self.update_result()
        for i in range(len(result)):
            self.lessons_list.addItem(result[i][0])

    def add_less(
            self):  # Тут всё работает, из нижней строки добавляет уроки в базу данных
        lesson = self.lesson_line.text()
        self.cur.execute(
            f"""INSERT INTO lessons(Урок) VALUES('{lesson}')""")
        self.con.commit()
        result = self.cur.execute("""SELECT Урок FROM lessons""").fetchall()
        self.lessons_list.clear()
        for i in range(len(result)):
            self.lessons_list.addItem(result[i][0])

    def update_db(
            self):  # вот это должно добавлять выбранный урок и время в выбранную ячейку в таблице
        cur_row = self.timetable.currentRow()
        cur_column = self.timetable.currentColumn()
        self.timetable.setItem(cur_row, cur_column, self.current_lesson)

    def cur_lesson(self,
                   item):  # считывает какой урок сейчас выбран в списке уроков
        self.current_lesson = item
        print(item.text())

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
        self.modified = {}

    def avtorization(self):  # кнопка авторизации
        self.login.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())

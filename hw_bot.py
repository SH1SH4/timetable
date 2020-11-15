import sys
import sqlite3
import csv
from main import WEEK
from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QDialog


class NoLessonDelWindow(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('del_lesson.ui', self)
        self.setModal(True)
        self.CancelButton.clicked.connect(self.cancel_button)

    def cancel_button(self):
        self.close()


class NoneLessonDelWindow(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('none_lesson_del.ui', self)
        self.setModal(True)
        self.CancelButton.clicked.connect(self.cancel_button)

    def cancel_button(self):
        self.close()


class NoTokenAndClubIdWindow(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('untitled3.ui', self)
        self.setModal(True)
        self.CancelButton.clicked.connect(self.cancel_button)

    def cancel_button(self):
        self.close()


class NoClubIdWindow(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('untitled2.ui', self)
        self.setModal(True)
        self.CancelButton.clicked.connect(self.cancel_button)

    def cancel_button(self):
        self.close()


class NoTokenWindow(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('untitled.ui', self)
        self.setModal(True)
        self.CancelButton.clicked.connect(self.cancel_button)

    def cancel_button(self):
        self.close()


class TimeInCsv(QDialog):

    def __init__(self):
        super().__init__()
        uic.loadUi('time.ui', self)
        self.setModal(True)
        self.CancelButton.clicked.connect(self.cancel_button)

    def cancel_button(self):
        self.close()


class TimeDelNo(QDialog):

    def __init__(self):
        super().__init__()
        uic.loadUi('time_del.ui', self)
        self.setModal(True)
        self.CancelButton.clicked.connect(self.cancel_button)

    def cancel_button(self):
        self.close()


class MyWidget(QMainWindow):

    def __init__(self):
        self.current_lesson = None
        self.current_time = None
        super().__init__()
        uic.loadUi('qt.ui', self)
        self.con = sqlite3.connect("расписание.db")
        self.cur = self.con.cursor()
        self.add_lesson.clicked.connect(self.add_less)
        self.db_update.clicked.connect(self.update_db)
        self.add_time_message.clicked.connect(self.add_message_time)
        self.lessons_list.itemClicked.connect(self.cur_lesson)
        self.message_list.itemClicked.connect(self.del_time_message)
        self.timetable.itemClicked.connect(self.check_homework)
        self.dz_label.hide()
        self.Homework_quest.hide()
        self.login_button.clicked.connect(self.ok_login_button)
        self.del_time.clicked.connect(self.del_time_in_list)
        self.dz_label.textChanged.connect(self.add_homework)
        self.del_lesson_button.clicked.connect(self.del_lesson)
        # self.Delete_time_button.clicked.connect(self.del_time_message)
        self.none_lesson_delete = NoneLessonDelWindow()
        self.no_del_lesson = NoLessonDelWindow()
        self.del_time_no = TimeDelNo()
        self.no_club_id_token_window = NoTokenAndClubIdWindow()
        self.no_token_widow = NoTokenWindow()
        self.no_club_id_widow = NoClubIdWindow()
        self.time_in_csv = TimeInCsv()
        self.result = self.cur.execute(
            """SELECT lesson FROM lessons""").fetchall()
        self.timetable_ss()
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
        self.EditToken.setText(self.token)
        self.EditId.setText(self.id)
        self.result = self.cur.execute(
            """SELECT lesson FROM lessons""").fetchall()
        self.timetable_ss()
        for i in range(len(self.result)):
            self.lessons_list.addItem(self.result[i][0])
        with open('time_message.csv', 'r', newline='', encoding='utf8') as f:
            f = f.read().split()
            for i in f:
                self.message_list.addItem(i)

    def del_lesson(self):
        if self.current_lesson:
            id_lesson = self.cur.execute('''SELECT id FROM lessons
WHERE lesson = ?''', (self.current_lesson,)).fetchall()[0][0]
            if id_lesson > 16:
                id_lesson = id_lesson[0]
                self.cur.execute('''DELETE FROM lessons
    WHERE id = ?''', (id_lesson[0],)).fetchall()
                self.con.commit()
                self.lessons_list.clear()
                self.result = self.cur.execute(
                    '''SELECT lesson FROM lessons''').fetchall()
                for i in range(len(self.result)):
                    self.lessons_list.addItem(self.result[i][0])
            elif id_lesson <= 16:
                print('Низя')
            else:
                self.none_lesson_delete.show()
        else:
            self.no_del_lesson.show()

    def add_homework(self):
        self.dz_label.show()
        self.Homework_quest.show()
        self.cc = self.timetable.currentColumn()
        self.cr = self.timetable.currentRow()
        self.cur.execute(f'''UPDATE homrwork
SET {WEEK[self.cc]} = '{self.dz_label.toPlainText()}'
WHERE id = {self.cr + 1}''')
        self.con.commit()

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

    def check_homework(self):  # строка с дз
        self.cc = self.timetable.currentColumn()
        self.cr = self.timetable.currentRow()
        self.result = self.cur.execute(f'''SELECT {WEEK[self.cc]}
FROM homrwork
WHERE id = {self.cr + 1}''').fetchall()
        self.result_dz = self.result[0][0]
        self.dz_label.setText(str(self.result_dz))

    def update_db(
            self):  # вот это должно добавлять выбранный урок и время в выбранную ячейку в таблице
        self.cur_row = self.timetable.currentRow()
        self.cur_column = self.timetable.currentColumn()
        if self.current_lesson == 'None':

            self.cur.execute(f'''UPDATE timetable_lessons
SET {WEEK[self.cur_column]} = NULL
WHERE id = {self.cur_row + 1}''')
            self.cur.execute(f'''UPDATE timetable_time
SET {WEEK[self.cur_column]} = NULL
WHERE id = {self.cur_row + 1}''')
        else:
            self.cur.execute(f'''UPDATE timetable_time
                SET {WEEK[self.cur_column]} = '{self.add_time.text()}'
                WHERE id = {self.cur_row + 1}''')
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
                    self.timetable.setItem(i, j - 1, QTableWidgetItem(''))

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
        self.token = self.EditToken.text()
        self.id = self.EditId.text()
        self.EditToken.setText(self.token)
        self.EditId.setText(self.id)
        if len(self.id) == 9 and len(
                self.token) == 85:  # проверка на символы(beta)
            with open('authorize.csv', 'w', newline='', encoding='utf=8') as f:
                writer = csv.DictWriter(
                    f, fieldnames=['club_id', 'token'],
                    delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
                writer.writeheader()
                data = {'club_id': self.id, 'token': self.token}
                writer.writerow(data)
                self.EditToken.setStyleSheet(
                    "background-color: white; color: black")
                self.EditId.setStyleSheet(
                    "background-color: white; color: black")
                self.EditId.setText('ok')
                self.EditToken.setText('ok')
        else:
            if len(self.id) != 9 or len(self.token) != 85:
                if len(self.id) != 9 and len(self.token) != 85:
                    self.no_club_id_token_window.show()
                    self.EditId.setText('Некорректный ID')
                    self.EditId.setStyleSheet("color: red")
                    self.EditToken.setText('Некорректный Token')
                    self.EditToken.setStyleSheet("color: red")
                else:
                    if len(self.id) != 9:
                        self.no_club_id_widow.show()
                        self.EditId.setText('Некорректный ID')
                        self.EditId.setStyleSheet("color: red")
                    if len(self.token) != 85:
                        self.no_token_widow.show()
                        self.EditToken.setText('Некорректный Token')
                        self.EditToken.setStyleSheet("color: red")

    def add_message_time(self):
        with open('time_message.csv', 'r', newline='', encoding='utf8') as f:

            f = f.read().split()

            if self.time_message.text() in f:
                time_in_csv = True

            else:
                time_in_csv = False

        with open('time_message.csv', 'a', newline='',
                  encoding='utf8') as f_new:

            if time_in_csv == False:
                message_time = self.time_message.text()
                f_new.writelines('\n' + message_time)
                self.message_list.addItem(message_time)

            else:
                self.time_in_csv.show()

    def del_time_message(self, item):
        self.current_time = item.text()

    def del_time_in_list(self):
        if self.current_time != None:
            with open('time_message.csv', 'r', newline='',
                      encoding='utf8') as f:
                f = f.read().split()

                if self.current_time in f:
                    time = f.index(self.current_time)
                    del f[time]
                self.message_list.clear()
            with open('time_message.csv', 'a', newline='',
                      encoding='utf8') as new_f:
                for i in f:
                    new_f.writelines('\n' + i)
                for i in f:
                    self.message_list.addItem(i)
        else:
            self.del_time_no.show()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())

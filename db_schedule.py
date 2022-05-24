import sqlite3


class ScheduleDB:
    def __init__(self, db_file):
        """Инициализация соединения с БД"""
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def schedule_exists(self, group):
        """Проверяем, есть ли расписание группы в БД """
        result = self.cursor.execute('SELECT * FROM `schedule` WHERE `group` = ?', (group,))
        return bool(len(result.fetchall()))

    def add_schedule(self, info):
        """Добавляем расписание 2 недель в БД"""
        try:
            self.cursor.execute(
                'INSERT INTO `schedule` (`group`, `mon_even`, `tues_even`, `wed_even`, '
                '`thurs_even`, `fr_even`, `sat_even`, `mon_odd`, `tues_odd`, `wed_odd`, `thurs_odd`, `fr_odd`, '
                '`sat_odd`) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', info)
            return self.conn.commit()
        except Exception:
            print('Расписание этой группы уже есть в БД')

    def get_schedule_even(self, group, num_of_day):
        """Получение расписания пользователя по его группе"""
        try:
            result = self.cursor.execute('SELECT `mon_even`, `tues_even`, `wed_even`, '
                                         '`thurs_even`, `fr_even`, `sat_even` FROM `schedule` WHERE `group` = ?',
                                         (group,))
            return result.fetchone()[num_of_day]
        except Exception:
            print('Ошибка считывания расписания четной недели с БД')
            return 'Не удалось загрузить расписание'

    def get_schedule_odd(self, group, num_of_day):
        """Получение расписания пользователя по его группе"""
        try:
            result = self.cursor.execute('SELECT `mon_odd`, `tues_odd`, `wed_odd`, '
                                         '`thurs_odd`, `fr_odd`, `sat_odd` FROM `schedule` WHERE `group` = ?', (group,))

            return result.fetchone()[num_of_day]
        except Exception:
            print('Ошибка считывания расписания нечетной недели с БД')
            return 'Не удалось загрузить расписание'

    def delete_all(self):
        try:
            self.cursor.execute('DELETE FROM `schedule`;',)
            return self.conn.commit()
        except Exception:
            print('Не удалось очистить БД')

    def close(self):
        """Закрытие соединения с БД"""
        self.conn.close()

import sqlite3


class BotDB:
    def __init__(self, db_file):
        """Инициализация соединения с БД"""
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def user_exists(self, tg_id):
        """Проверяем, есть ли юзуер в БД """
        result = self.cursor.execute('SELECT `id` FROM `users` WHERE `tg_id` = ?', (tg_id,))
        return bool(len(result.fetchall()))

    def add_user(self, tg_id):
        """Добавляем юзера в БД"""
        self.cursor.execute('INSERT INTO `users` (`tg_id`) VALUES (?)', (tg_id,))
        return self.conn.commit()

    def add_user_group(self, tg_id, group):
        """Добавляем группу пользователю"""
        self.cursor.execute('UPDATE `users` SET `group` = ? WHERE `tg_id` = ?', (group, tg_id))
        return self.conn.commit()

    def get_user_group(self, tg_id):
        """Получение группы пользователя по его tg id"""
        result = self.cursor.execute('SELECT `group` FROM `users` WHERE tg_id = ?', (tg_id,))
        return result.fetchone()[0]

    def close(self):
        """Закрытие соединения с БД"""
        self.conn.close()

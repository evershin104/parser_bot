import sqlite3


class SQL_db:

    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def prepare_statuses(self):
        with self.connection:
            return self.cursor.execute("UPDATE `subscriptions` SET `status` = ?", (0,))

    def get_subscriptions(self):
        """Получаем всех подписчиков бота"""
        with self.connection:
            return self.cursor.execute("SELECT * FROM `subscriptions`").fetchall()

    def get_active_subs(self):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `subscriptions` WHERE `status` = TRUE").fetchall()

    def subscriber_exists(self, tg_id):
        """Проверяем, есть ли уже юзер в базе"""
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `subscriptions` WHERE `tg_id` = ?', (tg_id,)).fetchall()
            return bool(len(result))

    def add_subscriber(self, tg_id, status, time):
        """Добавляем нового подписчика"""
        with self.connection:
            return self.cursor.execute("INSERT INTO `subscriptions` (`tg_id`, `status`, 'end_date') VALUES(?,?,?)",
                                       (tg_id, status, time))

    def delete_subscriber(self, tg_id):
        # Удаляем пользователя
        with self.connection:
            return self.cursor.execute("DELETE FROM 'subscriptions' WHERE `tg_id` = ?", (tg_id,)).fetchall()

    def change_status(self, tg_id, status):
        # Реверс статуса пользователя *start - stop*
        with self.connection:
            return self.cursor.execute("UPDATE `subscriptions` SET `status` = ? WHERE `tg_id` = ?", (status, tg_id))

    def find_user(self, tg_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `subscriptions` WHERE `tg_id` = ?", (tg_id,)).fetchall()

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()

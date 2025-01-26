import sqlite3


class User:

    def __init__(self, database_file):
        self.connection = sqlite3.connect(database_file, check_same_thread= False)
        self.cursor = self.connection.cursor()
        
    def get_gender(self, user_id):
        with self.connection:
            gender = self.cursor.execute("SELECT `gender` FROM `users` WHERE `chat_id` = ?", (user_id,)).fetchall()
            for row in gender:
                gender = str(row[0])
                return gender
            
            
    def get_room(self, user_id):
        with self.connection:
            room = self.cursor.execute("SELECT `room` FROM `users` WHERE `chat_id` = ?", (user_id,)).fetchall()
            for row in room:
                room = str(row[0])
                return room
            
            
    def get_age(self, user_id):
        with self.connection:
            age = self.cursor.execute("SELECT `age` FROM `users` WHERE `chat_id` = ?", (user_id,)).fetchall()
            for row in age:
                age = str(row[0])
                return age
            
            
    def set_gender(self, user_id, gender):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `gender` = ? WHERE `chat_id` = ?", (gender, user_id,))

    def set_age(self, user_id, age):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `age` = ? WHERE `chat_id` = ?", (age, user_id,))

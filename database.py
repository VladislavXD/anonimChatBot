import sqlite3


class Database:
    def __init__(self, database_file):
        self.connection = sqlite3.connect(database_file, check_same_thread= False)
        self.cursor = self.connection.cursor()
        
        
    # register
    # -------------------------------------
    def add_user(self, chat_id):
        with self.connection:
            self.cursor.execute("INSERT INTO `users` (`chat_id`) VALUES (?)", (chat_id,))

    
    def user_exsist(self, chat_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `users` WHERE `chat_id` = ?", (chat_id,)).fetchall()
            return bool(len(result))
    
    
    def set_gender(self, user_id, gender):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `gender` = ? WHERE `chat_id` = ?", (gender, user_id,))
    
    
    def set_room(self, user_id, room):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `room` = ? WHERE `chat_id` = ?", (room, user_id,))
     
    def set_age(self, user_id, age):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `age` = ? WHERE `chat_id` = ?", (age, user_id,))

    
    def get_signup(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT `signup` FROM `users` WHERE `chat_id` = ?", (user_id,)).fetchall()
            for row in result:
                 signup = str(row[0])
                 return signup
    
    def set_signup(self, user_id, signup):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `signup` = ? WHERE `chat_id` = ?", (signup, user_id,))
    
    
    
    

    
    # chat
    # ----------------------------
            

     
    def add_queue(self, chat_id):
        # проверка повтторяюзегося пользователя в базе
        if self.is_in_queue(chat_id):
            return False  
        
        with self.connection:
            self.cursor.execute("INSERT INTO `queue` (`chatID`) VALUES (?)", (chat_id,))
            return True  

    def is_in_queue(self, chat_id):
        with self.connection:
            result = self.cursor.execute("SELECT EXISTS(SELECT 1 FROM `queue` WHERE `chatID` = ?)", (chat_id,))
            return result.fetchone()[0] == 1

    
    def delete_queue(self, chat_id):
        with self.connection:
            return self.cursor.execute("DELETE FROM `queue` WHERE `chatID` = ?", (chat_id,))
    
    def delete_chat(self, id_chat): 
        with self.connection:
            return self.cursor.execute("DELETE FROM `chats` WHERE `id` = ?", (id_chat,))
            
    
    def get_chat(self):
        with self.connection:
            chat = self.cursor.execute("SELECT * FROM `queue`", ()).fetchmany(1)
            if(bool(len(chat))):
                for row in chat:
                    return row[1]
                
            else: 
                return False
            
            
    
    def create_chat(self, chat_one, chat_two):
        with self.connection: 
            if chat_two != 0:
                # Create chat
                self.cursor.execute("DELETE FROM `queue` WHERE `chatID` = ?", (chat_two,))
                self.cursor.execute("INSERT INTO `chats` (`chat_one`,`chat_two`) VALUES (?,?)", (chat_one, chat_two,))
            else: 
                # to get in line
                return False
            
            
    
    def get_active_chat(self, chat_id):
        with self.connection:
            chat = self.cursor.execute("SELECT * FROM `chats` WHERE `chat_one` = ? ", (chat_id,))
            id_chat = 0
            for row in chat:
                id_chat =  row[0]
                chat_info = [row[0], row[2]]
                
                
            if id_chat == 0:
                chat = self.cursor.execute("SELECT * FROM `chats` WHERE `chat_two` = ? ", (chat_id,))
                for row in chat:
                    id_chat = row[0]
                    chat_info = [row[0], row[1]]
                    
                if id_chat == 0:
                    return False
                
                else:
                    return chat_info
                
            else:
                return  chat_info

import aiosqlite
from async_class import AsyncClass

path_db = 'bot/data/database.db'

#Преобразование результата в словарь
def dict_factory(cursor, row):
    save_dict = {}

    for idx, col in enumerate(cursor.description):
        save_dict[col[0]] = row[idx]

    return save_dict

# Форматирование запроса без аргументов
def query(sql, parameters: dict):
    if "XXX" not in sql: sql += " XXX "
    values = ", ".join([
        f"{item} = ?" for item in parameters
    ])
    sql = sql.replace("XXX", values)

    return sql, list(parameters.values())

# Форматирование запроса с аргументами
def query_args(sql, parameters: dict):
    sql = f"{sql} WHERE "

    sql += " AND ".join([
        f"{item} = ?" for item in parameters
    ])

    return sql, list(parameters.values())

#Проверка и создание бд
class DB(AsyncClass):
    async def __ainit__(self):
        self.con = await aiosqlite.connect(path_db)
        self.con.row_factory = dict_factory
        
    # Получение пользователя из БД
    async def get_user(self, **kwargs):
        queryy = "SELECT * FROM users"
        queryy, params = query_args(queryy, kwargs)
        row = await self.con.execute(queryy, params)
        return await row.fetchone()
    
    # Регистрация пользователя в БД
    async def register_user(self, user_id, user_name, first_name):
        await self.con.execute("INSERT INTO users("
                                "user_id, user_name, first_name)"
                                "VALUES (?,?,?)",
                                [user_id, user_name, first_name])
        await self.con.commit()
    
    # Получение всех пользователей из БД
    async def all_users(self):
        row = await self.con.execute("SELECT * FROM users")
        return await row.fetchall()
    
    # Получение всех тематик каналов
    async def all_themes(self):
        row = await self.con.execute("SELECT * FROM tema")
        return await row.fetchall()
    
    # Получение всех услуг
    async def all_services(self):
        row = await self.con.execute("SELECT * FROM services")
        return await row.fetchall()
    
    # Добавление новой группы
    async def new_theme(self, name):
        await self.con.execute(f"INSERT INTO tema(name) VALUES (?)", (name, ))
        await self.con.commit()
        
    # Получение тематики из БД
    async def get_services(self, **kwargs):
        queryy = "SELECT * FROM services"
        queryy, params = query_args(queryy, kwargs)
        row = await self.con.execute(queryy, params)
        return await row.fetchone()
        
    # Удаление товаров
    async def delete_order(self, **kwargs):
        sql = "DELETE FROM chat"
        sql, parameters = query_args(sql, kwargs)
        await self.con.execute(sql, parameters)
        await self.con.commit()
        
    # Получение тематики из БД
    async def get_theme(self, **kwargs):
        queryy = "SELECT * FROM tema"
        queryy, params = query_args(queryy, kwargs)
        row = await self.con.execute(queryy, params)
        return await row.fetchone()
    
    # Получение заявки из бд с unix
    async def get_orders(self, **kwargs):
        queryy = "SELECT * FROM orders"
        queryy, params = query_args(queryy, kwargs)
        row = await self.con.execute(queryy, params)
        return await row.fetchone()
    
    # Редактирование статуса заказа
    async def edit_order_status(self, unix, **kwargs):
        queryy = f"UPDATE orders SET"
        queryy, params = query(queryy, kwargs)
        params.append(unix)
        await self.con.execute(queryy + "WHERE unix = ?", params)
        await self.con.commit()
        
    # Получение списка чатов из бд с тематикой
    async def list_chat_theme(self, **kwargs):
        queryy = "SELECT * FROM chat"
        queryy, params = query_args(queryy, kwargs)
        row = await self.con.execute(queryy, params)
        return await row.fetchall()
    
    # Редактирование названия тематики
    async def edit_theme_name(self, id, **kwargs):
        queryy = f"UPDATE tema SET"
        queryy, params = query(queryy, kwargs)
        params.append(id)
        await self.con.execute(queryy + "WHERE id = ?", params)
        await self.con.commit()
    
    # Добавление Новой заявки
    async def add_orders(self, date, theme, channel, type, photo_id, video_id, msg, status, unix, user_id):
        await self.con.execute(f"INSERT INTO orders(date, theme, channel, type, photo_id, video_id, msg, status, unix, user_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (date, theme, channel, type, photo_id, video_id, msg, status, unix, user_id))
        await self.con.commit()
        
    # Добавление нового чата
    async def new_chat(self, chat_id, theme_id, chat_type):
        await self.con.execute(f"INSERT INTO chat(chat_id, theme_id, chat_type) VALUES (?, ?, ?)", (chat_id, theme_id, chat_type))
        await self.con.commit()
        
    #Проверка на существование бд и ее создание
    async def create_db(self):
        users_info = await self.con.execute("PRAGMA table_info(users)")
        if len(await users_info.fetchall()) == 4:
            print("database was found (Users | 1/3)")
        else:
            await self.con.execute("CREATE TABLE users ("
                                   "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                                   "user_id INTEGER,"
                                   "user_name TEXT,"
                                   "first_name TEXT)")
            print("database was not found (Users | 1/3), creating...")
            await self.con.commit()
            
        tema_info = await self.con.execute("PRAGMA table_info(tema)")
        if len(await tema_info.fetchall()) == 2:
            print("database was found (Tema | 1/3)")
        else:
            await self.con.execute("CREATE TABLE tema ("
                                   "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                                   "name TEXT)")
            print("database was not found (Tema | 1/3), creating...")
            
        chat_info = await self.con.execute("PRAGMA table_info(chat)")
        if len(await chat_info.fetchall()) == 4:
            print("database was found (Chat | 1/3)")
        else:
            await self.con.execute("CREATE TABLE chat ("
                                   "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                                   "chat_id TEXT,"
                                   "chat_type TEXT,"
                                   "theme_id INTEGER)")
            print("database was not found (Chat | 1/3), creating...")
            
        services_info = await self.con.execute("PRAGMA table_info(services)")
        if len(await services_info.fetchall()) == 2:
            print("database was found (Services | 1/3)")
        else:
            await self.con.execute("CREATE TABLE services ("
                                   "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                                   "name TEXT)")
            await self.con.execute("INSERT INTO services("
                                   "name) "
                                    "VALUES (?)", ['Закреп'])
            await self.con.execute("INSERT INTO services("
                                   "name) "
                                    "VALUES (?)", ['Пересылка в чат/группу'])
            print("database was not found (Services | 1/3), creating...")
        
        order_info = await self.con.execute("PRAGMA table_info(orders)")
        if len(await order_info.fetchall()) == 12:
            print("database was found (Orders | 1/3)")
        else:
            await self.con.execute("CREATE TABLE orders ("
                                   "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                                   "user_id INTEGER,"
                                   "date TEXT,"
                                   "theme TEXT,"
                                   "channel TEXT,"
                                   "type TEXT,"
                                   "photo_id TEXT DEFAULT NULL,"
                                   "video_id TEXT DEFAULT NULL,"
                                   "msg TEXT,"
                                   "unix INTEGER,"
                                   "price INTEGER DEFAULT NULL,"
                                   "status TEXT)")
            print("database was not found (Orders | 1/3), creating...")
        await self.con.commit()
        
# orders/status{
#     accepted - одобрено, но не оплачено
#     waiting - Ожидает решения администрации
#     rejected - Отклоненно
#     paid - Оплачено
# }
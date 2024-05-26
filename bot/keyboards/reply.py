# - *- coding: utf- 8 - *-
from aiogram.types import ReplyKeyboardMarkup

from bot.utils.utils_functions import get_admins

#Главное меню
async def user_menu(user_id):
    main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
    main_menu.row("📰  Заказать рекламу")
    if user_id in get_admins():
        main_menu.row("👨‍💻 Админка")
    return main_menu
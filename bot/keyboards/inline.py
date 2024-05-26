# - *- coding: utf- 8 - *-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.data.loader import bot

from bot.data.config import db

#Главное меню пользователя
async def kb_open_type():
    keyboard = InlineKeyboardMarkup(row_width=2)
    themes = await db.all_themes()
    for theme in themes:
        channel_info = await db.list_chat_theme(theme_id=theme['id'])
        if len(channel_info) != 0:
            keyboard.add(InlineKeyboardButton(theme['name'], callback_data=f"change_theme:{theme['id']}"))
    keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data=f"back_to_m"))
    return keyboard

#Главное меню админа
def kb_adm_menu():
    keyboard = InlineKeyboardMarkup()
    kb = []
    kb.append(InlineKeyboardButton("🎵 Темы каналов", callback_data="adm_theme_channels"))
    kb.append(InlineKeyboardButton("🈂️ Услуги", callback_data="adm_services"))
    kb.append(InlineKeyboardButton("📩 Рассылка", callback_data="newsletter"))
    keyboard.add(kb[0], kb[1])
    keyboard.add(kb[2])
    return keyboard

def kb_tip_newsletter():
   keyboard = InlineKeyboardMarkup()
   kb = []

   kb.append(InlineKeyboardButton("🖊️ Текст", callback_data=f"msg:text"))
   kb.append(InlineKeyboardButton("🖼️ Текст c фото", callback_data=f"msg:photo"))

   keyboard.add(kb[0], kb[1])
   keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data=f"back_main_adm"))

   return keyboard

#Список открытия тематик - Админ
async def adm_list_theme():
    keyboard = InlineKeyboardMarkup(row_width=2)
    kb = []
    themes = await db.all_themes()
    for theme in themes:
        keyboard.add(InlineKeyboardButton(theme['name'], callback_data=f"adm_change_theme:{theme['id']}"))
    kb.append(InlineKeyboardButton("🔙 Назад", callback_data="back_main_adm"))
    kb.append(InlineKeyboardButton("➕ Добавить", callback_data="add_theme"))
    keyboard.add(kb[0], kb[1])
    return keyboard

def adm_back_delete(theme_id):
    keyboard = InlineKeyboardMarkup()
    kb = []
    kb.append(InlineKeyboardButton("🔙 Назад", callback_data=f"adm_change_theme:{theme_id}"))
    keyboard.add(kb[0])
    return keyboard

#Клавиатура для меню тематики
def adm_edit_list_theme(theme_id):
    keyboard = InlineKeyboardMarkup()
    kb = []
    kb.append(InlineKeyboardButton("Изменить название", callback_data=f"edit_name_theme:{theme_id}"))
    kb.append(InlineKeyboardButton("Добавить каналы", callback_data=f"add_channel_theme:{theme_id}"))
    kb.append(InlineKeyboardButton("Удалить каналы", callback_data=f"del_channel_theme:{theme_id}"))
    kb.append(InlineKeyboardButton("🔙 Назад", callback_data="adm_theme_channels"))
    keyboard.add(kb[0])
    keyboard.add(kb[1], kb[2])
    keyboard.add(kb[3])
    return keyboard

#Занова указать айди канала
def adm_reload_channel(theme_id):
    keyboard = InlineKeyboardMarkup()
    kb = []
    kb.append(InlineKeyboardButton("🔃 Попробовать снова", callback_data=f"add_channel_theme:{theme_id}"))
    keyboard.add(kb[0])
    return keyboard

#Возвращение к списку каналов - Админ
def adm_back_list_theme():
    keyboard = InlineKeyboardMarkup()
    kb = []
    kb.append(InlineKeyboardButton("🔙 Назад", callback_data="adm_theme_channels"))
    keyboard.add(kb[0])
    return keyboard

#Возвращение в главное меню
def adm_back_main():
    keyboard = InlineKeyboardMarkup()
    kb = []
    kb.append(InlineKeyboardButton("🔙 Назад", callback_data="back_main_adm"))
    keyboard.add(kb[0])
    return keyboard


async def list_channels(theme_id):
    keyboard = InlineKeyboardMarkup(row_width=2)
    kb = []
    channel_info = await db.list_chat_theme(theme_id=theme_id)
    for channel in channel_info:
        chat = await bot.get_chat(channel['chat_id'])
        kb.append(InlineKeyboardButton(chat['title'], url=chat['invite_link']))
        kb.append(InlineKeyboardButton("🔘 Выбрать", callback_data=f"select_chat:{theme_id}:{channel['chat_id']}"))
    keyboard.add(*kb)
    keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data="change_theme"))
    return keyboard

async def del_list_channels(theme_id):
    keyboard = InlineKeyboardMarkup(row_width=2)
    kb = []
    channel_info = await db.list_chat_theme(theme_id=theme_id)
    for channel in channel_info:
        chat = await bot.get_chat(channel['chat_id'])
        kb.append(InlineKeyboardButton(chat['title'], url=chat['invite_link']))
        kb.append(InlineKeyboardButton("🗑️ Удалить", callback_data=f"del_chat:{theme_id}:{channel['chat_id']}"))
    keyboard.add(*kb)
    keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data="user_list_theme"))
    return keyboard

#Список открытия Услуг - Админ
async def adm_services_list():
    keyboard = InlineKeyboardMarkup(row_width=2)
    kb = []
    services = await db.all_services()
    for service in services:
        keyboard.add(InlineKeyboardButton(service['name'], callback_data=f"adm_change_service:{service['id']}"))
    kb.append(InlineKeyboardButton("🔙 Назад", callback_data="back_main_adm"))
    keyboard.add(kb[0])
    return keyboard

#Список открытия Услуг
async def user_services_list(theme_id, channel_id):
    keyboard = InlineKeyboardMarkup(row_width=2)
    kb = []
    services = await db.all_services()
    for service in services:
        keyboard.add(InlineKeyboardButton(service['name'], callback_data=f"select_services:{theme_id}:{channel_id}:{service['id']}"))
    kb.append(InlineKeyboardButton("🔙 Назад", callback_data="user_list_theme"))
    keyboard.add(kb[0])
    return keyboard

#Список открытия Услуг
def kb_yes_mo(unix):
    keyboard = InlineKeyboardMarkup()
    kb = []
    kb.append(InlineKeyboardButton("✅ Принять", callback_data=f"yes:{unix}"))
    kb.append(InlineKeyboardButton("❌ Отклонить", callback_data=f"no:{unix}"))
    keyboard.add(kb[0], kb[1])
    return keyboard

#Выбор способа оплаты
def kb_sposob_opl(unix, price):
    keyboard = InlineKeyboardMarkup()
    kb = []
    kb.append(InlineKeyboardButton("💳 Карта (РФ, УК, КЗ)", callback_data=f"aaio:{unix}:{price}"))
    kb.append(InlineKeyboardButton("💎 CryptoBot", callback_data=f"Crypto_bot:{unix}:{price}"))
    keyboard.add(kb[0], kb[1])
    return keyboard

def refill_open_inl_aaio(link, unix, pay_id):
   keyboard = InlineKeyboardMarkup()
   kb = []

   kb.append(InlineKeyboardButton("💵 Перейти к оплате", url=link))
   kb.append(InlineKeyboardButton("💎 Проверить оплату", callback_data=f"check_aaio_opl:{pay_id}:{unix}"))

   keyboard.add(kb[0])
   keyboard.add(kb[1])

   return keyboard

def refill_open_inl(link, unix, invoice_id):
   keyboard = InlineKeyboardMarkup()
   kb = []

   kb.append(InlineKeyboardButton("💵 Перейти к оплате", url=link))
   kb.append(InlineKeyboardButton("💎 Проверить оплату", callback_data=f"check_opl:{invoice_id}:{unix}"))

   keyboard.add(kb[0])
   keyboard.add(kb[1])

   return keyboard

def back_tip_news():
   keyboard = InlineKeyboardMarkup()
   kb = []
   kb.append(InlineKeyboardButton("🔙 Назад", callback_data="newsletter"))
   keyboard.add(kb[0])
   return keyboard
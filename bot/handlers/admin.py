from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
import re
from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import markdown

from bot.data.loader import dp, bot
from bot.filters.filters import IsAdmin
from bot.keyboards.inline import kb_adm_menu, adm_list_theme, adm_edit_list_theme, adm_back_list_theme, adm_reload_channel, adm_services_list, kb_sposob_opl, del_list_channels, kb_tip_newsletter, adm_back_main, back_tip_news
from bot.state.admin import NewTheme, EditTheme, AddGroup, GetPrice, Newsletter_photo, Newsletter
from bot.data.config import db
from bot.utils.utils_functions import ded, send_back, send_admins, is_number

#Открытие меню
@dp.message_handler(IsAdmin(), text="👨‍💻 Админка", state="*")
async def func_admin_menu(message: Message, state: FSMContext):
    await state.finish()
    await message.answer("👨‍💻 Добро пожаловать в админ панель", reply_markup=kb_adm_menu())
    
@dp.callback_query_handler(IsAdmin(), text="back_main_adm", state="*")
async def func_admin_menu(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    await call.message.answer("👨‍💻 Добро пожаловать в админ панель", reply_markup=kb_adm_menu())

#Открытие списка тематик каналов
@dp.callback_query_handler(IsAdmin(), text="adm_theme_channels", state="*")
async def func_admin_list_theme(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    await bot.send_message(call.from_user.id, "Доступные тематики: ", reply_markup=await adm_list_theme())

#Добавление тематики
@dp.callback_query_handler(IsAdmin(), text="add_theme", state="*")
async def func_admin_newTheme(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    await call.message.answer("Введите название тематики")
    await NewTheme.name.set()
    
@dp.message_handler(state=NewTheme.name)
async def func_NewTheme_text(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    data = await state.get_data()
    await db.new_theme(name = data['name'])
    await message.answer('Тематика успешно добавлена', reply_markup=await adm_list_theme())
    
#Открытие тематики
@dp.callback_query_handler(text_startswith="adm_change_theme", state="*")
async def func_open_theme_adm(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    theme_id = call.data.split(":")[1]
    channel_info = await db.list_chat_theme(theme_id=theme_id)
    theme_info = await db.get_theme(id=theme_id)
    msg1 = ""
    msg2 = ""
    for i, list in enumerate(channel_info):
        chat = await bot.get_chat(list['chat_id'])
        if chat['type'] == 'channel':
            msg1 += f"<a href='{chat['invite_link']}'>{chat['title']}</a>\n"
        elif chat['type'] == 'supergroup':
            msg2 += f"<a href='{chat['invite_link']}'>{chat['title']}</a>\n"
    await call.message.answer(ded(f"""🆔 ID: <b>{theme_info['id']}</b>
                                  🎲 Название: <b>{theme_info['name']}</b>

                                  🔢 Каналов/Групп с этой тематикой: <b>{len(channel_info)}</b>
                                  
                                  📢 Список каналов:
                                  {msg1}
                                  👥 Список супергрупп:
                                  {msg2}"""), reply_markup=adm_edit_list_theme(theme_id = theme_info['id']))

#Рассылка
@dp.callback_query_handler(IsAdmin(), text="newsletter", state="*")
async def func_newsletter_tip(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    await call.message.answer("Выберите тип рассылки", reply_markup=kb_tip_newsletter())
    
@dp.callback_query_handler(IsAdmin(), text_startswith="msg", state="*")
async def func_newsletter_msg(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    type_id = call.data.split(":")[1]
    if type_id == 'text':
        await call.message.answer("Введите текст рассылки", reply_markup=back_tip_news())
        await Newsletter.msg.set()
    elif type_id == 'photo':
        await call.message.answer("Введите текст рассылки", reply_markup=back_tip_news())
        await Newsletter_photo.msg.set()
    
@dp.message_handler(state=Newsletter_photo.msg)
async def func_newsletter_text(message: Message, state: FSMContext):
    msg = message.parse_entities()
    await state.update_data(msg=message.text)
    await message.answer("Отправьте фотографию для рассылки", reply_markup=adm_back_main())
    await Newsletter_photo.photo.set()
    
@dp.message_handler(IsAdmin(), content_types=['photo'], state=Newsletter_photo.photo)
async def mail_photo_starts(message: Message, state: FSMContext):
    photo = message.photo[-1].file_id
    await state.update_data(photo=photo)
    data = await state.get_data()
    await send_admins(f"<b>❗ Администратор @{message.from_user.username} запустил рассылку!</b>")
    users = await db.all_users()
    yes_users, no_users = 0, 0
    for user in users:
        user_id = user['id']
        try:
            user_id = user['user_id']
            await bot.send_photo(chat_id=user_id, photo=data['photo'] ,caption=data['msg'])
            yes_users += 1
        except:
            no_users += 1

    new_msg = f"""
<b>💎 Всего пользователей: <code>{len(await db.all_users())}</code>
✅ Отправлено: <code>{yes_users}</code>
❌ Не отправлено (Бот заблокирован): <code>{no_users}</code></b>
    """

    await message.answer(new_msg)
    await state.finish()
    
@dp.message_handler(state=Newsletter.msg)
async def func_newsletter_text(message: Message, state: FSMContext):
    await state.update_data(msg=message.text)
    data = await state.get_data()
    await send_admins(f"<b>❗ Администратор @{message.from_user.username} запустил рассылку!</b>")
    users = await db.all_users()
    yes_users, no_users = 0, 0
    for user in users:
        user_id = user['id']
        try:
            user_id = user['user_id']
            await bot.send_message(chat_id=user_id, text=data['msg'])
            yes_users += 1
        except:
            no_users += 1

    new_msg = f"""
<b>💎 Всего пользователей: <code>{len(await db.all_users())}</code>
✅ Отправлено: <code>{yes_users}</code>
❌ Не отправлено (Бот заблокирован): <code>{no_users}</code></b>
    """

    await message.answer(new_msg)
    await state.finish()

#Редактирование название тематики
@dp.callback_query_handler(text_startswith="edit_name_theme", state="*")
async def func_edit_name_theme(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    theme_id = call.data.split(":")[1]
    await call.message.answer("Укажите новое название тематики")
    await EditTheme.name.set()
    await state.update_data(theme_id=theme_id)
    
@dp.message_handler(state=EditTheme.name)
async def func_NewTheme_text(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    data = await state.get_data()
    await db.edit_theme_name(id=data['theme_id'], name=data['name'])
    await message.answer("Успешно изменено", reply_markup=adm_back_list_theme())

#Добавление Каналов/Групп
@dp.callback_query_handler(text_startswith="add_channel_theme", state="*")
async def func_add_channel(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    theme_id = call.data.split(":")[1]
    await call.message.answer("Укажите айди канала/группы\nНапример <b>-123456789</b>")
    await AddGroup.channel_id.set()
    await state.update_data(theme_id=theme_id)

#Удаление Каналов/Групп
@dp.callback_query_handler(text_startswith="del_channel_theme", state="*")
async def func_del_chats(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    theme_id = call.data.split(":")[1]
    await call.message.answer("Выберите Канал/Группу для удаления", reply_markup= await del_list_channels(theme_id=theme_id))
    
@dp.callback_query_handler(text_startswith="del_chat", state="*")
async def func_del_chats2(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    theme_id = call.data.split(":")[1]
    channel_id = call.data.split(":")[2]
    await db.delete_order(theme_id=theme_id, chat_id=channel_id)
    # await call.message.answer("Успешно удалено", reply_markup=adm_back_delete(theme_id=theme_id))
    channel_info = await db.list_chat_theme(theme_id=theme_id)
    theme_info = await db.get_theme(id=theme_id)
    msg1 = ""
    msg2 = ""
    for i, list in enumerate(channel_info):
        chat = await bot.get_chat(list['chat_id'])
        if chat['type'] == 'channel':
            msg1 += f"<a href='{chat['invite_link']}'>{chat['title']}</a>\n"
        elif chat['type'] == 'supergroup':
            msg2 += f"<a href='{chat['invite_link']}'>{chat['title']}</a>\n"
    await call.message.answer(ded(f"""🆔 ID: <b>{theme_info['id']}</b>
                                  🎲 Название: <b>{theme_info['name']}</b>

                                  🔢 Каналов/Групп с этой тематикой: <b>{len(channel_info)}</b>
                                  
                                  📢 Список каналов:
                                  {msg1}
                                  👥 Список супергрупп:
                                  {msg2}"""), reply_markup=adm_edit_list_theme(theme_id = theme_info['id']))
    
@dp.message_handler(state=AddGroup.channel_id)
async def func_addGroup_text(message: Message, state: FSMContext):
    await state.update_data(channel_id=message.text)
    data = await state.get_data()
    try:
        chat = await bot.get_chat(data['channel_id'])
        await db.new_chat(chat_id=chat['id'], theme_id=data['theme_id'], chat_type=chat['type'])
        await bot.send_message(message.from_user.id, "Канал успешно добавлен!", reply_markup=adm_back_list_theme())
    except Exception as e:
        await bot.send_message(message.from_user.id, f'Ошибка: {e}', reply_markup=adm_reload_channel(data['theme_id']))
        
#Добавление услуг
@dp.callback_query_handler(IsAdmin(), text="adm_services", state="*")
async def func_adm_servises(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    await bot.send_message(call.from_user.id, "Доступныый список услуг", reply_markup=await adm_services_list())    
    
@dp.callback_query_handler(text_startswith="no", state="*")
async def func_no(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    unix = call.data.split(":")[1]
    order_info = await db.get_orders(unix=unix)
    if order_info['status'] == 'waiting':
        await db.edit_order_status(unix=unix, status='rejected')
        await bot.send_message(int(order_info['user_id']), "Ваша заявка была отклоненна администратором")
    else:
        await call.message.answer("Уже не актуально")
    
@dp.callback_query_handler(text_startswith="yes", state="*")
async def func_yes(call: CallbackQuery, state: FSMContext):
    await state.finish()
    unix = call.data.split(":")[1]
    order_info = await db.get_orders(unix=unix)
    if order_info['status'] == 'waiting':
        await db.edit_order_status(unix=unix, status='accepted')
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        if order_info['video_id'] or order_info['photo_id']:
            await bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption="<b>Укажите цену</b>")
        else:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="<b>Укажите цену</b>")
        await GetPrice.price.set()
        await state.update_data(unix = unix)
    else:
        await call.message.answer("Уже не актуально")

@dp.message_handler(state=GetPrice.price)
async def func_Getprice_text(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    data = await state.get_data()
    if is_number(data['name']):
        order_info = await db.get_orders(unix=data['unix'])
        await db.edit_order_status(unix=data['unix'], price=data['name'])
        await send_back(user_id=order_info['user_id'], msg=ded(f"""{order_info['msg']}
                                                            🟰🟰🟰🟰🟰🟰🟰
                                                            <b>Ваша заявка принята</b>
                                                            <b>К оплате:</b> <i>{data['name']}</i>"""), photo=order_info['photo_id'], video=order_info['video_id'], reply_markup=kb_sposob_opl(unix=data['unix'], price=data['name']))
    else:
        await message.answer("Нужно указать число!")
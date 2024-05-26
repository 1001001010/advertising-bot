from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.data.loader import dp, bot
from bot.data.config import db, cryptoBot
from bot.utils.utils_functions import send_admins
from bot.keyboards.inline import kb_open_type, list_channels, user_services_list, kb_yes_mo, refill_open_inl_aaio, refill_open_inl
from bot.state.user import NewPost
from bot.utils.utils_functions import ded, get_date, get_unix, send_back, send_back2
from bot.data.config import db, aaio_client
from bot.utils.aaio import Aaio
from bot.data import config
from AsyncPayments.cryptoBot import AsyncCryptoBot

try:
    aaio = Aaio(
        aaio_api_key=config.aaio_api_key,
        aaio_id_shop=config.aaio_id_shop,
        aaio_secret_key=config.aaio_secret_key_1
    )
except:
    pass

#Открытие меню
@dp.message_handler(text="📰  Заказать рекламу", state="*")
async def func__menu(message: Message, state: FSMContext):
    await state.finish()
    orders = await db.get_orders(user_id = message.from_user.id, status = 'waiting')
    if orders:
        await message.answer("<b>Дождитесь одобрения предыдущей заявки</b>")
    else:
        await message.answer("Выберите тематику канала", reply_markup=await kb_open_type())
    
@dp.callback_query_handler(text="user_list_theme", state="*")
async def func__menu2(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    await bot.send_message(call.from_user.id, "Выберите тематику канала", reply_markup=await kb_open_type())
    
#Выбор тематики канала
@dp.callback_query_handler(text_startswith="change_theme", state="*")
async def func_pick_theme(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    theme_id = call.data.split(":")[1]
    await bot.send_message(call.from_user.id, "Выберите канал, в котором хотите опубликовать свою запись", reply_markup=await list_channels(theme_id=theme_id))
    
@dp.callback_query_handler(text_startswith="select_chat", state="*")
async def func_pick_theme(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    theme_id = call.data.split(":")[1]
    channel_id = call.data.split(":")[2]
    await bot.send_message(call.from_user.id, "Выберите тип услуги", reply_markup=await user_services_list(theme_id=theme_id, channel_id=channel_id))
    
@dp.callback_query_handler(text_startswith="select_services", state="*")
async def func_pick_theme(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    theme_id = call.data.split(":")[1]
    channel_id = call.data.split(":")[2]
    type_id = call.data.split(":")[3] 
    await call.message.answer("Отправьте сообщение. Можете использовать Telegram разметку, отправляйте сразу с фото и видео")
    await NewPost.msg.set()
    await state.update_data(theme_id=theme_id)
    await state.update_data(channel_id=channel_id)
    await state.update_data(type_id=type_id)
    
@dp.message_handler(state=NewPost.msg, content_types=['photo', 'video', 'text'])
async def func_NewTheme_text(message: Message, state: FSMContext):
    if message.photo:
        msg = message.parse_entities()
        photo_id = message.photo[-1].file_id
        await state.update_data(msg=msg)
        video_id = None
    elif message.video:
        msg = message.parse_entities()
        video_id = message.video.file_id
        await state.update_data(msg=msg)
        photo_id = None
    elif message.text:
        msg = message.parse_entities()
        print(msg)
        await state.update_data(msg=msg)
        video_id = None
        photo_id = None
    data = await state.get_data()
    date = get_date(True)
    theme_name = await db.get_theme(id=data['theme_id'])
    chat = await bot.get_chat(data['channel_id'])
    type_name = await db.get_services(id=data['type_id'])
    unix = get_unix()
    await db.add_orders(date=date, theme=theme_name['id'], channel=data['channel_id'], type=type_name['id'], photo_id=photo_id, video_id=video_id, msg=data['msg'], status='waiting', unix=unix, user_id=message.from_user.id)
    await bot.send_message(message.from_user.id, "Ваша заявка отправленна, дожидайтесь ее одобрения")
    await send_admins(msg=ded(f"""
                        {data['msg']}
                        
                        🟰🟰🟰🟰🟰🟰🟰
                        <b>Дата:</b> <i>{date}</i>
                        <b>Тематика:</b> <i>{theme_name['name']}</i>
                        <b>Канал:</b> <a href='{chat['invite_link']}'>{chat['title']}</a>
                        <b>Тип:</b> <i>{type_name['name']}</i>
                        """), photo=photo_id, video=video_id, reply_markup=kb_yes_mo(unix=unix))
    
@dp.callback_query_handler(text_startswith="aaio", state="*")
async def func_vibor_plat(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    unix = call.data.split(":")[1]
    price = call.data.split(":")[2]
    group_info = await db.get_orders(unix=unix)
    payment = await aaio_client.create_payment_url(amount=price, order_id=unix, desc=group_info['date'])
    await bot.send_message(call.from_user.id, "Оплатите по ссылке ниже, после оплаты ваша реклама будет опубликовано", reply_markup=refill_open_inl_aaio(link=payment, unix=unix, pay_id=unix))

@dp.callback_query_handler(text_startswith="check_aaio_opl", state="*")
async def func_check_opl(call: CallbackQuery, state: FSMContext):
    await state.finish()
    pay_id = call.data.split(":")[1]
    unix = call.data.split(":")[2]
    order_info = await aaio.check_payment(order_id=pay_id)
    group_info = await db.get_orders(unix=unix)
    if order_info == True:
        await call.message.delete()
        await call.message.answer("Ваше сообщение успешно опубликовано")
        if int(group_info['type']) == 2:
            await db.edit_order_status(unix=unix, status='paid')
            await send_back(user_id=group_info['channel'], msg=ded(f"{group_info['msg']}"), photo=group_info['photo_id'], video=group_info['video_id'])
        elif int(group_info['type']) == 1:
            await db.edit_order_status(unix=unix, status='paid')
            sent_message = ded(f"{group_info['msg']}")
            await send_back2(user_id=group_info['channel'], msg=sent_message, photo=group_info['photo_id'], video=group_info['video_id'])
    elif order_info == False:
        await call.answer("❌ Платеж не найдет")
        
@dp.callback_query_handler(text_startswith="Crypto_bot", state="*")
async def func_Cryptobot(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    unix = call.data.split(":")[1]
    price = call.data.split(":")[2]
    group_info = await db.get_orders(unix=unix)
    cheack = await cryptoBot.create_invoice(amount=price, currency_type="fiat", fiat="RUB", description=group_info['date'])
    pay_url = cheack.pay_url
    amount = cheack.amount
    fiat = cheack.fiat
    invoice_id = cheack.invoice_id
    await bot.send_message(call.from_user.id, "Оплатите по ссылке ниже, после оплаты ваша реклама будет опубликовано", reply_markup=refill_open_inl(link=pay_url, invoice_id=invoice_id, unix=unix))
    
@dp.callback_query_handler(text_startswith="check_opl", state="*")
async def func_check_opl_crypto(call: CallbackQuery, state: FSMContext):
    await state.finish()
    invoice_id = call.data.split(":")[1]
    unix = call.data.split(":")[2]
    order_info = await db.get_orders(unix=unix)
    cheack = await cryptoBot.get_invoices(invoice_ids=invoice_id)
    if cheack[0].status == 'active':
        await call.answer("❌ Платеж не найдет")
    elif cheack[0].status == 'paid':
        await call.message.delete()
        await call.message.answer("Ваше сообщение успешно опубликовано")
        
        if int(order_info['type']) == 2:
            await db.edit_order_status(unix=unix, status='paid')
            await send_back(user_id=order_info['channel'], msg=ded(f"{order_info['msg']}"), photo=order_info['photo_id'], video=order_info['video_id'])
        elif int(order_info['type']) == 1:
            await db.edit_order_status(unix=unix, status='paid')
            sent_message = ded(f"{order_info['msg']}")
            await send_back2(user_id=order_info['channel'], msg=sent_message, photo=order_info['photo_id'], video=order_info['video_id'])   
    else:
        await call.answer("❌ Платеж не найдет")
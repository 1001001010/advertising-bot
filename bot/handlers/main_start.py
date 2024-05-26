from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.data.config import db
from bot.data.loader import dp, bot
from bot.keyboards.reply import user_menu

#Обработка команды /start
@dp.message_handler(commands=['start'], state="*")
async def func_main_start(message: Message, state: FSMContext):
    await state.finish()
    await bot.send_message(message.from_user.id, f"Добро пожаловать, {message.from_user.username}, у нас вы можете оставить заявку на рекламу", reply_markup=await user_menu(message.from_user.id))
    
# В основное меню
@dp.callback_query_handler(text='back_to_m', state="*")
async def change_language(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    await bot.send_message(call.from_user.id, f"Добро пожаловать, {call.from_user.username}, у нас вы можете оставить заявку на рекламу", reply_markup=await user_menu(call.from_user.id))
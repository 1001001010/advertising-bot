from aiogram.dispatcher.filters.state import State, StatesGroup


class NewTheme(StatesGroup): #State на добавление тематики
    name = State()
    
class EditTheme(StatesGroup): #State на редактирование названия тематики
    theme_id = State()
    name = State()
    
class AddGroup(StatesGroup): #State на Добавление группы
    theme_id = State()
    channel_id = State()
    
class GetPrice(StatesGroup):
    unix = State()
    price = State()
    
class Newsletter(StatesGroup): #State на рассылку
    msg = State()
    
class Newsletter_photo(StatesGroup): #State на рассылку с офто
    msg = State()
    photo = State()
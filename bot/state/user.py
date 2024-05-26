from aiogram.dispatcher.filters.state import State, StatesGroup


class NewPost(StatesGroup): #State на добавление тематики
    theme_id = State()
    channel_id = State()
    type_id = State()
    msg = State()
    photo = State()
    video = State()
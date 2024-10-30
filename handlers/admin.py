from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from create_bot import bot, c, con
from aiogram.dispatcher.filters import Text
from keyboards import kb_admin
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ContentType, ReplyKeyboardRemove, InlineKeyboardButton, \
    InlineKeyboardMarkup

ID = None
NUMBERS = [15, 16, 17, 18, 19]


# Add task

class FSMAdminAdd(StatesGroup):
    n = State()
    task = State()
    answer = State()
    source = State()


async def make_changes_command(message: types.Message):
    global ID
    ID = message.from_user.id
    await bot.send_message(message.from_user.id, 'Что хозяин надо?', reply_markup=kb_admin)
    await message.delete()


async def cm_start_add(message: types.Message):
    if message.from_user.id == ID:
        await FSMAdminAdd.n.set()
        await message.reply('Какое задание хотите добавить?', reply_markup=ReplyKeyboardRemove())


async def load_n_add(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        if not message.text.isdigit() or int(message.text) not in NUMBERS:
            await message.reply('Какое задание хотите добавить? Доступные: ' + ' '.join(map(str, NUMBERS)))
            return
        async with state.proxy() as data:
            data['n'] = message.text
        await FSMAdminAdd.next()
        await message.reply('Введи задание')


async def load_task(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['task'] = message.text
        await FSMAdminAdd.next()
        await message.reply('Введи ответ на это задание')


async def load_answer(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['answer'] = message.text
        await FSMAdminAdd.next()
        await message.reply('Теперь введи источник')


async def load_source(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['source'] = message.text

        async with state.proxy() as data:
            c.execute(f"INSERT INTO EgeNumber{data['n']}(task, answer, source) VALUES(?, ?, ?)",
                      (data['task'], data['answer'], data['source']))
            con.commit()
        await state.finish()
        await bot.send_message(message.from_user.id, 'Задание добавлено!', reply_markup=kb_admin)


async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('OK', reply_markup=kb_admin)


# Edit task

async def edit_task_menu(message: types.Message):
    pass


# Del task

class FSMAdminDel(StatesGroup):
    n = State()
    id = State()


async def cm_start_del(message: types.Message):
    if message.from_user.id == ID:
        await FSMAdminDel.n.set()
        await message.reply('Какое задание хотите удалить?', reply_markup=ReplyKeyboardRemove())


async def load_n_del(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        if not message.text.isdigit() or int(message.text) not in NUMBERS:
            await message.reply('Какое задание хотите удалить? Доступные: ' + ' '.join(map(str, NUMBERS)))
            return
        async with state.proxy() as data:
            data['n'] = message.text
        await message.reply('Введите айди задания')
        await FSMAdminAdd.next()


async def del_task_menu(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            c.execute(f"DELETE FROM EgeNumber{data['n']} WHERE id={message.text}")
            con.commit()
            await state.finish()
            await bot.send_message(message.from_user.id, 'Успешно удалено', reply_markup=kb_admin)


async def get_id_task(message: types.Message):
    if message.from_user.id == ID:
        from client import slider
        id = slider[0][slider[1]][1]
        await bot.send_message(message.from_user.id, id)


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(make_changes_command, text=['moderator', '/moderator'], is_chat_admin=True)
    dp.register_message_handler(cm_start_add, text=['Добавить', '/add'], state=None)
    dp.register_message_handler(cm_start_del, text=['Удалить', '/del'], state=None)
    dp.register_message_handler(cancel_handler, state="*", text=['Отмена', '/Отмена'])
    dp.register_message_handler(cancel_handler, Text(equals=['отмена', '/отмена'], ignore_case=True), state="*")
    dp.register_message_handler(load_n_add, state=FSMAdminAdd.n)
    dp.register_message_handler(load_task, state=FSMAdminAdd.task)
    dp.register_message_handler(load_answer, state=FSMAdminAdd.answer)
    dp.register_message_handler(load_source, state=FSMAdminAdd.source)
    dp.register_message_handler(load_n_del, state=FSMAdminDel.n)
    dp.register_message_handler(del_task_menu, state=FSMAdminDel.id)
    dp.register_message_handler(get_id_task, text=['id', '/id'])

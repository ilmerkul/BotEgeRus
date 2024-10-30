from aiogram import types, Dispatcher
from create_bot import bot, c, con
from keyboards import kb_client1, kb_client2, sub_inline_markup, kb_slider, buy_menu
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ContentType, ReplyKeyboardRemove, InlineKeyboardButton, \
    InlineKeyboardMarkup
from random import random, randint
import datetime
from pyqiwip2p import QiwiP2P

mode_train = [0, 0, 0, 0]
slider = [[], 0]

QIWI_TOKEN = 'eyJ2ZXJzaW9uIjoiUDJQIiwiZGF0YSI6eyJwYXlpbl9tZXJjaGFudF9zaXRlX3VpZCI6InFlNWRvZS0wMCIsInVzZXJfaWQiOiI3OTA2MjY2MjM1MCIsInNlY3JldCI6ImE1YmE0YjRlOTBmZDQ2ZDQwYTU2ODFkODEyMzNjZTkwYjdjNzAxMzM2ZjE1OGEzNzIxYmVkODQ1NzIyNzJlNzgifX0='
p2p = QiwiP2P(auth_key=QIWI_TOKEN)


async def subthreemonth(call: types.CallbackQuery):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    comment = str(call.from_user.id) + '_' + str(randint(1000, 9999))
    bill = p2p.bill(amount=149, lifetime=15, comment=comment)
    c.execute("INSERT INTO 'Check' ('user_id', 'sub', 'bill_id') VALUES(?, ?, ?)", (call.from_user.id, 1, bill.bill_id))
    con.commit()

    await bot.send_message(call.from_user.id, 'Оплатить', reply_markup=buy_menu(url=bill.pay_url, bill=bill.bill_id))


async def subconst(call: types.CallbackQuery):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    comment = str(call.from_user.id) + '_' + str(randint(1000, 9999))
    bill = p2p.bill(amount=349, lifetime=15, comment=comment)
    c.execute("INSERT INTO 'Check' ('user_id', 'sub', 'bill_id') VALUES(?, ?, ?)", (call.from_user.id, 0, bill.bill_id))
    con.commit()

    await bot.send_message(call.from_user.id, 'Оплатить', reply_markup=buy_menu(url=bill.pay_url, bill=bill.bill_id))


async def check_pay(callback: types.CallbackQuery):
    bill = str(callback.data[6:])
    info = c.execute("SELECT * FROM 'Check' WHERE bill_id=?", (bill,)).fetchmany(1)[0]
    if bool(info):
        if str(p2p.check(bill_id=bill).status) == 'PAID':
            if not bool(c.execute("SELECT id FROM Users WHERE user_id = ?", (info[1],)).fetchmany(1)):
                c.execute("INSERT INTO Users(user_id, sub) VALUES(?, ?)", (info[1], 0))
                con.commit()
            if info[2] == 1:
                c.execute("UPDATE Users SET sub=1, sub_date=? WHERE user_id=?",
                          (datetime.datetime.now() + datetime.timedelta(days=90), info[1]))
                await bot.send_message(callback.from_user.id, 'Вам выдана подписка на три месяца')
            elif info[2] == 0:
                c.execute("UPDATE Users SET sub=1 WHERE user_id=?", (info[1],))
                await bot.send_message(callback.from_user.id, 'Вам выдана подписка')

            c.execute("DELETE FROM 'Check' WHERE bill_id=?", (bill,))
            con.commit()
        else:
            await bot.send_message(callback.from_user.id, 'Вы не оплатили счет')
    else:
        await bot.send_message(callback.from_user.id, 'Счет не найден')


async def start_slider(call: types.CallbackQuery):
    _, n, source = call.data.split('_')
    data = [*map(lambda x: (f'{x[0]}\n\nОтвет: <span class="tg-spoiler">{str(x[1])}</span>', x[2]),
                 c.execute(f"SELECT task, answer, id FROM EgeNumber{n} WHERE source=?",
                           (source,)).fetchall())]
    data = [(str(i + 1) + ') ' + data[i][0], data[i][1]) for i in range(len(data))]
    slider[0] = data
    slider[1] = 0

    await bot.send_message(call.from_user.id, data[0][0], reply_markup=kb_slider, parse_mode=types.ParseMode.HTML)


async def update_slider(call: types.CallbackQuery):
    if call.data[-1] in ('⬅', '➡') and len(slider[0]) > 1:
        if call.data[-1] == '➡':
            slider[1] = (slider[1] + 1) % len(slider[0])
        elif call.data[-1] == '⬅':
            slider[1] = (slider[1] - 1) % len(slider[0])

        await call.message.edit_text(slider[0][slider[1]][0], reply_markup=kb_slider, parse_mode=types.ParseMode.HTML)


async def command_processing(message: types.Message):
    if message.text in ('/start', 'Старт'):
        await message.delete()

        await bot.send_message(message.from_user.id,
                               '👾 Я помогу тебе отлично подготовиться к ЕГЭ по русскому \n ❓ Введите /help, если возникли вопросы',
                               reply_markup=kb_client1)

        if not bool(c.execute("SELECT id FROM Users WHERE user_id = ?", (message.from_user.id,)).fetchmany(1)):
            c.execute("INSERT INTO Users(user_id, sub) VALUES(?, ?)", (message.from_user.id, 0))
            con.commit()
    elif message.text in ('/help', '❓Помощь'):
        await message.delete()

        await bot.send_message(message.from_user.id, 'Вы можете задать любой вопрос мне: @pynex')

    elif message.text == '🔥Премиум':
        await message.delete()

        if bool(c.execute("SELECT sub FROM Users WHERE user_id=?", (message.from_user.id,)).fetchmany(1)[0][0]):
            sub_date = c.execute("SELECT sub_date FROM Users WHERE user_id=?", (message.from_user.id,)).fetchmany(1)[0][
                0]
            if bool(sub_date):
                if datetime.datetime.strptime(sub_date.split()[0], "%Y-%m-%d") < datetime.datetime.now():
                    c.execute("UPDATE Users SET sub=0, sub_date=? WHERE user_id=?", ('', message.from_user.id))
                    con.commit()
                else:
                    await bot.send_message(message.from_user.id, f'У вас имеется подписка до {sub_date.split()[0]}')
            else:
                await bot.send_message(message.from_user.id, 'У вас уже имеется подписка навсегда)')
        else:
            await bot.send_message(message.from_user.id, 'Описание возможностей подписки', reply_markup=sub_inline_markup)

    elif message.text in ('/train', '💪Тренироваться'):

        await message.delete()

        await bot.send_message(message.from_user.id, '✏ Выбирай задание и отрабатывай его', reply_markup=kb_client2)
    elif message.text == 'Назад ⬅':
        await message.delete()

        await bot.send_message(message.from_user.id, 'Меню', reply_markup=kb_client1)

    elif message.text == '💁🏻‍♂️Наша группа':
        await message.delete()

        await bot.send_message(message.from_user.id, 'Наша группа: https://t.me/+vZuFaVSrVVc5NGRi')

    start_train(0, 0, 0, 0)
    slider[0] = []
    slider[0] = 0


async def train_processing(message: types.Message):
    if mode_train[0] == 4:
        if message.text == mode_train[2]:
            mode_train[1] += 1
            await bot.send_message(message.from_user.id, '✅Верно!')

            score = mode_train[1]
            word, variant1, variant2 = mode_train[3][score]
            mode_train[2] = variant1

            kb = ReplyKeyboardMarkup(resize_keyboard=True)
            kb.row(*map(KeyboardButton, sorted([variant1, variant2], key=lambda A: random())))

            await bot.send_message(message.from_user.id, word, reply_markup=kb)
        else:
            await bot.send_message(message.from_user.id, f'❌Неправильно\nВаш счет: {mode_train[1]}',
                                   reply_markup=kb_client2)
            start_train(0, 0, 0, 0)
    elif message.text in (
            '4) Ударения', '15) НН/Н', '16) Пунктуация', '17) Пунктуация', '18) Пунктуация', '19) Пунктуация'):
        if message.text == '4) Ударения':
            await message.delete()
            data = c.execute("SELECT word, word_variant1, word_variant2 FROM EgeNumber4 ORDER BY RANDOM()").fetchall()
            start_train(4, 0, 0, data)

            score = mode_train[1]
            word, variant1, variant2 = mode_train[3][score]
            mode_train[2] = variant1

            kb = ReplyKeyboardMarkup(resize_keyboard=True)
            kb.row(*map(KeyboardButton, sorted([variant1, variant2], key=lambda A: random())))

            await bot.send_message(message.from_user.id, word, reply_markup=kb)
        elif bool(c.execute("SELECT sub FROM Users WHERE user_id=?", (message.from_user.id,)).fetchmany(1)[0][0]):
            sub_date = c.execute("SELECT sub_date FROM Users WHERE user_id=?", (message.from_user.id,)).fetchmany(1)[0][
                0]
            if bool(sub_date):
                if datetime.datetime.strptime(sub_date.split()[0], "%Y-%m-%d") < datetime.datetime.now():
                    c.execute("UPDATE Users SET sub=0, sub_date=? WHERE user_id=?", ('', message.from_user.id))
                    con.commit()

            n = message.text.split(')')[0]
            categories = map(lambda x: InlineKeyboardButton(text=x[0], callback_data=f'slider_{n}_{x[0]}'),
                             set(c.execute(f"SELECT source FROM EgeNumber{n}").fetchall()))

            kb = InlineKeyboardMarkup(resize_keyboard=True)
            kb.add(*categories)

            await bot.send_message(message.from_user.id, 'Выбери источник:', reply_markup=kb)
        else:
            await bot.send_message(message.from_user.id, 'Эти задания доступны только пользователям с подпиской :(')


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(command_processing,
                                text=['/start', 'Старт', '/help', '❓Помощь', '🔥Премиум', '/train', '💪Тренироваться',
                                      'Назад ⬅', '💁🏻‍♂️Наша группа'])
    dp.register_message_handler(train_processing)

    dp.register_callback_query_handler(start_slider, text_contains='slider_')
    dp.register_callback_query_handler(update_slider, text_contains='update_slider')

    dp.register_callback_query_handler(subthreemonth, text='subthreemonth')
    dp.register_callback_query_handler(subconst, text='subconst')
    dp.register_callback_query_handler(check_pay, text_contains='check_')


def start_train(n, score, answer, data):
    mode_train[0] = n
    mode_train[1] = score
    mode_train[2] = answer
    mode_train[3] = data

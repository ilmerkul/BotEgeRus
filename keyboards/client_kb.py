from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton

b1 = KeyboardButton('💪Тренироваться')
b2 = KeyboardButton('🔥Премиум')
b3 = KeyboardButton('💁🏻‍♂️Наша группа')
b4 = KeyboardButton('❓Помощь')

kb_client1 = ReplyKeyboardMarkup(resize_keyboard=True)

kb_client1.row(b1, b2).row(b3, b4)

b5 = KeyboardButton('4) Ударения')
b6 = KeyboardButton('15) НН/Н')
b7 = KeyboardButton('16) Пунктуация')
b8 = KeyboardButton('17) Пунктуация')
b9 = KeyboardButton('18) Пунктуация')
b10 = KeyboardButton('19) Пунктуация')
b11 = KeyboardButton('Назад ⬅')

kb_client2 = ReplyKeyboardMarkup(resize_keyboard=True)

kb_client2.add(b5, b6, b7, b8, b9, b10, b11)

sub_inline_markup = InlineKeyboardMarkup(row_width=1)

btnSubTreeMonth = InlineKeyboardButton(text='3 месяца - 149 руб', callback_data='subthreemonth')
btnSub = InlineKeyboardButton(text='навсегда - 349 руб', callback_data='subconst')

sub_inline_markup.insert(btnSubTreeMonth).insert(btnSub)


def buy_menu(isUrl=True, url='', bill=''):
    qiwiMenu = InlineKeyboardMarkup(row_width=1)
    if isUrl:
        btnUrlQiwi = InlineKeyboardButton(text='Оплатить', url=url)
        qiwiMenu.insert(btnUrlQiwi)

    btnCheckQiwi = InlineKeyboardButton(text='Проверить оплату', callback_data='check_' + bill)
    qiwiMenu.insert(btnCheckQiwi)
    return qiwiMenu

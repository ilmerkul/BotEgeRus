from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import sqlite3

# import os

storage = MemoryStorage()

# bot = Bot(token=os.getenv('TOKEN'))
bot = Bot(token='5108503462:AAFn5UVmuw6Z2HDJcs2yaDy8g25tWU_UtCU')
dp = Dispatcher(bot, storage=storage)

con = sqlite3.connect('RusEgeDB.db')
c = con.cursor()

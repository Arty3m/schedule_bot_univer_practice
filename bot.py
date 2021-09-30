from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types.message import ContentType

from config import TOKEN

from group_schedule import available_groups, available_days, schedule
from db import BotDB
import keyboard as kb

BotDB = BotDB('allusers.db')

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands='help', commands_prefix='/!')
async def process_help_command(message: types.Message):
    await bot.send_message(message.from_user.id,
                           '/help - список доступных команд\n/group АА-000 - чтобы выбрать группу')


@dp.message_handler(commands='start', commands_prefix='/!')
async def process_start_command(message: types.Message):
    if BotDB.user_exists(message.from_user.id):
        if BotDB.get_user_group(message.from_user.id):
            already_selected_group = 'Я тебя помню! Ты из группы ' + BotDB.get_user_group(
                message.from_user.id) + '\nСписок всех доступных команд - /help'
            await bot.send_message(message.from_user.id, already_selected_group)
            await message.answer('Выбери день недели:', reply_markup=kb.choosing_day)
        else:
            await message.answer('Мне кажется я тебя уже видел!\nДля того чтобы выбрать группу введи \n/group AA-000')
    else:
        BotDB.add_user(message.from_user.id)
        await bot.send_message(message.from_user.id,
                               'Добро пожаловать!\nДля того чтобы выбрать группу введи \n/group AA-000')


@dp.message_handler(commands='group', commands_prefix='/!')
async def process_group_command(message: types.Message):
    inserted_group = message.get_args().upper()
    if inserted_group == '':
        await bot.send_message(message.from_user.id, 'Введите группу в формате: /group - AA-000')
    else:
        if inserted_group in available_groups:
            if not BotDB.get_user_group(message.from_user.id):
                BotDB.add_user_group(message.from_user.id, inserted_group)
                await bot.send_message(message.from_user.id, 'Группа успешно установлена!')
                await message.answer('Выбери день недели:', reply_markup=kb.choosing_day)
            else:
                BotDB.add_user_group(message.from_user.id, inserted_group)
                await bot.send_message(message.from_user.id, 'Группа успешно изменена!')
                await message.answer('Выбери день недели:', reply_markup=kb.choosing_day)
        else:
            await bot.send_message(message.from_user.id, 'Такой группы нет в списке доступных.\nВведите еще раз')


@dp.message_handler(content_types=ContentType.TEXT)
async def schedule_for_day(message: types.Message):
    if BotDB.get_user_group(message.from_user.id):
        gr = BotDB.get_user_group(message.from_user.id)
        print(gr)
        day = message.text.lower()
        if day in available_days:
            await message.answer(schedule[gr, day])
        else:
            await message.answer('Выбери день недели:', reply_markup=kb.choosing_day)
    else:
        await bot.send_message(message.from_user.id, 'Введите группу в формате: /group - AA-000')


if __name__ == '__main__':
    executor.start_polling(dp)

import asyncio
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.utils.markdown import bold
from aiogram.types import ParseMode
from aiogram.utils.exceptions import MessageCantBeDeleted, MessageToDeleteNotFound
from contextlib import suppress
import datetime
from config import TOKEN, admins
from shedule_scrap import get_schedule, fill_db, reset_db, get_week_num, get_data
from group_schedule import available_groups, available_days
from db import BotDB

import keyboard as kb

BotDB = BotDB('databases/allusers.db')

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
count = 0


async def delete_message(msg: types.Message, sleep_time: int = 0, msg1: types.Message = types.Message):
    if await bot.get_chat_member_count(msg.chat.id) > 2:
        await asyncio.sleep(sleep_time)
        with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
            await msg.delete()
            try:
                await msg1.delete()
            except Exception:
                print('Не удалось удалить сообщение 2')


@dp.message_handler(commands='help', commands_prefix='/!')
async def process_help_command(message: types.Message):
    msg = await bot.send_message(message.from_user.id,
                                 '/help - список доступных команд\n/group АА-000 - чтобы выбрать группу\n'
                                 'Чтобы увидеть расписание на определенный день введите\n'
                                 '/Понедельник или /любой_ день_недели (с пн - сб)')
    await asyncio.create_task(delete_message(msg, 15))


@dp.message_handler(commands='start', commands_prefix='/!')
async def process_start_command(message: types.Message):
    if BotDB.user_exists(message.from_user.id):
        if BotDB.get_user_group(message.from_user.id):
            already_selected_group = f'{message.from_user.first_name}, я тебя помню! Ты из группы ' + BotDB.get_user_group(
                message.from_user.id) + '\nСписок всех доступных команд - /help'
            await bot.send_message(message.from_user.id, already_selected_group)
            await message.answer('Выбери день недели:', reply_markup=kb.choosing_day)
        else:
            await message.answer('Мне кажется я тебя уже видел!\nДля того чтобы выбрать группу введи \n/group ИИ-000')
    else:
        BotDB.add_user(message.from_user.id)
        msg = await bot.send_message(message.from_user.id,
                                     'Добро пожаловать!\nДля того чтобы выбрать группу введи \n/group ИИ-000')
        await asyncio.create_task(delete_message(msg, 15, message))


@dp.message_handler(commands='group', commands_prefix='/!')
async def process_group_command(message: types.Message):
    inserted_group = message.get_args().upper()
    if inserted_group == '':
        msg = await bot.send_message(message.from_user.id, 'Введите группу в формате: /group ИИ-000')
        await asyncio.create_task(delete_message(msg, 15, message))
    else:
        if inserted_group in available_groups:
            if not BotDB.get_user_group(message.from_user.id):
                BotDB.add_user_group(message.from_user.id, inserted_group)
                print(f'ID: {message.from_user.id} Group:{BotDB.get_user_group(message.from_user.id)} (new)')
                msg = await bot.send_message(message.from_user.id, 'Группа успешно установлена!')
                await message.answer('Выбери день недели:', reply_markup=kb.choosing_day)
                await asyncio.create_task(delete_message(msg, 15, message))

            else:
                BotDB.add_user_group(message.from_user.id, inserted_group)
                print(f'ID: {message.from_user.id} Group:{BotDB.get_user_group(message.from_user.id)} (change)')
                msg = await bot.send_message(message.from_user.id, 'Группа успешно изменена!')
                await asyncio.create_task(delete_message(msg, 15, message))
                await message.answer('Выбери день недели:', reply_markup=kb.choosing_day)

        else:
            msg = await bot.send_message(message.from_user.id, 'Такой группы нет в списке доступных.\nВведите '
                                                               'группу в формате: /group ИИ-000')
            await asyncio.create_task(delete_message(msg, 15, message))


@dp.message_handler(commands=['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота'], commands_prefix='/!')
async def schedule_for_day(message: types.Message):
    if BotDB.get_user_group(message.from_user.id):
        gr = BotDB.get_user_group(message.from_user.id).upper()
        day = message.text.lower().strip('/!')
        if day in available_days:
            msg = await message.answer(
                f'Расписание на {bold(day.upper())} ({get_data(day)}, {"нечётная" if get_week_num() else "чётная"}):'
                f'\n\n{get_schedule(gr, day)}', parse_mode=ParseMode.MARKDOWN)
            await asyncio.create_task(delete_message(msg, 15, message))

    else:
        msg = await bot.send_message(message.from_user.id, 'Введите группу в формате: /group - ИИ-000')
        await asyncio.create_task(delete_message(msg, 15))


@dp.message_handler(commands=['admin'], commands_prefix='/!')
async def admin_command(message: types.Message):
    if str(message.from_user.id) in admins:
        match message.text.split(' ', )[1]:
            case 'fill':
                await message.answer('Заполнение..')
                txt = fill_db()
                await message.answer(txt)
            case 'reset':
                txt = reset_db()
                await message.answer(txt)
    else:
        await asyncio.create_task(delete_message(message, 3))


if __name__ == '__main__':
    executor.start_polling(dp)

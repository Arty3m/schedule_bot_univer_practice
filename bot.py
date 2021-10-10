import asyncio
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.utils.markdown import bold
from aiogram.types import ParseMode
from aiogram.utils.exceptions import MessageCantBeDeleted, MessageToDeleteNotFound
from contextlib import suppress

from config import TOKEN

from group_schedule import available_groups, available_days, to_snd, schedule
from db import BotDB
import keyboard as kb

BotDB = BotDB('allusers.db')

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
count = 0


async def delete_message(msg: types.Message, sleep_time: int = 0, msg1: types.Message = types.Message):
    if await bot.get_chat_member_count(msg.chat.id) > 2:
        await asyncio.sleep(sleep_time)
        with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
            await msg.delete()
            await msg1.delete()


@dp.message_handler(commands='help', commands_prefix='/!')
async def process_help_command(message: types.Message):
    await bot.send_message(message.from_user.id,
                           '/help - список доступных команд\n/group АА-000 - чтобы выбрать группу\n'
                           'Чтобы увидеть расписание на определенный день введите\n'
                           '/Понедельник или /любой_ день_недели (с пн - сб)')
    await asyncio.create_task(delete_message(msg, 15))


@dp.message_handler(commands='start', commands_prefix='/!')
async def process_start_command(message: types.Message):
    if BotDB.user_exists(message.from_user.id):
        if BotDB.get_user_group(message.from_user.id):
            already_selected_group = 'Я тебя помню! Ты из группы ' + BotDB.get_user_group(
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
    inserted_group = message.get_args().lower()
    if inserted_group == '':
        msg = await bot.send_message(message.from_user.id, 'Введите группу в формате: /group - ИИ-000')
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
            msg = await bot.send_message(message.from_user.id, 'Такой группы нет в списке доступных.\nВведите еще раз')
            await asyncio.create_task(delete_message(msg, 15, message))


@dp.message_handler(commands=['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота'], commands_prefix='/!')
async def schedule_for_day(message: types.Message):
    if BotDB.get_user_group(message.from_user.id):
        gr = BotDB.get_user_group(message.from_user.id).lower()
        day = message.text.lower().strip('/!')
        if day in available_days:
            msg = await message.answer(f'Расписание на {bold(to_snd[day])}:\n\n{schedule[gr, day]}',
                                       parse_mode=ParseMode.MARKDOWN)
            await asyncio.create_task(delete_message(msg, 15, message))
    else:
        msg = await bot.send_message(message.from_user.id, 'Введите группу в формате: /group - ИИ-000')
        await asyncio.create_task(delete_message(msg, 15))


if __name__ == '__main__':
    executor.start_polling(dp)

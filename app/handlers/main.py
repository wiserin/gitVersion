from aiogram import Router, F
from aiogram.types import ReplyKeyboardRemove
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from app.parse.telegram_parser import get_channel_name
import app.database.requests as db
import app.keyboards as kb
import requests
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import json

load_dotenv()

storage = MemoryStorage()
main_router = Router()
router = main_router

class Add_channel(StatesGroup):
    finish = State()

# Старт
@router.message(F.text == '/start')
async def cmd_start(message: Message):
    await db.initialization(message.from_user.id, message.from_user.username)
    await message.answer('Привет', reply_markup=kb.main_kb)

# Добавление канала
@router.message(F.text == 'Добавить канал')
async def add_newsmaker(message: Message, state: FSMContext):
    await message.answer('Пришлите username канала в формате @имя_канала')
    await state.set_state(Add_channel.finish)


@router.message(Add_channel.finish)
async def new_channel(message: Message, state: FSMContext):

    try:
        # Получение ссылки на канал и первичная проверка ее действительности
        channel = message.text.removeprefix('@')
        channel_link = f'https://t.me/s/{channel}'
        # channel_link = f'https://web.telegram.org/k/#@{channel}'
        code = requests.get(channel_link)
        channel_name = await get_channel_name(channel_link)
        print(code.status_code)
        print(code.url)
        print(channel_name)

        if code.status_code == 200 and code.url != 'https://telegram.org/' and channel_name != False:

            # Добавление канала и подписчика
            new = await db.new_newsmaker(channel_link, channel_name, message.from_user.id)

            # Если пользователь уже подписан
            if new == 'In':
                await message.answer(f'Вы уже подписаны на {channel_name}', reply_markup=kb.main_kb)
                await state.clear()

            # Если пользователь еще не был подписан
            elif new == 'Ok':
                await message.answer(f'Вы успешно подписались на "{channel_name}"',
                                      reply_markup=kb.main_kb)
                await state.clear()

            # Ошибка
            else:
                await message.answer('Ошибка', reply_markup=kb.main_kb)
                await state.clear()

        else:
            await message.answer('Источника не существует', reply_markup=kb.main_kb)
            await state.clear()


    except Exception:

        await message.answer('Ошибка', reply_markup=kb.main_kb)
        await print(Exception)
        await state.clear()


@router.message(F.text == 'Мои подписки')
async def my_subscriptions(message: Message):
    data = await db.get_my_subscriptions(message.from_user.id)
    k = data.keys()
    kb_ = await kb.sub_generator(k)
    await message.answer('Выберете источник', reply_markup=kb_)

@router.callback_query(lambda callback_query: callback_query.data.startswith('sub'))
async def my_subscriptions2(call: CallbackQuery):
    media = call.data.removeprefix('sub_')
    if media != 'cancel' and media == 'Telegram':
        data = await db.get_my_subscriptions(call.from_user.id)
        media_id = data[media]
        media_data = await db.get_media_name(media_id)

        for_callback = []
        for i in media_data:
            for_callback.append(i['id'])
        kb_ = await kb.media_info_kb(for_callback)

        text = ''
        count = 1
        for i in media_data:
            text+=f'{str(count)}) <a href="{i["link"]}">{i["name"]}</a>\n'
            count+=1


        await call.message.answer(text,
                                  reply_markup=kb_,
                                  parse_mode='html')
            
    elif media == 'cancel':
        await call.message.answer('Отмена', reply_markup=kb.main_kb)

    else:
        await call.message.answer('Функционал ещё находится в разработке',
                            reply_markup=kb.main_kb)

@router.callback_query(lambda callback_query: callback_query.data.startswith('minfo'))
async def media_info(call: CallbackQuery):
    try:
        id = int(call.data.removeprefix('minfo_'))
        kb_ = await kb.private_media_info_kb(id)
        media_data = (await db.get_media_name([id]))[0]
        await call.message.answer(f'<a href="{media_data["link"]}">{media_data["name"]}</a>',
                                reply_markup=kb_,
                                parse_mode='html')
    except IndexError as e:
        await call.message.answer('Канал не найден')

@router.callback_query(lambda callback_query: callback_query.data.startswith('unsub'))
async def unsubscribe(call: CallbackQuery):
    id = int(call.data.removeprefix('unsub_'))
    state = await db.unsubscribe(id, call.from_user.id)
    if state:
        await call.message.answer('Успешно', reply_markup=kb.main_kb)


# @router.message(F.text == 'Получить')
# async def get_what(message: Message):
#     cipher_suite = Fernet(os.getenv('KEY'))
#     data = {"token": os.getenv('API_TOKEsvetov_timofey"]}
#     edata = cipher_suite.encrypt(json.dumpsN'),
#             "media": ["futakuchimana", "t(data).encode())
#     headers = {"data": edata}

#     response = requests.get('http://213.148.9.188:8000/instagram/get_data', headers=headers)
#     ddata = json.loads(response.text)
#     print(ddata)
#     rdata = cipher_suite.decrypt(ddata['data'])
#     print(rdata.decode())
#     await message.answer(rdata.decode())
    
    
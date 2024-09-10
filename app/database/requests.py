from sqlalchemy import create_engine, update, delete
from sqlalchemy.orm import sessionmaker
from app.database.models import (Base, User, Mass_media)
import asyncio
import json

engine = create_engine('sqlite:///bot.db')


session = sessionmaker(bind=engine)
s = session()

# сериализация и десериализация списков
async def serialize_list(lst):
    return json.dumps(lst)

async def deserialize_list(s):
    return json.loads(s)

# инициализация нового пользователя
async def initialization(tg_id: int, username: str):
    user = s.query(User).filter(User.user_tg_id == tg_id).one_or_none()
    if user == None:
        new_user = User(user_tg_id=tg_id, username=username, subscriptions=await serialize_list({
            'Telegram':[],
            'Instagram':[],
            'X':[],
            'VK':[]
        }))
        s.add(new_user)
        s.commit()

# добавление нового источника и подписчика
async def new_newsmaker(link: str, channel_name: str, subscriber: int):
    try:

        channel = s.query(Mass_media).filter(Mass_media.media_link==link).one_or_none()
        # если источника еще нет в БД
        if channel == None:
            new = Mass_media(media_link=link, media_name=channel_name,
                              subscribers = await serialize_list([subscriber]))
            s.add(new)
            s.commit()

            # добавление канала в подписки
            s.refresh(new)
            for user in s.query(User.subscriptions).filter(User.user_tg_id == subscriber):
                subscriptions = await deserialize_list(user[0])
                tg_channels = subscriptions['Telegram']
                tg_channels.append(new.id)
                subscriptions['Telegram'] = tg_channels
                end = await serialize_list(subscriptions)
                upd = update(User).where(User.user_tg_id == subscriber).values(subscriptions=end)
                s.execute(upd)
                s.commit()
            return 'Ok'
        # если уже есть
        else:
            subscribers = []
            # получение уже имеющихся подписчиков
            for i in s.query(Mass_media.subscribers).filter(Mass_media.media_link==link):
                subscribers_list = await deserialize_list(i[0])
                for j in subscribers_list:
                    subscribers.append(j)

            # если пользователь уже подписан
            if subscriber in subscribers:
                return 'In'
            
            # добавление пользователя в число подписчиков
            else:
                subscribers.append(subscriber)
                channel.subscribers = await serialize_list(subscribers)
                s.commit()
                # добавление канала в подписки
                for user in s.query(User.subscriptions).filter(User.user_tg_id == subscriber):
                    subscriptions = await deserialize_list(user[0])
                    tg_channels = subscriptions['Telegram']
                    tg_channels.append(channel.id)
                    subscriptions['Telegram'] = tg_channels
                    end = await serialize_list(subscriptions)
                    upd = update(User).where(User.user_tg_id == subscriber).values(subscriptions=end)
                    s.execute(upd)
                    s.commit()
                
                return 'Ok'

    except Exception:
        await print(Exception)

# получение всех источников
async def get_newsmakers():
    newsmakers = []
    for i in s.query(Mass_media.media_link):
        newsmakers.append(i[0])

    return newsmakers

# проверка актуальности текста новости
async def check_new_text(link: str, new: dict):
    for i in s.query(Mass_media.last_message).filter(Mass_media.media_link == link):
        if i[0] != None:
            text_in_db = await deserialize_list(i[0])
        else:
            upd = update(Mass_media).where(Mass_media.media_link == link).values(last_message=await serialize_list(new))
            s.execute(upd)
            s.commit()
            return True
        # print(f'text from db: {text_in_db}')
        # print(f'text from telegram: {new}')
        if text_in_db['text']:
            if text_in_db['text'] == new['text']:
                return False
            else:
                upd = update(Mass_media).where(Mass_media.media_link == link).values(last_message=await serialize_list(new))
                s.execute(upd)
                s.commit()
                return True
        else:
            new_media = []
            old_media = []

            if new['photo']:
                for i in new['photo']:
                    new_media.append(i)
            if new['video']:
                for i in new['video']:
                    new_media.append(i)

            if text_in_db['photo']:
                for i in text_in_db['photo']:
                    old_media.append(i)
            if text_in_db['video']:
                for i in text_in_db['video']:
                    old_media.append(i)

            if len(new_media) == len(old_media):
                сoincidences = 0

                for i in new_media:
                    if i in old_media:
                        сoincidences += 1
                
                if сoincidences == len(old_media):
                    return False
                else:
                    upd = update(Mass_media).where(Mass_media.media_link == link).values(last_message=await serialize_list(new))
                    s.execute(upd)
                    s.commit()
                    return True
            else:
                upd = update(Mass_media).where(Mass_media.media_link == link).values(last_message=await serialize_list(new))
                s.execute(upd)
                s.commit()
                return True

    # new_ = s.query(Mass_media).filter(Mass_media.media_link == link,
    #                                   Mass_media.last_message == await serialize_list(new)).one_or_none()
    # # если актуален, обновление последнего сообщения в бд
    # if new_ == None:
    #     upd = update(Mass_media).where(Mass_media.media_link == link).values(last_message=await serialize_list(new))
    #     s.execute(upd)
    #     s.commit()
    #     return True
    # else:
    #     return False

# получение подписчиков источника
async def get_subscribers(link: str):
    for i in s.query(Mass_media.subscribers).filter(Mass_media.media_link == link):
        return await deserialize_list(i[0])

async def get_channel_name(link: str):
    for i in s.query(Mass_media.media_name).filter(Mass_media.media_link == link):
        return i[0]

# удаление источника
async def delete_newsmaker(link: str):
    delt = delete(Mass_media).where(Mass_media.media_link == link)
    s.execute(delt)
    s.commit()

async def get_my_subscriptions(id: int) -> dict:
    for i in s.query(User.subscriptions).filter(User.user_tg_id == id):
        list_ = await deserialize_list(i[0])
        return list_
    
async def get_media_name(ids: list):
    response = []
    for id in ids:
        for i in s.query(Mass_media.media_name, 
                         Mass_media.media_link).filter(Mass_media.id == id):
            response.append({'id': id,
                             'name': i[0],
                             'link': i[1]})
    return response

async def unsubscribe(media_id: int, user_id: int):
    for i in s.query(Mass_media.subscribers).filter(Mass_media.id == media_id):
        sub = await deserialize_list(i[0])
        print(sub)
        print(user_id)
        sub.remove(user_id)
        if len(sub) > 0:
            upd = update(Mass_media).where(Mass_media.id == media_id).values(subscribers=await serialize_list(sub))
            s.execute(upd)
            s.commit()
        else:
            del_ = delete(Mass_media).where(Mass_media.id == media_id)
            s.execute(del_)
            s.commit()


    for i in s.query(User.subscriptions).filter(User.user_tg_id == user_id):
        pre_media = await deserialize_list(i[0])
        media = [pre_media['Telegram'], pre_media['Instagram'],
                 pre_media['X'], pre_media['VK']]
        end = []
        for k in media:
            if media_id in k:
                k.remove(media_id)
                end.append(k)
            else:
                end.append(k)
        upd = update(User).where(User.user_tg_id==user_id).values(subscriptions=await serialize_list({
            'Telegram': end[0],
            'Instagram': end[1],
            'X': end[2],
            'VK': end[3]
        }))
        s.execute(upd)
        s.commit()
    return True
    
    # комментарий
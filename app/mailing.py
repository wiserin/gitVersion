from aiogram.types import URLInputFile
from bot import bot
import asyncio
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.methods.send_media_group import SendMediaGroup
import app.database.requests as db
from app.parse.main_parser import parser
import asyncio

# Отвечает за рассылку
async def mailing():
    while True:
        try:
            # получение списка ссылок на ресурсы
            newsmakers = await db.get_newsmakers()

            # обработка каждого из них
            for newsmaker in newsmakers:
                # получение текста и ссылок на фото и видео
                new = await parser(newsmaker)


                if new:
                    # проверка актуальности текста новости
                    new_text = new['text']
                    state = await db.check_new_text(newsmaker, new)


                    if state:
                        # рассылка подписчикам
                        print(new)
                        name = await db.get_channel_name(newsmaker)
                        subscribers = await db.get_subscribers(newsmaker)

                        # только текст
                        if new['text'] != False and new['photo'] == False and new['video'] == False:
                            for subscriber in subscribers:
                                if len(new['text']) < 4000:
                                    await bot.send_message(subscriber, 
                                                        f'<a href="{newsmaker}">{name}</a>\n\n{new_text}', 
                                                        parse_mode='html')
                                else:
                                    s_text = await split_text(new_text, 4000)
                                    if len(s_text) < 4:

                                        await bot.send_message(subscriber,
                                                            f'<a href="{newsmaker}">{name}</a>\n\n{s_text[0]}',
                                                            parse_mode='html')
                                        await asyncio.sleep(0.1)
                                        
                                        for i in range (1, len(s_text)):
                                            await bot.send_message(subscriber,
                                                                f'<b>Продолжение текста</b>\n\n{s_text[i]}',
                                                                parse_mode='html')
                                            await asyncio.sleep(0.1)
                                    else:
                                        await bot.send_message(subscriber, 
                                                            f'<a href="{newsmaker}">{name}</a>\n\nТекст новости слишком длинный', 
                                                            parse_mode='html')
                                await asyncio.sleep(0.1)

                    

                        # Текст и медиа
                        elif (new['photo'] != False or new['video'] != False):
                            all_media = []

                            if new['photo']:
                                for i in new['photo']:
                                    all_media.append({'photo': i})

                            if new['video']:
                                for i in new['video']:
                                    all_media.append({'video': i})


                            if len(all_media) == 1:
                                media_type = list(all_media[0].keys())[0]
                                media = list(all_media[0].values())[0]
                            
                                if media_type == 'photo':
                                    for subscriber in subscribers:
                                        if len(new['text']) < 1020:
                                            await bot.send_photo(chat_id=subscriber,
                                                                photo=URLInputFile(media),
                                                                caption=f'<a href="{newsmaker}">{name}</a>\n\n{new_text if new_text else ""}',
                                                                parse_mode='html')
                                        else:
                                            s_text = await split_text(new_text, 1000)
                                            if len(s_text) < 4:

                                                await bot.send_photo(chat_id=subscriber,
                                                                photo=URLInputFile(media),
                                                                caption=f'<a href="{newsmaker}">{name}</a>\n\n{s_text[0]}',
                                                                parse_mode='html')
                                                
                                                await asyncio.sleep(0.1)
                                                
                                                for i in range (1, len(s_text)):
                                                    await bot.send_message(subscriber,
                                                                        f'<b>Продолжение текста</b>\n\n{s_text[i]}',
                                                                        parse_mode='html')
                                                    await asyncio.sleep(0.1)
                                            else:
                                                await bot.send_message(subscriber, 
                                                                    f'<a href="{newsmaker}">{name}</a>\n\nТекст новости слишком длинный', 
                                                                    parse_mode='html')
                                                await asyncio.sleep(0.1)

                                    
                                elif media_type == 'video':
                                    for subscriber in subscribers:
                                        if len(new['text']) < 1020:
                                            await bot.send_video(chat_id=subscriber,
                                                                video=URLInputFile(media),
                                                                caption=f'<a href="{newsmaker}">{name}</a>\n\n{new_text if new_text else ""}',
                                                                parse_mode='html')
                                        else:
                                            s_text = await split_text(new_text, 1000)
                                            if len(s_text) < 4:

                                                await bot.send_video(chat_id=subscriber,
                                                                video=URLInputFile(media),
                                                                caption=f'<a href="{newsmaker}">{name}</a>\n\n{new_text[0]}',
                                                                parse_mode='html')
                                                
                                                await asyncio.sleep(0.1)
                                                
                                                for i in range (1, len(s_text)):
                                                    await bot.send_message(subscriber,
                                                                        f'<b>Продолжение текста</b>\n\n{s_text[i]}',
                                                                        parse_mode='html')
                                                    await asyncio.sleep(0.1)
                                            else:
                                                await bot.send_message(subscriber, 
                                                                    f'<a href="{newsmaker}">{name}</a>\n\nТекст новости слишком длинный', 
                                                                    parse_mode='html')
                                                
                                        await asyncio.sleep(0.07)
                                    

                            else:
                                s_text = await split_text(new_text, 1000)
                                media_group = MediaGroupBuilder(caption=f'<a href="{newsmaker}">{name}</a>\n\n{new_text if len(s_text) == 1 else s_text[0]}')
                            
                                for media in all_media:
                                    type_ = list(media.keys())[0]
                                    item  = list(media.values())[0]
                                    media_group.add(type=type_, media=item, parse_mode='html')
                            

                                for subscriber in subscribers:
                                    if len(new['text']) < 1000:
                                        await bot.send_media_group(chat_id=subscriber,
                                                                media=media_group.build())
                                        
                                    else:
                                        if len(s_text) < 4:

                                            await bot.send_media_group(chat_id=subscriber,
                                                                media=media_group.build())
                                            await asyncio.sleep(0.1)
                                            
                                            for i in range (1, len(s_text)):
                                                await bot.send_message(subscriber,
                                                                    f'<b>Продолжение текста</b>\n\n{s_text[i]}',
                                                                    parse_mode='html')
                                                await asyncio.sleep(0.1)

                                        else:
                                            await bot.send_message(chat_id=subscriber,
                                                                text='Текст новости слишком длинный')
                                    await asyncio.sleep(0.1)

                        if new['text'] == False and new['photo'] == False and new['video'] == False:
                            for subscriber in subscribers:
                                await bot.send_message(subscriber, 
                                                    f'<a href="{newsmaker}">{name}</a>\n\nЭто сообщение не может быть отображено', 
                                                    parse_mode='html')
                                await asyncio.sleep(0.1)
                await asyncio.sleep(0.1)
            await asyncio.sleep(25)
            
        except Exception as e:
            print(e)




async def split_text(text: str, max_length: int):
    pre = text.split('\n')
    print(pre)
    response = []

    while len(pre) != 0:
        if len(pre) == 1:
            response.append(pre[0])
            pre.remove(pre[0])

        elif (len(pre[0]) + len(pre[1])) < max_length:
            new_str = f'{pre[0]}\n{pre[1]}'
            pre[0] = new_str
            pre.remove(pre[1])

        elif (len(pre[0]) + len(pre[1])) > max_length:
            response.append(pre[0])
            pre.remove(pre[0])

    return response



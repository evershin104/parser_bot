from database_interactions import *
from post_class import *
from new_posts_page import *
from stack_class import *
import config
import logging
import asyncio
import time
from datetime import date, timedelta
from aiogram import Bot, Dispatcher, executor, types

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)
stack = Stack()

# инициализируем соединение с БД
db = SQL_db('subscribed_users.db')
db.prepare_statuses()

posts_line = NewPosts()


# Обработка команлы старт. Если юзер в ДБ, то меняем статус
@dp.message_handler(commands=['start'])
async def subscribe(message: types.Message):
    if not db.subscriber_exists(message.from_user.id):
        await message.answer(
            'Твой ID - {0}! Пиши \info - там вся информация'.format(message.from_user.id))
    else:
        # Если он в БД - меняем статус в БД для отправки постов
        db.change_status(message.from_user.id, 1)
        await message.answer("Скоро пойдут логи")


# Обработка команды, если юзер в ДБ, меняем статус.
@dp.message_handler(commands=['stop'])
async def subscribe(message: types.Message):
    if db.subscriber_exists(message.from_user.id):
        db.change_status(message.from_user.id, 0)
        await message.answer('Stopped!')


# Краткая инфа вот так вот
@dp.message_handler(commands=['info'])
async def show_info(message: types.Message):
    await message.answer('info',
                         disable_web_page_preview=True)


# Краткая инфа для админа
@dp.message_handler(commands=['adm_info'])
async def show_adm_info(message: types.Message):
    if message.from_user.id in config.admins:
        await message.answer("/add XXXXXXXX - добавить юзера на неделю, вместо XXXXXXXX его ID\n"
                             "/delete XXXXXXXX - удалить юзера из подписки, вместо XXXXXXXX его ID\n"
                             "/text_all TEXT - рассылка всем подписанным юзерам\n"
                             "/stop_bot TEXT - остановка бота и рассылка TEXT\n"
                             "/all_users - вывод всех пользователей")


# Вывод всех юзеров
@dp.message_handler(commands=['all_users'])
async def show_users(message: types.Message):
    if message.from_user.id in config.admins:
        users = db.get_subscriptions()
        for user in users:
            await bot.send_message(message.from_user.id,
                                   'ID - {0}, Status - {1}, DateExp - {2}'.format(user[0], user[1], user[2]))
            time.sleep(0.5)


# Добавить юзера в ДБ (эт значит, что он подписался). Добавляем пока ручками
@dp.message_handler(commands=['add'])
async def add_user(message: types.Message):
    if message.from_user.id in config.admins:
        id = int(message.text.split(" ")[1])
        if not db.subscriber_exists(id):
            time = date.today() + timedelta(days=7)
            db.add_subscriber(id, False, time)
            await bot.send_message(id,
                                   "Подписка закончится {0}. Инструкция к боту: ссылка".format(
                                       time))
            await bot.send_message(config.log_chat_id,
                                   '@{0} added {1} until {2}'.format(message.from_user.username, id, time))
        else:
            end_date = db.find_user(id)[0][2]
            await bot.send_message(message.from_user.id, 'Юзер уже записан в ДБ до {0}'.format(end_date))
            await bot.send_message(config.log_chat_id, 'Try to write existing user {0} ({1}) by @{2}'
                                   .format(id, end_date, message.from_user.username))


# Удалить юзера из ДБ руками (автоматически это делается кадые сутки)
@dp.message_handler(commands=['delete'])
async def delete_user(message: types.Message):
    if message.from_user.id in config.admins:
        id = int(message.text.split(" ")[1])
        if db.subscriber_exists(id):
            db.delete_subscriber(id)
            await bot.send_message(id, "Удаление пользователя из БД, причина: окончание подписки")
            await bot.send_message(config.log_chat_id,
                                   '@{0} deleted {1} from DB'.format(message.from_user.username, id))
        else:
            await bot.send_message(config.log_chat_id,
                                   'Try to delete non-existing user {0} by @{1}'.format(id, message.from_user.username))


# Сделать рассылку всем подписанным пользователям
@dp.message_handler(commands=['text_all'])
async def text_all_subs(message: types.Message):
    if message.from_user.id in config.admins:
        text = message.text[10:len(message.text)]
        for user in db.get_subscriptions():
            await bot.send_message(user[0], text=text)
        await bot.send_message(config.log_chat_id,
                               '@{0} sent to all users: {1}'.format(message.from_user.username, text))


# Останавливает бот и отправляет всем сообщение
@dp.message_handler(commands=['stop_bot'])
async def stop_bot(message: types.Message):
    if message.from_user.id in config.admins:
        db.prepare_statuses()
        if message.text == "/stop_bot":
            text = "Бот выключен."
        else:
            text = message.text[10:len(message.text)]
        for user in db.get_subscriptions():
            await bot.send_message(user[0], text=text)
        await bot.send_message(config.log_chat_id,
                               '@{0} stopped the bot with text: {1}'.format(message.from_user.username, text))
        db.close()
        await bot.close()


# Рассылка новых постов
async def scheduled(wait_for):
    posts_line.parse_page()
    stack.add_urls_to_stack(posts_line.posts)
    while True:
        await asyncio.sleep(wait_for)
        if len(stack.current_urls) != 0:
            for link in reversed(stack.current_urls):
                # await bot.send_message(config.log_chat_id, 'Parsed {0}'.format(link))
                text = Post(link).generate_text()
                if text == "":
                    stack.current_urls.remove(link)
                    continue
                subscriptions = db.get_active_subs()
                for user in subscriptions:
                    await bot.send_message(user[0], text, disable_web_page_preview=True)
                time.sleep(5)
        posts_line.parse_page()
        stack.add_urls_to_stack(posts_line.posts)


# Удаляем с ДБ пользователей с просроченной подпиской
async def check_dates(wait_for):
    await asyncio.sleep(wait_for)
    for user in db.get_subscriptions():
        if user[2] == str(date.today()):
            db.delete_subscriber(user[0])
            await bot.send_message(user[0],
                                   'Срок подписки закончился')
            await bot.send_message(config.log_chat_id,
                                   '{0} was deleted due to the time of subscription'.format(user[0]))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(check_dates(86400))
    loop.create_task(scheduled(60))
    executor.start_polling(dp, skip_updates=True)

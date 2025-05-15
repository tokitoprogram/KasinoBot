import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram import F
import asyncio
from datetime import datetime, time, timedelta, timezone
import random, uuid, requests

def tranfer(user_id, asset, amount):
    spend_id = str(uuid.uuid4())
    headers = {
        "Crypto-Pay-API-Token":"",
        "Content-Type":"application/json"
    }
    data = {
        "user_id":user_id,
        "asset":asset,
        "amount":amount,
        "spend_id":spend_id
    }
    respose = requests.post("https://pay.crypt.bot/api/transfer", headers=headers, json=data)
    print(respose.json)
    return respose.json

def get_invoices():
    invoices = []
    headers = {
        "Crypto-Pay-API-Token":"",
        "Content-Type":"application/json"
    }

    requests_data = requests.post('https://pay.crypt.bot/api/getInvoices', headers=headers)


    if len(invoices)==0:

        for item in requests_data.json().get('result').get('items'):

            invoice_id = item.get('invoice_id')
            invoice_url = item.get('pay_url')
            invoice_status = item.get('status')
            invoice_userId =  # С бота берем айдишник пользователя
            invoice_data = {
                'invoice_id':invoice_id,
                'invoice_userId':invoice_userId, #invoice_id привязан к invoice_user
                'invoice_url':invoice_url,
                'invoice_status':invoice_status
            }
            invoices.append(invoice_data)
    else:
        for item in requests_data.json().get('result').get('items'):

            invoice_id = item.get('invoice_id')
            invoice_url = item.get('pay_url')
            invoice_status = item.get('status')
            invoice_userId =  # С бота берем айдишник пользователя
            invoice_data = {
                'invoice_id':invoice_id,
                'invoice_userId':invoice_userId, #invoice_id привязан к invoice_user
                'invoice_url':invoice_url,
                'invoice_status':invoice_status
            }
            invoices.append(invoice_data)


        # while item.get('invoice_id') != invoices
    return invoices

def create_invoices(asset, amount, invoice_userId):
    headers = {
        "Crypto-Pay-API-Token":"",
    }
    data = {
        "asset":asset,
        "amount": amount
    }
    requests_data = requests.post('https://pay.crypt.bot/api/createInvoice', headers=headers, data=data)
    invoice_id = requests_data.json().get('result').get('invoice_id')
    invoice_url = requests_data.json().get('result').get('pay_url')

    invoice_data = {
        'invoice_id':invoice_id,
        'invoice_userId':invoice_userId, #invoice_id привязан к invoice_user
        'invoice_url':invoice_url,

    }

    return invoice_data



moscow_tz = timezone(timedelta(hours=3))

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота и ID чатов
BOT_TOKEN = ""
ADMIN_CHAT_ID = ...   # Замените на ID администратора
GROUP_CHAT_ID = ... # Замените на ID группы

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Словари для хранения данных пользователей и выбранных чисел
user_data = {}
selected_numbers = set()
invoice_data = {}
# Проверка времени для ставок



def is_bet_time():
    """Проверяет, находится ли текущее время в диапазоне разрешенных ставок."""

    now = datetime.now(timezone(timedelta(hours=3))).time()
    return time(9, 0) <= now <= time(22, 0)

# Преобразование текста в перечеркнутую версию
def strike(text):
    result = ""
    for c in text:
        result = result + c + "\u0336"
    return result
def main_kb():
    kb_list = [
        [KeyboardButton(text="/start" )],
        [KeyboardButton(text="/choose")],
        [KeyboardButton(text="Проверить оплату")]
    ]

    keyboard = ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True)
    return keyboard

async def check_pay(message: types.Message, pay_link):
    import time
    import asyncio

    global user_data
    start_time = time.time() 
    while time.time() - start_time < 60: 

        if not invoice_data:
            await asyncio.sleep(2) 
            continue


        for invoice in get_invoices():
            if invoice.get('invoice_id') == invoice_data.get('invoice_id'):
                if invoice.get('invoice_status') == "paid":
                    user_id = message.from_user.id
                    user_data[user_id] = user_data.get(user_id, {})
                    user_data[user_id]["payment_confirmed"] = True

                    invoice_data.clear()
                    keyboard = generate_numbers_keyboard()
                    await bot.edit_message_text(
                        text="Выберите число для участия в розыгрыше:",
                        chat_id=pay_link.chat.id,
                        message_id=pay_link.message_id,
                        reply_markup=keyboard
                    )
                    return  

        await asyncio.sleep(4) 


    invoice_data.clear()
    await bot.edit_message_text('Время истекло, создайте новый платёж, /start',chat_id=pay_link.chat.id,message_id=pay_link.message_id)


def generate_numbers_keyboard():
    """Создает клавиатуру с числами от 1 до 100, разбивая их на строки по 10 чисел."""
    buttons = []
    for row_start in range(1, 101, 8):  # Числа начинаются с 1 до 100
        row_buttons = [
            InlineKeyboardButton(
                text="❌" if num in selected_numbers else str(num),
                callback_data=f"number_{num}" if num not in selected_numbers else "disabled",
            )
            for num in range(row_start, row_start + 8)
            if num <= 100
        ]
        buttons.append(row_buttons)
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard




# Хендлер команды /start
@dp.message(Command("start"))
async def start_command_handler(message: types.Message):

    """Обрабатывает команду /start."""
    global invoice_data    
    user_id = message.from_user.id
    if not is_bet_time():
        await message.answer("Ставки принимаются только с 10:00 до 21:00 по Москве. Попробуйте позже!")
    else:
        if  invoice_data:
            send_message = await message.answer("Вы больше не можете создавать платежи оплатите свой в течении 60 секунд")
            await asyncio.sleep(4)
            await message.delete()
            await bot.delete_message(chat_id=send_message.chat.id,message_id=send_message.message_id)
        elif user_id  in user_data:
            if "selected_number" in user_data[user_id] or "payment_confirmed" in user_data[user_id]:
                await message.answer("Вы уже выбрали число ожидайте конца розыгрыша")
        else:
            await message.answer(
                "🎰 Добро пожаловать в игру 'Джекпот каждый день'! 🎉\n\n"
                "💵 Сделай ставку, угадай число от 1 до 100 и получи шанс забрать 70% от всех ставок!\n\n"
                "👉 Чтобы сделать ставку нужно оплатить 1 USDT.\n"
                "✅ После подтверждения ты сможешь выбрать число для участия в розыгрыше!\n\n"
                "🛠 Команды:\n"

                "/choose - Выбрать число"
            )
            invoice_data = create_invoices("TON",1,message.from_user.id)              
            pay_link_message = await message.answer(f" Ссылка на платеж {invoice_data.get('invoice_url')}\n . Состояние платежа проверяеться каждые 10 секунд. Вы можете")
            asyncio.create_task(check_pay(message, pay_link_message)) 

    print(invoice_data)




    


       



# Хендлер команды /choose


# Хендлер для получения скриншота оплаты
 

# Команда для администратора для подтверждения оплаты


# Хендлер для выбора числа
@dp.callback_query(lambda callback: callback.data.startswith("number_"))
async def number_selection_handler(callback: types.CallbackQuery):
    """Обрабатывает выбор числа пользователем."""
    user_id = callback.from_user.id
    selected_number = int(callback.data.split("_")[1])

    # Проверяем, не выбрано ли уже это число
    if selected_number in selected_numbers:
        await callback.answer(f"Это число уже выбрано. Попробуйте другое.", show_alert=True)
        return

    # Проверяем, не выбрал ли пользователь уже число
    if user_id in user_data and "selected_number" in user_data[user_id]:
        await callback.answer("Вы уже выбрали число. Изменить выбор нельзя.", show_alert=True)
        return

    # Сохраняем выбор пользователя
    user_data[user_id]["selected_number"] = selected_number
    user_data[user_id]["username"] = callback.from_user.username or "пользователь"
    selected_numbers.add(selected_number)

    keyboard = generate_numbers_keyboard()
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer(f"Вы выбрали число {selected_number}. Удачи!")
    await callback.message.answer(f"Вы выбрали число {selected_number}. Удачи!")




# Команда для администратора для подтверждения оплаты



# Автоматический розыгрыш (происходит в 22:00 ежедневно)
async def daily_draw():
    """Ежедневный розыгрыш в 22:00."""
    global user_data, selected_numbers, invoice_data
    while True:
        now = datetime.now(timezone(timedelta(hours=3)))
        target_time = datetime.combine(now.date(), time(21, 00)).replace(tzinfo=moscow_tz)  
        if now > target_time:
            target_time += timedelta(days=1)
        sleep_duration = (target_time - now).total_seconds()
        await asyncio.sleep(sleep_duration)

        # Фильтруем только тех, кто выбрал число
        eligible_users = [
            user_id 
            for user_id, data in user_data.items() 
            if data.get("selected_number") is not None
        ]

        if eligible_users:
            # Выбираем случайного победителя из подходящих
            winner_id = random.choice(eligible_users)
            winner_info = f"@{user_data[winner_id].get('username', 'пользователь')} ({winner_id})"
            prize_amount = len(user_data)*0.7
            prize_amount_text = f"70% от всех ставок это {prize_amount}"

            print(user_data)
            print(winner_id)
            # Оповещение
            tranfer(winner_id, "TON", len(user_data)*0.7)
            await bot.send_message(winner_id, f"🎉 Поздравляем! Вы выиграли {prize_amount_text}! 🏆, Кол во участников {prize_amount} ")
            await bot.send_message(GROUP_CHAT_ID, f"🎊 Победитель: {winner_info}. Приз: {prize_amount_text}")
            await bot.send_message(ADMIN_CHAT_ID, f"Розыгрыш завершен. Победитель: {winner_info}")



            # Очистка данных
            user_data = {}
            selected_numbers.clear()
            invoice_data.clear()
            await bot.send_message(GROUP_CHAT_ID, "Розыгрыш завершен. Сделайте новую ставку для участия в следующем!")
        else:
            await bot.send_message(ADMIN_CHAT_ID, "Розыгрыш завершен, но участников не было.")

# Основная функция запуска
async def main():
    asyncio.create_task(daily_draw())


    print("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

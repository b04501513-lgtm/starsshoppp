import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
import json
import os
from datetime import datetime, timedelta

# --- CONFIG ---
BOT_TOKEN = os.getenv("8627903535:AAFMlMGPx60msH_5YYKKiTqTE9uVIZH7SRA")
ADMIN_ID = int(os.getenv("ADMIN_ID", "8058955962"))
CARD_NUMBER = os.getenv("CARD_NUMBER", "5614 6803 7065 8706")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "WarNexxxx")
SUPPORT_USERNAMES = ["WarNexxxx", "Sytik11"]

# --- NARXLAR ---
STAR_PRICES = {
    50: 11000,
    75: 16500,
    100: 22000,
    150: 33000,
    250: 55000,
    350: 77000,
    500: 110000,
    1000: 220000,
    2000: 440000,
    5000: 1100000,
}

PRICE_PER_STAR = 220

PREMIUM_PRICES = {
    3: 169990,
    6: 229990,
    12: 399990,
}

REFERRAL_REWARD_STARS = 10

# Bonus yechish miqdorlari
WITHDRAW_AMOUNTS = [75, 100, 125, 150]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# --- TRANSLATIONS ---
TEXTS = {
    "uz": {
        "welcome": "👋 <b>{name}</b>, Star Shop'ga xush kelibsiz!\n\n⭐ Stars va 💎 Premium eng arzon narxlarda!\n🚀 Qulay menyu orqali buyurtma bering:",
        "choose_lang": "🌐 Пожалуйста, выберите язык / Iltimos, tilni tanlang:",
        "lang_set": "✅ Til o'zbekchaga o'zgartirildi!",
        "main_menu": "🏠 Bosh menyu",
        "buy_stars": "⭐ Yulduz sotib olish",
        "rating": "🏆 Reyting",
        "buy_premium": "💎 Premium sotib olish",
        "my_orders": "📦 Buyurtmalarim",
        "referrals": "🔗 Referallar",
        "bonuses": "💰 Bonuslar",
        "ref_rating": "👥 Referallar reytingi",
        "contact": "📞 Bog'lanish",
        "settings": "⚙️ Sozlamalar",
        "stars_title": "⭐ <b>Telegram Stars sotib olish</b>\n\nObunani rasmiylashtirish uchun quyidagi variantlardan birini tanlang.",
        "premium_title": "💎 <b>Telegram Premium miqdorini tanlang</b>\n\n<i>Obunani rasmiylashtirish uchun quyidagi variantlardan birini tanlang.</i>",
        "back": "↩️ Orqaga",
        "back_main": "↩️ Bosh menyu",
        "custom_amount": "➕ Boshqa miqdor",
        "recipient_self": "👤 O'zimga",
        "confirm": "✅ Tasdiqlash",
        "no_orders": "📦 Sizda hali buyurtmalar yo'q.",
        "orders_title": "📦 <b>Sizning buyurtmalaringiz:</b>\n\n",
        "contact_text": "🛠️ <b>Star Shop qo'llab-quvvatlash xizmati</b>\n\n👨‍💼 Qo'llab-quvvatlash:\n@{s1}\n@{s2}\n\n⚡ Odatda juda tez javob beramiz.",
        "contact_btn": "📞 Qo'llab-quvvatlash bilan bog'lanish",
        "settings_text": "⚙️ <b>Sozlamalar</b>\n\n👤 Ism: {name}\n🆔 ID: <code>{uid}</code>\n📝 Username: @{uname}\n🌐 Til: O'zbekcha",
        "change_lang": "🌐 Tilni o'zgartirish",
        "bonus_text": "💰 <b>Bonus balansi</b>\n\n⭐ Stars bonuslari: <b>{stars} Stars</b>\n\nBonuslar referal tizimi orqali to'planadi.\nYechish uchun miqdorni tanlang:",
        "bonus_withdraw_all": "💫 Hammasini",
        "bonus_low": "❌ Minimal yechish: 10 Stars. Sizda: {stars} Stars",
        "bonus_withdraw_req": "💰 <b>Bonus Stars yechish</b>\n\nSizda: <b>{stars} ⭐ Stars</b>\nYechish summasi: <b>{amount} ⭐</b>\n\nYechish uchun @{admin} ga murojaat qiling.",
        "ref_text": "🔗 <b>Referal tizimi</b>\n\n👥 Taklif qilingan: <b>{count}</b>\n⭐ Har bir referal uchun: <b>{reward} Stars</b>\n\n🔗 Sizning havolangiz:\n<a href='{link}'>{link}</a>\n\n📋 <b>Qanday ishlaydi:</b>\n1. Havolani do'stlaringizga yuboring\n2. Ular botga kiradi\n3. Birinchi marta Stars sotib olganda\n4. Siz avtomatik <b>{reward} ⭐</b> olasiz\n\n💎 Bonus Stars: <b>{stars} ⭐</b>",
        "share_ref": "📤 Referalni ulashish",
        "withdraw_bonus": "💰 Bonuslarni yechish",
        "ref_rating_title": "👥 <b>Referallar reytingi - Umumiy</b>\n\n📊 Kim eng ko'p odam taklif qilgan (umumiy):\n\n",
        "ref_rating_today": "👥 <b>Referallar reytingi - Bugun</b>\n\n📊 Bugungi eng faol referalchilar:\n\n",
        "ref_rating_week": "👥 <b>Referallar reytingi - Hafta</b>\n\n📊 Haftalik eng faol referalchilar:\n\n",
        "ref_rating_month": "👥 <b>Referallar reytingi - Oy</b>\n\n📊 Oylik eng faol referalchilar:\n\n",
        "ref_my_place": "📍 Sizning o'rningiz: Referallar yo'q",
        "ref_my_place_n": "📍 Sizning o'rningiz: {place}-o'rin ({count} ta)",
        "no_data": "Hali ma'lumot yo'q.",
        "refresh": "🔄 Yangilash",
        "period_today": "✅ Bugun",
        "period_week": "Hafta",
        "period_month": "Oy",
        "period_all": "Barcha vaqt",
        "top_rating_title": "🏆 <b>Top foydalanuvchilar reytingi</b>\n\n",
        "custom_min": "❌ Minimal miqdor: 50 ⭐",
        "custom_num": "❌ Iltimos, faqat raqam kiriting!",
        "custom_prompt": "✏️ Nechta yulduz sotib olmoqchisiz?\n\nMinimal: 50 ⭐\nRaqamni kiriting:",
        "enter_username_prompt": "⭐ Telegram Stars: <b>{amount}</b>\n💵 Narx: <b>{price:,} UZS</b>\n\n❗ <code>@username</code> kiriting, agar o'zingiz uchun bo'lsa — quyidagi tugmani bosing",
        "order_confirm": "🛒 <b>Buyurtma tasdiqlash</b>\n\n📦 Xizmat: Telegram Stars\n⭐ Miqdor: {stars} ⭐\n👤 Qabul qiluvchi: {recipient}\n\n💰 To'lov summasi: <b>{price:,} UZS</b>\n🏦 To'lov rekvizitlari:\n<code>{card}</code>\n\n📌 To'lovni amalga oshirgandan so'ng chek skrinshotini shu yerga yuboring.\n⏰ Tasdiqlangandan keyin 1-3 daqiqa ichida xizmat faollashadi.",
        "order_created": "✅ Buyurtma <b>#{oid}</b> qabul qilindi!\n\n💳 To'lov rekvizitlari:\n<code>{card}</code>\n\n💰 To'lov summasi: <b>{price:,} UZS</b>\n\n📸 To'lovni amalga oshirgandan so'ng <b>chek skrinshotini</b> shu chatga yuboring!",
        "payment_received": "✅ Chekingiz qabul qilindi!\n⏳ Admin tomonidan tekshirilmoqda...\n1-3 daqiqa ichida faollashadi.",
        "prem_enter_username": "💎 Telegram Premium: <b>{months} oylik</b>\n💵 Narx: <b>{price:,} UZS</b>\n\n❗ <code>@username</code> kiriting, agar o'zingiz uchun bo'lsa — quyidagi tugmani bosing:",
        "prem_confirm": "🛒 <b>Buyurtma tasdiqlash</b>\n\n📦 Xizmat: Telegram Premium\n💎 Muddat: {months} oylik\n👤 Qabul qiluvchi: {recipient}\n\n💰 To'lov summasi: <b>{price:,} UZS</b>\n🏦 To'lov rekvizitlari:\n<code>{card}</code>\n\n📌 To'lovni amalga oshirgandan so'ng chek skrinshotini shu yerga yuboring.\n⏰ Tasdiqlangandan keyin 1-3 daqiqa ichida faollashadi.",
        "approved_msg": "✅ <b>Buyurtma #{oid} tasdiqlandi!</b>\n\n{emoji} Xizmat yuborildi. Rahmat! 🙏",
        "rejected_msg": "❌ <b>Buyurtma #{oid} rad etildi.</b>\n\nTo'lov tasdiqlanmadi. Iltimos, qayta urinib ko'ring yoki @{admin} bilan bog'laning.",
        "referral_joined": "🎉 Yangi referal! <b>{name}</b> sizning havolangiz orqali qo'shildi!\n\nUlar birinchi marta Stars sotib olganda siz <b>{reward} ⭐ Stars</b> olasiz!",
        "referral_reward": "🎉 <b>Referal mukofot!</b>\n\nSizning referal do'stingiz birinchi marta xarid qildi!\n✨ Hisobingizga <b>{reward} ⭐ Stars bonusi</b> qo'shildi!\n\nJami bonus Stars: <b>{total} ⭐</b>",
    },
    "ru": {
        "welcome": "👋 <b>{name}</b>, добро пожаловать в Star Shop!\n\n⭐ Stars и 💎 Premium по самым низким ценам!\n🚀 Сделайте заказ через удобное меню:",
        "choose_lang": "🌐 Пожалуйста, выберите язык / Iltimos, tilni tanlang:",
        "lang_set": "✅ Язык изменён на русский!",
        "main_menu": "🏠 Главное меню",
        "buy_stars": "⭐ Купить звёзды",
        "rating": "🏆 Рейтинг",
        "buy_premium": "💎 Купить Premium",
        "my_orders": "📦 Мои заказы",
        "referrals": "🔗 Рефералы",
        "bonuses": "💰 Бонусы",
        "ref_rating": "👥 Рейтинг рефералов",
        "contact": "📞 Связаться",
        "settings": "⚙️ Настройки",
        "stars_title": "⭐ <b>Купить Telegram Stars</b>\n\nВыберите один из вариантов для оформления подписки.",
        "premium_title": "💎 <b>Выберите срок Telegram Premium</b>\n\n<i>Выберите один из вариантов для оформления подписки.</i>",
        "back": "↩️ Назад",
        "back_main": "↩️ Главное меню",
        "custom_amount": "➕ Другое количество",
        "recipient_self": "👤 Себе",
        "confirm": "✅ Подтвердить",
        "no_orders": "📦 У вас ещё нет заказов.",
        "orders_title": "📦 <b>Ваши заказы:</b>\n\n",
        "contact_text": "🛠️ <b>Служба поддержки Star Shop</b>\n\n👨‍💼 Поддержка:\n@{s1}\n@{s2}\n\n⚡ Обычно отвечаем очень быстро.",
        "contact_btn": "📞 Связаться с поддержкой",
        "settings_text": "⚙️ <b>Настройки</b>\n\n👤 Имя: {name}\n🆔 ID: <code>{uid}</code>\n📝 Username: @{uname}\n🌐 Язык: Русский",
        "change_lang": "🌐 Сменить язык",
        "bonus_text": "💰 <b>Бонусный баланс</b>\n\n⭐ Stars бонусы: <b>{stars} Stars</b>\n\nБонусы накапливаются через реферальную систему.\nВыберите сумму для вывода:",
        "bonus_withdraw_all": "💫 Всё",
        "bonus_low": "❌ Минимальный вывод: 10 Stars. У вас: {stars} Stars",
        "bonus_withdraw_req": "💰 <b>Вывод бонусных Stars</b>\n\nУ вас: <b>{stars} ⭐ Stars</b>\nСумма вывода: <b>{amount} ⭐</b>\n\nДля вывода обратитесь к @{admin}.",
        "ref_text": "🔗 <b>Реферальная система</b>\n\n👥 Приглашено: <b>{count}</b>\n⭐ За каждого реферала: <b>{reward} Stars</b>\n\n🔗 Ваша ссылка:\n<a href='{link}'>{link}</a>\n\n📋 <b>Как работает:</b>\n1. Отправьте ссылку друзьям\n2. Они заходят через вашу ссылку\n3. При первой покупке Stars\n4. Вы автоматически получаете <b>{reward} ⭐</b>\n\n💎 Бонусные Stars: <b>{stars} ⭐</b>",
        "share_ref": "📤 Поделиться рефералом",
        "withdraw_bonus": "💰 Вывести бонусы",
        "ref_rating_title": "👥 <b>Рейтинг рефералов - Общий</b>\n\n📊 Кто пригласил больше всего (общий):\n\n",
        "ref_rating_today": "👥 <b>Рейтинг рефералов - Сегодня</b>\n\n📊 Самые активные рефереры сегодня:\n\n",
        "ref_rating_week": "👥 <b>Рейтинг рефералов - Неделя</b>\n\n📊 Самые активные рефереры за неделю:\n\n",
        "ref_rating_month": "👥 <b>Рейтинг рефералов - Месяц</b>\n\n📊 Самые активные рефереры за месяц:\n\n",
        "ref_my_place": "📍 Ваше место: Рефералов нет",
        "ref_my_place_n": "📍 Ваше место: {place}-е место ({count} чел.)",
        "no_data": "Данных пока нет.",
        "refresh": "🔄 Обновить",
        "period_today": "✅ Сегодня",
        "period_week": "Неделя",
        "period_month": "Месяц",
        "period_all": "Всё время",
        "top_rating_title": "🏆 <b>Рейтинг топ пользователей</b>\n\n",
        "custom_min": "❌ Минимальное количество: 50 ⭐",
        "custom_num": "❌ Пожалуйста, введите только цифры!",
        "custom_prompt": "✏️ Сколько звёзд хотите купить?\n\nМинимум: 50 ⭐\nВведите число:",
        "enter_username_prompt": "⭐ Telegram Stars: <b>{amount}</b>\n💵 Цена: <b>{price:,} UZS</b>\n\n❗ Введите <code>@username</code>, или нажмите кнопку ниже если для себя",
        "order_confirm": "🛒 <b>Подтверждение заказа</b>\n\n📦 Услуга: Telegram Stars\n⭐ Количество: {stars} ⭐\n👤 Получатель: {recipient}\n\n💰 Сумма: <b>{price:,} UZS</b>\n🏦 Реквизиты:\n<code>{card}</code>\n\n📌 После оплаты отправьте скриншот чека сюда.\n⏰ Активация в течение 1-3 минут.",
        "order_created": "✅ Заказ <b>#{oid}</b> принят!\n\n💳 Реквизиты:\n<code>{card}</code>\n\n💰 Сумма: <b>{price:,} UZS</b>\n\n📸 После оплаты отправьте <b>скриншот чека</b> в этот чат!",
        "payment_received": "✅ Ваш чек принят!\n⏳ Проверяется администратором...\n Активация в течение 1-3 минут.",
        "prem_enter_username": "💎 Telegram Premium: <b>{months} мес.</b>\n💵 Цена: <b>{price:,} UZS</b>\n\n❗ Введите <code>@username</code>, или нажмите кнопку ниже если для себя:",
        "prem_confirm": "🛒 <b>Подтверждение заказа</b>\n\n📦 Услуга: Telegram Premium\n💎 Срок: {months} мес.\n👤 Получатель: {recipient}\n\n💰 Сумма: <b>{price:,} UZS</b>\n🏦 Реквизиты:\n<code>{card}</code>\n\n📌 После оплаты отправьте скриншот чека сюда.\n⏰ Активация в течение 1-3 минут.",
        "approved_msg": "✅ <b>Заказ #{oid} подтверждён!</b>\n\n{emoji} Услуга отправлена. Спасибо! 🙏",
        "rejected_msg": "❌ <b>Заказ #{oid} отклонён.</b>\n\nОплата не подтверждена. Попробуйте снова или свяжитесь с @{admin}.",
        "referral_joined": "🎉 Новый реферал! <b>{name}</b> присоединился по вашей ссылке!\n\nКогда они купят Stars впервые — вы получите <b>{reward} ⭐ Stars</b>!",
        "referral_reward": "🎉 <b>Реферальный бонус!</b>\n\nВаш реферал впервые сделал покупку!\n✨ На ваш счёт начислено <b>{reward} ⭐ Stars</b>!\n\nВсего бонусных Stars: <b>{total} ⭐</b>",
    }
}

def t(lang, key, **kwargs):
    text = TEXTS.get(lang, TEXTS["uz"]).get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except:
            return text
    return text

# --- ORDERS DB ---
ORDERS_FILE = "orders.json"

def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_orders(orders):
    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)

def add_order(order: dict):
    orders = load_orders()
    orders.append(order)
    save_orders(orders)
    return len(orders)

def update_order_status(order_id: int, status: str):
    orders = load_orders()
    for o in orders:
        if o.get("id") == order_id:
            o["status"] = status
    save_orders(orders)

# --- USERS DB ---
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def get_or_create_user(user_id: int, username: str, full_name: str):
    users = load_users()
    uid = str(user_id)
    if uid not in users:
        users[uid] = {
            "id": user_id,
            "username": username,
            "full_name": full_name,
            "joined": datetime.now().isoformat(),
            "referrer": None,
            "balance_bonus": 0,
            "bonus_stars": 0,
            "orders_count": 0,
            "has_purchased": False,
            "lang": None,  # None = not chosen yet
        }
        save_users(users)
    return users[uid]

def get_user(user_id: int):
    users = load_users()
    return users.get(str(user_id))

def get_user_lang(user_id: int) -> str:
    user = get_user(user_id)
    if user and user.get("lang"):
        return user["lang"]
    return "uz"

def update_user(user_id: int, data: dict):
    users = load_users()
    uid = str(user_id)
    if uid in users:
        users[uid].update(data)
        save_users(users)

def get_referral_count(user_id: int, period: str = "all"):
    users = load_users()
    now = datetime.now()
    result = []
    for u in users.values():
        if str(u.get("referrer")) == str(user_id):
            if period == "all":
                result.append(u)
            else:
                joined = u.get("joined", "")
                try:
                    joined_dt = datetime.fromisoformat(joined)
                    if period == "today" and joined_dt.date() == now.date():
                        result.append(u)
                    elif period == "week" and joined_dt >= now - timedelta(days=7):
                        result.append(u)
                    elif period == "month" and joined_dt >= now - timedelta(days=30):
                        result.append(u)
                except:
                    pass
    return len(result)

# --- FSM STATES ---
class LangState(StatesGroup):
    choosing = State()

class OrderStates(StatesGroup):
    choosing_amount = State()
    entering_custom_amount = State()
    entering_username = State()
    waiting_payment = State()

class PremiumStates(StatesGroup):
    choosing_period = State()
    entering_username = State()
    waiting_payment = State()

class WithdrawState(StatesGroup):
    choosing_amount = State()

# --- KEYBOARDS ---
def lang_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang_ru"),
            InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="set_lang_uz"),
        ]
    ])

def main_menu_keyboard(lang="uz"):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "buy_stars"))],
            [KeyboardButton(text=t(lang, "rating")), KeyboardButton(text=t(lang, "buy_premium"))],
            [KeyboardButton(text=t(lang, "my_orders")), KeyboardButton(text=t(lang, "referrals")), KeyboardButton(text=t(lang, "bonuses"))],
            [KeyboardButton(text=t(lang, "ref_rating")), KeyboardButton(text=t(lang, "contact")), KeyboardButton(text=t(lang, "settings"))],
        ],
        resize_keyboard=True
    )

def star_amounts_keyboard(lang="uz"):
    buttons = []
    items = list(STAR_PRICES.items())
    for i in range(0, len(items), 2):
        row = []
        star1, price1 = items[i]
        row.append(InlineKeyboardButton(text=f"{star1} ⭐ - {price1:,} UZS", callback_data=f"stars_{star1}"))
        if i + 1 < len(items):
            star2, price2 = items[i + 1]
            row.append(InlineKeyboardButton(text=f"{star2} ⭐ - {price2:,} UZS", callback_data=f"stars_{star2}"))
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text=t(lang, "custom_amount"), callback_data="stars_custom")])
    buttons.append([InlineKeyboardButton(text=t(lang, "back"), callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def premium_keyboard(lang="uz"):
    buttons = []
    for months, price in PREMIUM_PRICES.items():
        label = f"{months} oy" if lang == "uz" else f"{months} мес."
        buttons.append([InlineKeyboardButton(text=f"{label} 💎 - {price:,} UZS", callback_data=f"premium_{months}")])
    buttons.append([InlineKeyboardButton(text=t(lang, "back"), callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def recipient_keyboard(lang="uz"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "recipient_self"), callback_data="recipient_self")],
        [InlineKeyboardButton(text=t(lang, "back"), callback_data="back_amounts")],
    ])

def premium_recipient_keyboard(lang="uz"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "recipient_self"), callback_data="prem_recipient_self")],
        [InlineKeyboardButton(text=t(lang, "back"), callback_data="back_premium")],
    ])

def confirm_order_keyboard(lang="uz"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "confirm"), callback_data="confirm_order")],
        [InlineKeyboardButton(text=t(lang, "back"), callback_data="back_recipient")],
    ])

def confirm_premium_keyboard(lang="uz"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "confirm"), callback_data="confirm_premium")],
        [InlineKeyboardButton(text=t(lang, "back"), callback_data="back_premium")],
    ])

def admin_order_keyboard(order_id: int, user_id: int, order_type: str = "stars"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"admin_approve_{order_id}_{user_id}_{order_type}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"admin_reject_{order_id}_{user_id}_{order_type}"),
        ]
    ])

def referral_keyboard(ref_link: str, lang="uz"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "share_ref"), url=f"https://t.me/share/url?url={ref_link}&text=Star%20Shop%20orqali%20arzon%20narxda%20Stars%20va%20Premium%20sotib%20oling!")],
        [InlineKeyboardButton(text=t(lang, "withdraw_bonus"), callback_data="withdraw_bonus")],
    ])

def ref_rating_keyboard(period="all", lang="uz"):
    periods = {
        "today": t(lang, "period_today") if period == "today" else ("Bugun" if lang == "uz" else "Сегодня"),
        "week": t(lang, "period_week") if period == "week" else ("Hafta" if lang == "uz" else "Неделя"),
        "month": t(lang, "period_month") if period == "month" else ("Oy" if lang == "uz" else "Месяц"),
        "all": ("✅ " + ("Barcha vaqt" if lang == "uz" else "Всё время")) if period == "all" else ("Barcha vaqt" if lang == "uz" else "Всё время"),
    }
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=periods["today"], callback_data="ref_period_today"),
            InlineKeyboardButton(text=periods["week"], callback_data="ref_period_week"),
            InlineKeyboardButton(text=periods["month"], callback_data="ref_period_month"),
        ],
        [InlineKeyboardButton(text=periods["all"], callback_data="ref_period_all")],
        [InlineKeyboardButton(text=t(lang, "refresh"), callback_data=f"ref_period_{period}")],
    ])

def bonus_withdraw_keyboard(lang="uz", stars=0):
    buttons = []
    row = []
    for amount in WITHDRAW_AMOUNTS:
        if amount <= stars:
            row.append(InlineKeyboardButton(text=f"{amount} ⭐", callback_data=f"withdraw_{amount}"))
        if len(row) == 4:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    if stars > 0:
        buttons.append([InlineKeyboardButton(text=t(lang, "bonus_withdraw_all"), callback_data=f"withdraw_{stars}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None

def contact_keyboard(lang="uz"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=t(lang, "contact_btn"),
            url=f"https://t.me/{SUPPORT_USERNAMES[0]}"
        )],
    ])

# --- HANDLERS ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    user = get_or_create_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.full_name
    )

    # Referral tekshirish
    args = message.text.split()
    if len(args) > 1:
        ref_param = args[1]
        ref_id = ref_param.replace("ref_", "") if ref_param.startswith("ref_") else ref_param
        if ref_id.isdigit() and ref_id != str(message.from_user.id) and not user.get("referrer"):
            update_user(message.from_user.id, {"referrer": ref_id})
            ref_lang = get_user_lang(int(ref_id))
            try:
                await bot.send_message(
                    int(ref_id),
                    t(ref_lang, "referral_joined", name=message.from_user.full_name, reward=REFERRAL_REWARD_STARS),
                    parse_mode="HTML"
                )
            except:
                pass

    # Agar til tanlanmagan bo'lsa
    if not user.get("lang"):
        await state.update_data(pending_start=True, pending_ref=args[1] if len(args) > 1 else None)
        await message.answer(t("uz", "choose_lang"), reply_markup=lang_keyboard())
        return

    lang = user.get("lang", "uz")
    await message.answer(
        t(lang, "welcome", name=message.from_user.full_name),
        reply_markup=main_menu_keyboard(lang),
        parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith("set_lang_"))
async def set_language(callback: types.CallbackQuery, state: FSMContext):
    lang = callback.data.replace("set_lang_", "")
    update_user(callback.from_user.id, {"lang": lang})
    await callback.message.delete()
    await callback.answer(t(lang, "lang_set"))
    await callback.message.answer(
        t(lang, "welcome", name=callback.from_user.full_name),
        reply_markup=main_menu_keyboard(lang),
        parse_mode="HTML"
    )

# ==================== STARS ====================

@dp.message(F.text.in_(["⭐ Yulduz sotib olish", "⭐ Купить звёзды"]))
async def buy_stars(message: types.Message, state: FSMContext):
    lang = get_user_lang(message.from_user.id)
    await state.set_state(OrderStates.choosing_amount)
    await message.answer(t(lang, "stars_title"), reply_markup=star_amounts_keyboard(lang), parse_mode="HTML")

@dp.callback_query(F.data.startswith("stars_"))
async def select_stars(callback: types.CallbackQuery, state: FSMContext):
    lang = get_user_lang(callback.from_user.id)
    data = callback.data.replace("stars_", "")

    if data == "custom":
        await state.set_state(OrderStates.entering_custom_amount)
        await callback.message.edit_text(
            t(lang, "custom_prompt"),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=t(lang, "back"), callback_data="back_amounts")]
            ])
        )
    else:
        amount = int(data)
        price = STAR_PRICES.get(amount, amount * PRICE_PER_STAR)
        await state.update_data(stars=amount, price=price)
        await state.set_state(OrderStates.entering_username)
        await callback.message.edit_text(
            t(lang, "enter_username_prompt", amount=amount, price=price),
            reply_markup=recipient_keyboard(lang),
            parse_mode="HTML"
        )
    await callback.answer()

@dp.message(OrderStates.entering_custom_amount)
async def enter_custom_amount(message: types.Message, state: FSMContext):
    lang = get_user_lang(message.from_user.id)
    try:
        amount = int(message.text.strip())
        if amount < 50:
            await message.answer(t(lang, "custom_min"))
            return
        price = amount * PRICE_PER_STAR
        await state.update_data(stars=amount, price=price)
        await state.set_state(OrderStates.entering_username)
        await message.answer(
            t(lang, "enter_username_prompt", amount=amount, price=price),
            reply_markup=recipient_keyboard(lang),
            parse_mode="HTML"
        )
    except ValueError:
        await message.answer(t(lang, "custom_num"))

@dp.callback_query(F.data == "recipient_self")
async def recipient_self(callback: types.CallbackQuery, state: FSMContext):
    lang = get_user_lang(callback.from_user.id)
    username = callback.from_user.username or callback.from_user.full_name
    await state.update_data(recipient=f"@{username}" if callback.from_user.username else username)
    data = await state.get_data()
    await show_order_confirmation(callback.message, data, lang)
    await callback.answer()

@dp.message(OrderStates.entering_username)
async def enter_username(message: types.Message, state: FSMContext):
    lang = get_user_lang(message.from_user.id)
    username = message.text.strip()
    if not username.startswith("@"):
        username = "@" + username
    await state.update_data(recipient=username)
    data = await state.get_data()
    await show_order_confirmation(message, data, lang)

async def show_order_confirmation(msg, data: dict, lang="uz"):
    text = t(lang, "order_confirm",
             stars=data['stars'],
             recipient=data['recipient'],
             price=data['price'],
             card=CARD_NUMBER)
    kb = confirm_order_keyboard(lang)
    if hasattr(msg, 'edit_text'):
        await msg.edit_text(text, reply_markup=kb, parse_mode="HTML")
    else:
        await msg.answer(text, reply_markup=kb, parse_mode="HTML")

@dp.callback_query(F.data == "confirm_order")
async def confirm_order(callback: types.CallbackQuery, state: FSMContext):
    lang = get_user_lang(callback.from_user.id)
    data = await state.get_data()
    order = {
        "id": None,
        "type": "stars",
        "user_id": callback.from_user.id,
        "username": callback.from_user.username or callback.from_user.full_name,
        "stars": data["stars"],
        "price": data["price"],
        "recipient": data["recipient"],
        "status": "pending",
        "created_at": datetime.now().isoformat(),
    }
    order_id = add_order(order)
    order["id"] = order_id

    try:
        await bot.send_message(
            ADMIN_ID,
            f"🆕 <b>YANGI BUYURTMA #{order_id}</b>\n\n"
            f"📦 Tur: ⭐ Stars\n"
            f"👤 Foydalanuvchi: @{order['username']} (ID: <code>{order['user_id']}</code>)\n"
            f"⭐ Miqdor: <b>{order['stars']} Stars</b>\n"
            f"👥 Qabul qiluvchi: <b>{order['recipient']}</b>\n"
            f"💰 Summa: <b>{order['price']:,} UZS</b>\n"
            f"🕐 Vaqt: {order['created_at'][:16]}",
            reply_markup=admin_order_keyboard(order_id, callback.from_user.id, "stars"),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Admin xabar yuborishda xato: {e}")

    await state.set_state(OrderStates.waiting_payment)
    await state.update_data(order_id=order_id)

    await callback.message.edit_text(
        t(lang, "order_created", oid=order_id, card=CARD_NUMBER, price=data['price']),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "back_main"), callback_data="back_main")]
        ]),
        parse_mode="HTML"
    )
    await callback.answer("✅")

@dp.message(OrderStates.waiting_payment, F.photo)
async def receive_stars_payment_proof(message: types.Message, state: FSMContext):
    lang = get_user_lang(message.from_user.id)
    data = await state.get_data()
    order_id = data.get("order_id", "?")

    await bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    await bot.send_message(
        ADMIN_ID,
        f"📸 Yuqoridagi chek — <b>#{order_id}</b>-buyurtma uchun\n"
        f"👤 @{message.from_user.username} (ID: <code>{message.from_user.id}</code>)",
        reply_markup=admin_order_keyboard(order_id, message.from_user.id, "stars"),
        parse_mode="HTML"
    )
    await message.answer(t(lang, "payment_received"), reply_markup=main_menu_keyboard(lang))
    await state.clear()

# ==================== PREMIUM ====================

@dp.message(F.text.in_(["💎 Premium sotib olish", "💎 Купить Premium"]))
async def buy_premium(message: types.Message, state: FSMContext):
    lang = get_user_lang(message.from_user.id)
    await state.set_state(PremiumStates.choosing_period)
    await message.answer(t(lang, "premium_title"), reply_markup=premium_keyboard(lang), parse_mode="HTML")

@dp.callback_query(F.data.startswith("premium_"))
async def select_premium(callback: types.CallbackQuery, state: FSMContext):
    lang = get_user_lang(callback.from_user.id)
    months = int(callback.data.replace("premium_", ""))
    price = PREMIUM_PRICES.get(months)
    await state.update_data(months=months, price=price)
    await state.set_state(PremiumStates.entering_username)
    await callback.message.edit_text(
        t(lang, "prem_enter_username", months=months, price=price),
        reply_markup=premium_recipient_keyboard(lang),
        parse_mode="HTML"
    )
    await callback.answer()

@dp.callback_query(F.data == "prem_recipient_self")
async def prem_recipient_self(callback: types.CallbackQuery, state: FSMContext):
    lang = get_user_lang(callback.from_user.id)
    username = callback.from_user.username or callback.from_user.full_name
    await state.update_data(recipient=f"@{username}" if callback.from_user.username else username)
    data = await state.get_data()
    await show_premium_confirmation(callback.message, data, lang)
    await callback.answer()

@dp.message(PremiumStates.entering_username)
async def enter_premium_username(message: types.Message, state: FSMContext):
    lang = get_user_lang(message.from_user.id)
    username = message.text.strip()
    if not username.startswith("@"):
        username = "@" + username
    await state.update_data(recipient=username)
    data = await state.get_data()
    await show_premium_confirmation(message, data, lang)

async def show_premium_confirmation(msg, data: dict, lang="uz"):
    text = t(lang, "prem_confirm",
             months=data['months'],
             recipient=data['recipient'],
             price=data['price'],
             card=CARD_NUMBER)
    kb = confirm_premium_keyboard(lang)
    if hasattr(msg, 'edit_text'):
        await msg.edit_text(text, reply_markup=kb, parse_mode="HTML")
    else:
        await msg.answer(text, reply_markup=kb, parse_mode="HTML")

@dp.callback_query(F.data == "confirm_premium")
async def confirm_premium_order(callback: types.CallbackQuery, state: FSMContext):
    lang = get_user_lang(callback.from_user.id)
    data = await state.get_data()
    order = {
        "id": None,
        "type": "premium",
        "user_id": callback.from_user.id,
        "username": callback.from_user.username or callback.from_user.full_name,
        "months": data["months"],
        "price": data["price"],
        "recipient": data["recipient"],
        "status": "pending",
        "created_at": datetime.now().isoformat(),
    }
    order_id = add_order(order)
    order["id"] = order_id

    try:
        await bot.send_message(
            ADMIN_ID,
            f"🆕 <b>YANGI BUYURTMA #{order_id}</b>\n\n"
            f"📦 Tur: 💎 Premium\n"
            f"👤 Foydalanuvchi: @{order['username']} (ID: <code>{order['user_id']}</code>)\n"
            f"💎 Muddat: <b>{order['months']} oylik</b>\n"
            f"👥 Qabul qiluvchi: <b>{order['recipient']}</b>\n"
            f"💰 Summa: <b>{order['price']:,} UZS</b>\n"
            f"🕐 Vaqt: {order['created_at'][:16]}",
            reply_markup=admin_order_keyboard(order_id, callback.from_user.id, "premium"),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Admin xabar yuborishda xato: {e}")

    await state.set_state(PremiumStates.waiting_payment)
    await state.update_data(order_id=order_id)

    await callback.message.edit_text(
        t(lang, "order_created", oid=order_id, card=CARD_NUMBER, price=data['price']),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "back_main"), callback_data="back_main")]
        ]),
        parse_mode="HTML"
    )
    await callback.answer("✅")

@dp.message(PremiumStates.waiting_payment, F.photo)
async def receive_premium_payment_proof(message: types.Message, state: FSMContext):
    lang = get_user_lang(message.from_user.id)
    data = await state.get_data()
    order_id = data.get("order_id", "?")

    await bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    await bot.send_message(
        ADMIN_ID,
        f"📸 Yuqoridagi chek — <b>#{order_id}</b>-buyurtma uchun (💎 Premium)\n"
        f"👤 @{message.from_user.username} (ID: <code>{message.from_user.id}</code>)",
        reply_markup=admin_order_keyboard(order_id, message.from_user.id, "premium"),
        parse_mode="HTML"
    )
    await message.answer(t(lang, "payment_received"), reply_markup=main_menu_keyboard(lang))
    await state.clear()

# ==================== ADMIN ====================

@dp.callback_query(F.data.startswith("admin_approve_"))
async def admin_approve(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Ruxsat yo'q!")
        return
    parts = callback.data.split("_")
    order_id = int(parts[2])
    user_id = int(parts[3])
    order_type = parts[4] if len(parts) > 4 else "stars"

    update_order_status(order_id, "approved")

    user = get_user(user_id)
    user_lang = get_user_lang(user_id)
    if user and not user.get("has_purchased") and user.get("referrer"):
        ref_id = user.get("referrer")
        ref_user = get_user(int(ref_id))
        if ref_user:
            new_stars = ref_user.get("bonus_stars", 0) + REFERRAL_REWARD_STARS
            update_user(int(ref_id), {"bonus_stars": new_stars})
            ref_lang = get_user_lang(int(ref_id))
            try:
                await bot.send_message(
                    int(ref_id),
                    t(ref_lang, "referral_reward", reward=REFERRAL_REWARD_STARS, total=new_stars),
                    parse_mode="HTML"
                )
            except:
                pass
        update_user(user_id, {"has_purchased": True})

    emoji = "⭐" if order_type == "stars" else "💎"
    await bot.send_message(
        user_id,
        t(user_lang, "approved_msg", oid=order_id, emoji=emoji),
        parse_mode="HTML"
    )
    await callback.message.edit_text(callback.message.text + "\n\n✅ <b>TASDIQLANDI</b>", parse_mode="HTML")
    await callback.answer("✅ Tasdiqlandi!")

@dp.callback_query(F.data.startswith("admin_reject_"))
async def admin_reject(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Ruxsat yo'q!")
        return
    parts = callback.data.split("_")
    order_id = int(parts[2])
    user_id = int(parts[3])

    update_order_status(order_id, "rejected")

    user_lang = get_user_lang(user_id)
    await bot.send_message(
        user_id,
        t(user_lang, "rejected_msg", oid=order_id, admin=ADMIN_USERNAME),
        parse_mode="HTML"
    )
    await callback.message.edit_text(callback.message.text + "\n\n❌ <b>RAD ETILDI</b>", parse_mode="HTML")
    await callback.answer("❌ Rad etildi!")

# ==================== MENU BUTTONS ====================

@dp.message(F.text.in_(["📦 Buyurtmalarim", "📦 Мои заказы"]))
async def my_orders(message: types.Message):
    lang = get_user_lang(message.from_user.id)
    orders = load_orders()
    user_orders = [o for o in orders if o.get("user_id") == message.from_user.id]
    if not user_orders:
        await message.answer(t(lang, "no_orders"))
        return
    text = t(lang, "orders_title")
    for o in user_orders[-10:][::-1]:
        status_emoji = {"pending": "⏳", "approved": "✅", "rejected": "❌"}.get(o.get("status", ""), "❓")
        if o.get("type") == "premium":
            detail = f"{o.get('months')} oy 💎 → {o.get('recipient')}"
        else:
            detail = f"{o.get('stars')} ⭐ → {o.get('recipient')}"
        text += (
            f"#{o.get('id', '?')} {status_emoji} | {detail}\n"
            f"💰 {o.get('price', 0):,} UZS | {o.get('created_at', '')[:10]}\n\n"
        )
    await message.answer(text, parse_mode="HTML")

@dp.message(F.text.in_(["🔗 Referallar", "🔗 Рефералы"]))
async def referrals(message: types.Message):
    lang = get_user_lang(message.from_user.id)
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={message.from_user.id}"
    ref_count = get_referral_count(message.from_user.id)
    user = get_user(message.from_user.id)
    bonus_stars = user.get("bonus_stars", 0) if user else 0

    await message.answer(
        t(lang, "ref_text", count=ref_count, reward=REFERRAL_REWARD_STARS, link=ref_link, stars=bonus_stars),
        reply_markup=referral_keyboard(ref_link, lang),
        parse_mode="HTML",
        disable_web_page_preview=True
    )

@dp.callback_query(F.data == "withdraw_bonus")
async def withdraw_bonus(callback: types.CallbackQuery):
    lang = get_user_lang(callback.from_user.id)
    user = get_user(callback.from_user.id)
    bonus_stars = user.get("bonus_stars", 0) if user else 0
    if bonus_stars < 10:
        await callback.answer(t(lang, "bonus_low", stars=bonus_stars), show_alert=True)
        return
    kb = bonus_withdraw_keyboard(lang, bonus_stars)
    await callback.message.answer(
        t(lang, "bonus_text", stars=bonus_stars),
        reply_markup=kb,
        parse_mode="HTML"
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("withdraw_"))
async def process_withdraw(callback: types.CallbackQuery):
    lang = get_user_lang(callback.from_user.id)
    amount_str = callback.data.replace("withdraw_", "")
    try:
        amount = int(amount_str)
    except:
        await callback.answer()
        return
    user = get_user(callback.from_user.id)
    bonus_stars = user.get("bonus_stars", 0) if user else 0

    await callback.message.edit_text(
        t(lang, "bonus_withdraw_req", stars=bonus_stars, amount=amount, admin=ADMIN_USERNAME),
        parse_mode="HTML"
    )
    await callback.answer()

@dp.message(F.text.in_(["💰 Bonuslar", "💰 Бонусы"]))
async def bonuses(message: types.Message):
    lang = get_user_lang(message.from_user.id)
    user = get_user(message.from_user.id)
    bonus_stars = user.get("bonus_stars", 0) if user else 0
    kb = bonus_withdraw_keyboard(lang, bonus_stars)
    await message.answer(
        t(lang, "bonus_text", stars=bonus_stars),
        reply_markup=kb,
        parse_mode="HTML"
    )

@dp.message(F.text.in_(["🏆 Reyting", "🏆 Рейтинг"]))
async def rating(message: types.Message):
    lang = get_user_lang(message.from_user.id)
    orders = load_orders()
    from collections import Counter
    user_counts = Counter(o.get("user_id") for o in orders if o.get("status") != "rejected")
    users = load_users()
    text = t(lang, "top_rating_title")
    medals = ["🥇", "🥈", "🥉"]
    for i, (uid, count) in enumerate(user_counts.most_common(10), 1):
        user = users.get(str(uid), {})
        name = user.get("username") or user.get("full_name") or str(uid)
        medal = medals[i-1] if i <= 3 else f"{i}."
        text += f"{medal} @{name} — {count} ta buyurtma\n"
    if not user_counts:
        text += t(lang, "no_data")
    await message.answer(text, parse_mode="HTML")

@dp.message(F.text.in_(["👥 Referallar reytingi", "👥 Рейтинг рефералов"]))
async def referral_rating(message: types.Message):
    lang = get_user_lang(message.from_user.id)
    await show_ref_rating(message, "all", lang, message.from_user.id)

async def show_ref_rating(msg_or_cb, period: str, lang: str, user_id: int, edit=False):
    users = load_users()
    from collections import Counter
    now = datetime.now()

    def count_refs(referrer_id):
        cnt = 0
        for u in users.values():
            if str(u.get("referrer")) == str(referrer_id):
                if period == "all":
                    cnt += 1
                else:
                    joined = u.get("joined", "")
                    try:
                        jdt = datetime.fromisoformat(joined)
                        if period == "today" and jdt.date() == now.date():
                            cnt += 1
                        elif period == "week" and jdt >= now - timedelta(days=7):
                            cnt += 1
                        elif period == "month" and jdt >= now - timedelta(days=30):
                            cnt += 1
                    except:
                        pass
        return cnt

    ref_counts = {}
    for uid in users:
        c = count_refs(uid)
        if c > 0:
            ref_counts[uid] = c

    sorted_refs = sorted(ref_counts.items(), key=lambda x: x[1], reverse=True)

    period_key = {
        "all": "ref_rating_title",
        "today": "ref_rating_today",
        "week": "ref_rating_week",
        "month": "ref_rating_month",
    }.get(period, "ref_rating_title")

    text = t(lang, period_key)
    medals = ["🥇", "🥈", "🥉"]
    my_place = None
    for i, (uid, count) in enumerate(sorted_refs[:10], 1):
        user = users.get(uid, {})
        name = user.get("username") or user.get("full_name") or f"ID:{uid}"
        medal = medals[i-1] if i <= 3 else f"{i}."
        display = f"@{name}" if user.get("username") else name
        text += f"{medal} {display} - {count} ta odam\n"
        if str(uid) == str(user_id):
            my_place = (i, count)

    if not sorted_refs:
        text += t(lang, "no_data")

    # My place
    if my_place:
        text += f"\n{t(lang, 'ref_my_place_n', place=my_place[0], count=my_place[1])}"
    else:
        # check if user has any refs at all
        my_count = count_refs(user_id)
        if my_count == 0:
            text += f"\n{t(lang, 'ref_my_place')}"

    kb = ref_rating_keyboard(period, lang)

    if edit and hasattr(msg_or_cb, 'edit_text'):
        try:
            await msg_or_cb.edit_text(text, reply_markup=kb, parse_mode="HTML")
        except:
            await msg_or_cb.answer(text, reply_markup=kb, parse_mode="HTML")
    else:
        await msg_or_cb.answer(text, reply_markup=kb, parse_mode="HTML")

@dp.callback_query(F.data.startswith("ref_period_"))
async def ref_period_change(callback: types.CallbackQuery):
    lang = get_user_lang(callback.from_user.id)
    period = callback.data.replace("ref_period_", "")
    await show_ref_rating(callback.message, period, lang, callback.from_user.id, edit=True)
    await callback.answer()

@dp.message(F.text.in_(["📞 Bog'lanish", "📞 Связаться"]))
async def contact(message: types.Message):
    lang = get_user_lang(message.from_user.id)
    s1 = SUPPORT_USERNAMES[0]
    s2 = SUPPORT_USERNAMES[1]
    await message.answer(
        t(lang, "contact_text", s1=s1, s2=s2),
        reply_markup=contact_keyboard(lang),
        parse_mode="HTML"
    )

@dp.message(F.text.in_(["⚙️ Sozlamalar", "⚙️ Настройки"]))
async def settings(message: types.Message):
    lang = get_user_lang(message.from_user.id)
    uname = message.from_user.username or ("yo`q" if lang == "uz" else "нет")
    await message.answer(
        t(lang, "settings_text",
          name=message.from_user.full_name,
          uid=message.from_user.id,
          uname=uname),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "change_lang"), callback_data="change_lang")]
        ]),
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "change_lang")
async def change_lang(callback: types.CallbackQuery):
    await callback.message.answer(t("uz", "choose_lang"), reply_markup=lang_keyboard())
    await callback.answer()

# --- NAVIGATION ---
@dp.callback_query(F.data == "back_main")
async def back_main(callback: types.CallbackQuery, state: FSMContext):
    lang = get_user_lang(callback.from_user.id)
    await state.clear()
    await callback.message.delete()
    await callback.message.answer(t(lang, "main_menu"), reply_markup=main_menu_keyboard(lang))
    await callback.answer()

@dp.callback_query(F.data == "back_amounts")
async def back_amounts(callback: types.CallbackQuery, state: FSMContext):
    lang = get_user_lang(callback.from_user.id)
    await state.set_state(OrderStates.choosing_amount)
    await callback.message.edit_text(t(lang, "stars_title"), reply_markup=star_amounts_keyboard(lang), parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "back_premium")
async def back_premium(callback: types.CallbackQuery, state: FSMContext):
    lang = get_user_lang(callback.from_user.id)
    await state.set_state(PremiumStates.choosing_period)
    await callback.message.edit_text(t(lang, "premium_title"), reply_markup=premium_keyboard(lang), parse_mode="HTML")
    await callback.answer()

# ==================== ADMIN PANEL ====================

@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    orders = load_orders()
    users = load_users()
    pending = [o for o in orders if o.get("status") == "pending"]
    approved = [o for o in orders if o.get("status") == "approved"]
    total_revenue = sum(o.get("price", 0) for o in approved)
    await message.answer(
        f"🔧 <b>Admin panel</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{len(users)}</b>\n"
        f"📦 Jami buyurtmalar: <b>{len(orders)}</b>\n"
        f"⏳ Kutayotganlar: <b>{len(pending)}</b>\n"
        f"✅ Tasdiqlangan: <b>{len(approved)}</b>\n"
        f"💰 Jami daromad: <b>{total_revenue:,} UZS</b>\n\n"
        f"Buyruqlar:\n/stats — batafsil statistika",
        parse_mode="HTML"
    )

@dp.message(Command("stats"))
async def stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    orders = load_orders()
    users = load_users()
    total_revenue = sum(o.get("price", 0) for o in orders if o.get("status") == "approved")
    stars_orders = [o for o in orders if o.get("type") == "stars"]
    premium_orders = [o for o in orders if o.get("type") == "premium"]
    await message.answer(
        f"📊 <b>Batafsil Statistika</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{len(users)}</b>\n"
        f"📦 Jami buyurtmalar: <b>{len(orders)}</b>\n"
        f"  ⭐ Stars: <b>{len(stars_orders)}</b>\n"
        f"  💎 Premium: <b>{len(premium_orders)}</b>\n\n"
        f"✅ Tasdiqlangan: <b>{len([o for o in orders if o.get('status') == 'approved'])}</b>\n"
        f"❌ Rad etilgan: <b>{len([o for o in orders if o.get('status') == 'rejected'])}</b>\n"
        f"⏳ Kutilmoqda: <b>{len([o for o in orders if o.get('status') == 'pending'])}</b>\n\n"
        f"💰 Jami daromad: <b>{total_revenue:,} UZS</b>",
        parse_mode="HTML"
    )

async def main():
    logger.info("Bot ishga tushmoqda...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

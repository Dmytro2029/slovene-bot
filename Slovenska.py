import logging
import os
import sqlite3
import random
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Инициализация БД
def init_db():
    conn = sqlite3.connect("slovene_bot.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            level INTEGER DEFAULT 1,
            score INTEGER DEFAULT 0,
            last_active TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS homework (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            questions TEXT,
            answers TEXT,
            is_checked BOOLEAN DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Клавиатура
def get_main_keyboard():
    return ReplyKeyboardMarkup([
        ["/start", "/task"],
        ["/homework", "/progress"]
    ], resize_keyboard=True)

# Словарь
VOCABULARY = {
    "jabolko": "яблоко",
    "kruh": "хлеб",
    "mleko": "молоко",
    "voda": "вода",
    "meso": "мясо",
    "pes": "собака",
    "mačka": "кошка",
    "hiša": "дом",
    "miza": "стол",
    "knjiga": "книга",
    "šola": "школа",
    "učitelj": "учитель",
    "dan": "день",
    "noč": "ночь",
    "lahko noč": "спокойной ночи",
    "dobro jutro": "доброе утро",
    "dober dan": "добрый день",
    "hvala": "спасибо",
    "prosim": "пожалуйста",
    "kako si?": "как дела?",
    "dobro": "хорошо",
    "slabo": "плохо",
    "ime": "имя",
    "kaj": "что",
    "kje": "где",
    "zakaj": "почему",
    "Я голоден": "Sem lačen",
    "Я голодна": "Sem lačna",
    "Я хочу есть": "Hočem jesti",
    "Меня зовут Полина": "Ime mi je Polina",
    "Я из Украины": "Sem iz Ukrajine",
    "Я голоден": "Sem lačen",
    "Я голодна": "Sem lačna",
    "Я хочу есть": "Hočem jesti",
    "kdaj": "когда",
    "kako": "как",
    "jaz sem": "я есть",
    "Voznik pozorno spremlja cestne znake": "Водитель внимательно следит за дорожными знаками",
    "kruh": "хлеб",
    "mleko": "молоко",
    "voda": "вода",
    "meso": "мясо",
    "riba": "рыба",
    "V katerem času boš prišel?": "В какое время ты придешь?",
    "jajca": "яйца",
    "kava": "кофе",
    "čaj": "чай",
    "zelenjava": "овощи",
    "sadje": "фрукты",
    "testenine": "паста",
    "juha": "суп",
    "pica": "пицца",
    "Ko boš prišel, te bom čakal v dvorani": "Когда ты придёшь, я буду ждать тебя в зале.",
    "piščanec": "курица",
    "goveje meso": "говядина",
    "svinjsko meso": "свинина",
    "maslo": "масло",
    "marmelada": "джем",
    "jogurt": "йогурт",
    "muesli": "мюсли",
    "krompir": "картофель",
    "paradižnik": "помидор",
    "korenje": "морковь",
    "čebula": "лук",
    "kumara": "огурец",
    "solata": "салат",
    "jagoda": "клубника",
    "banana": "банан",
    "breskeva": "персик",
    "sliva": "слива",
    "grozdje": "виноград",
    "limona": "лимон",
    "oranža": "апельсин",
    "trgovina": "магазин",
    "supermarket": "супермаркет",
    "tržnica": "рынок",
    "pekarna": "пекарня",
    "mesnica": "мясная лавка",
    "ribarnica": "рыбный магазин",
    "lekarna": "аптека",
    "bolnica": "больница",
    "zdravstveni dom": "поликлиника",
    "zobozdravnik": "стоматолог",
    "šola": "школа",
    "vrtec": "детский сад",
    "fakulteta": "университет",
    "kino": "кинотеатр",
    "gledališče": "театр",
    "muzej": "музей",
    "galerija": "галерея",
    "restavracija": "ресторан",
    "kavarna": "кафе",
    "bar": "бар",
    "diskoteka": "клуб",
    "hotel": "отель",
    "pošta": "почта",
    "bankomat": "банкомат",
    "banka": "банк",
    "park": "парк",
    "igrišče": "детская площадка",
    "športni center": "спортивный центр",
    "bazen": "бассейн",
    "Dober dan!": "Добрый день!",
    "Zdravo!": "Привет!",
    "Kako si?": "Как дела?",
    "Hvala, dobro.": "Спасибо, хорошо.",
    "Slabo.": "Плохо.",
    "Nasvidenje!": "До свидания!",
    "Lahko noč!": "Спокойной ночи!",
    "Dobro jutro!": "Доброе утро!",
    "Pozdravljeni!": "Здравствуйте!",
    "Me veseli!": "Приятно познакомиться!",
    "Kako ti je ime?": "Как тебя зовут?",
    "Od kod si?": "Откуда ты?",
    "Koliko stane?": "Сколько стоит?",
    "Kje je...?": "Где находится...?",
    "Kdaj odpre?": "Когда открывается?",
    "Kdaj zapre?": "Когда закрывается?",
    "Zakaj?": "Почему?",
    "Kako?": "Как?",
    "Kateri?": "Какой?",
    "Ali lahko pomagate?": "Вы можете помочь?",
    "Kje je letališče?": "Где аэропорт?",
    "Kje je avtobusna postaja?": "Где автобусная остановка?",
    "Kje je vlak?": "Где поезд?",
    "Kje je postaja?": "Где станция?",
    "Kako pridem do...?": "Как добраться до...?",
    "Kje lahko najem avto?": "Где арендовать машину?",
    "Kje je hotel?": "Где отель?",
    "Kje je turistični center?": "Где туристический центр?",
    "Kje lahko kupim karto?": "Где купить билет?",
    "Kdaj odpelje vlak?": "Когда отправляется поезд?",
    "Ali lahko dobim jedilni list?": "Можно меню?",
    "Bi priporočili kaj?": "Что посоветуете?",
    "Rad bi jedel...": "Я хотел бы...",
    "Račun, prosim.": "Счёт, пожалуйста.",
    "Je brezglutensko?": "Это без глютена?",
    "Imate vegetarijansko hrano?": "У вас есть вегетарианская еда?",
    "Ali je to pekoče?": "Это острое?",
    "Lahko dobim vodo?": "Можно воды?",
    "Hvala za postrežbo!": "Спасибо за обслуживание!",
    "Jed je bila odlična!": "Еда была отличной!",
    "Koliko stane?": "Сколько стоит?",
    "Imate to v drugi barvi?": "Есть это в другом цвете?",
    "Lahko probam?": "Можно примерить?",
    "Kje so garderobe?": "Где примерочные?",
    "Ali lahko plačam s kartico?": "Можно оплатить картой?",
    "Ali imate popust?": "У вас есть скидка?",
    "Bi lahko zavili kot darilo?": "Можно упаковать как подарок?",
    "Ne potrebujem vrečke.": "Мне не нужен пакет.",
    "Hvala, lep dan!": "Спасибо, хорошего дня!",
    "Kje je blagajna?": "Где касса?",
    "jaz sem": "я есть",
    "ti si": "ты есть",
    "on je": "он есть",
    "ona je": "она есть",
    "mi smo": "мы есть",
    "vi ste": "вы есть",
    "oni so": "они есть",
    "Pomagajte!": "Помогите!",
    "Pokličite policijo!": "Вызовите полицию!",
    "Pokličite rešilca!": "Вызовите скорую!",
    "Kje je bolnica?": "Где больница?",
    "Izgubil sem se.": "Я потерялся.",
    "Ukradli so mi denarnico.": "У меня украли кошелёк.",
    "Potrebujem zdravniško pomoč.": "Мне нужна медицинская помощь.",
    "Kje je najbližja lekarna?": "Где ближайшая аптека?",
    "Ali govorite angleško?": "Вы говорите по-английски?",
    "Ne razumem.": "Я не понимаю.",
    "Čas hitro teče": "Время идет быстро",
    "On gre v trgovino": "Он идет в магазин",
    "On bo doma jutri": "Он будет дома завтра",
    "Kaj bo naredil on?": "Что будет делать он?",
    "Kdaj boš prišel?": "Когда ты придёшь?",
    "Jabolko jem za zajtrk": "Я съем яблоко на завтрак",
    "Kruh je dober.": "Хлеб хороший.",
    "Kruh ni star.": "Хлеб не старый.",
    "To je moj kruh.": "Это мой хлеб.",
    "Kje je kruh?": "Где хлеб?",
    "Kruh je tukaj.": "Хлеб здесь.",
    "To ni kruh.": "Это не хлеб.",
    "Dva kruha sta na mizi.": "Два хлеба на столе.",
    "Mleko je belo.": "Молоко белое.",
    "Mleko ni vroče.": "Молоко не горячее.",
    "To je mleko.": "Это молоко.",
    "To ni mleko.": "Это не молоко.",
    "Mleko je v steklenici.": "Молоко в бутылке.",
    "Kje je mleko?": "Где молоко?",
    "Voda je mrzla.": "Вода холодная.",
    "Voda ni topla.": "Вода не тёплая.",
    "To je moja voda.": "Это моя вода.",
    "To ni voda.": "Это не вода.",
    "Voda je v kozarcu.": "Вода в стакане.",
    "Kje je voda?": "Где вода?",
    "Meso je okusno.": "Мясо вкусное.",
    "Meso ni surovo.": "Мясо не сырое.",
    "To je meso.": "Это мясо.",
    "To ni meso.": "Это не мясо.",
    "Meso je na krožniku.": "Мясо на тарелке.",
    "Kje je meso?": "Где мясо?",
    "Dve mesi sta mehki.": "Два куска мяса мягкие.",
    "To je toplo mleko.": "Это тёплое молоко.",
    "To ni moj kruh.": "Это не мой хлеб.",
    "To mleko ni moje.": "Это молоко не моё.",
    "To meso je za psa.": "Это мясо для собаки."
}

# Генерация задания
def generate_task():
    word, translation = random.choice(list(VOCABULARY.items()))
    if random.choice([True, False]):
        return {
            "type": "slovene_to_russian",
            "question": f"Переведи на русский: {word}",
            "answer": translation.lower()
        }
    else:
        return {
            "type": "russian_to_slovene",
            "question": f"Переведи на словенский: {translation}",
            "answer": word.lower()
        }

# Команды
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    conn = sqlite3.connect("slovene_bot.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO users (user_id, username, last_active)
        VALUES (?, ?, ?)
    """, (user.id, user.username, datetime.now().isoformat()))
    conn.commit()
    conn.close()

    await update.message.reply_text(
        "🇸🇮 Добро пожаловать в бота для изучения словенского языка!\n\n"
        "/task - задание\n"
        "/homework - домашка\n"
        "/progress - ваш прогресс",
        reply_markup=get_main_keyboard()
    )

async def daily_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    task = generate_task()
    context.user_data["current_task"] = task
    await update.message.reply_text(
        f"📝 Задание:\n{task['question']}",
        reply_markup=get_main_keyboard()
    )

async def homework(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    tasks = [generate_task() for _ in range(4)]
    questions = [t["question"] for t in tasks]
    answers = [t["answer"] for t in tasks]

    conn = sqlite3.connect("slovene_bot.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO homework (user_id, questions, answers)
        VALUES (?, ?, ?)
    """, (user_id, "\n".join(questions), "\n".join(answers)))
    conn.commit()
    conn.close()

    context.user_data["current_homework"] = answers

    await update.message.reply_text(
        "📚 Домашка. Ответьте на все задания одним сообщением, по одному на строке:\n\n" +
        "\n".join(questions),
        reply_markup=get_main_keyboard()
    )

async def progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conn = sqlite3.connect("slovene_bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT score FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()

    score = result[0] if result else 0
    level = min(6, score // 100 + 1)

    await update.message.reply_text(
        f"📊 Прогресс:\n\nБаллы: {score}\nУровень: {level}",
        reply_markup=get_main_keyboard()
    )

# Обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()
    user_id = update.effective_user.id

    if "current_homework" in context.user_data:
        answers = context.user_data["current_homework"]
        user_lines = [line.strip().lower() for line in text.split("\n") if line.strip()]
        if len(user_lines) != len(answers):
            await update.message.reply_text(
                "⚠️ Пожалуйста, ответьте **ровно на все вопросы**, по одному в строке.",
                reply_markup=get_main_keyboard()
            )
            return

        correct_count = sum(1 for u, a in zip(user_lines, answers) if u == a)
        points = correct_count * 5

        conn = sqlite3.connect("slovene_bot.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET score = score + ? WHERE user_id = ?", (points, user_id))
        cursor.execute("UPDATE homework SET is_checked = 1 WHERE user_id = ? AND is_checked = 0", (user_id,))
        conn.commit()
        conn.close()

        feedback = []
        for i, (u, a) in enumerate(zip(user_lines, answers)):
            if u == a:
                feedback.append(f"{i+1}. ✅ {u}")
            else:
                feedback.append(f"{i+1}. ❌ {u} (нужно: {a})")

        await update.message.reply_text(
            "📋 Результаты домашки:\n\n" +
            "\n".join(feedback) +
            f"\n\n🏅 Итог: {correct_count} из {len(answers)} — +{points} баллов!",
            reply_markup=get_main_keyboard()
        )

        del context.user_data["current_homework"]

    elif "current_task" in context.user_data:
        task = context.user_data["current_task"]
        if text == task["answer"]:
            conn = sqlite3.connect("slovene_bot.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET score = score + 10 WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
            await update.message.reply_text("✅ Верно! +10 баллов!", reply_markup=get_main_keyboard())
        else:
            await update.message.reply_text(
                f"❌ Неверно. Правильный ответ: {task['answer']}",
                reply_markup=get_main_keyboard()
            )
        del context.user_data["current_task"]
    else:
        await update.message.reply_text(
            "ℹ️ Сначала используйте команду /task или /homework.",
            reply_markup=get_main_keyboard()
        )

# Запуск
def main():
    TOKEN = os.environ.get("7661086230:AAG8OBew5rI9emcVbJjWFHEymXAnq8vU9kY")
    if not TOKEN:
        raise RuntimeError("❌ Переменная окружения BOT_TOKEN не установлена.")

    app = ApplicationBuilder().token("7661086230:AAG8OBew5rI9emcVbJjWFHEymXAnq8vU9kY").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("task", daily_task))
    app.add_handler(CommandHandler("homework", homework))
    app.add_handler(CommandHandler("progress", progress))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()

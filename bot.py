#!/usr/bin/env python3
"""Telegram бот для адвент-календаря."""

import os
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Dict, Optional
from zoneinfo import ZoneInfo

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)

# Константы состояний
STATE_START = 1
STATE_END = 2

# Московское время
MOSCOW_TZ = ZoneInfo("Europe/Moscow")

@dataclass
class UserPlan:
    start_date: date
    end_date: date
    next_date: date
    # Дата, за которую последний раз реально был выдан подарок (по расписанию или вручную)
    last_gift_date: Optional[date] = None


def get_gift_text(gift_date: date) -> str:
    """Возвращает текст подарка для конкретной даты."""
    # 1 декабря
    if gift_date.month == 12 and gift_date.day == 1:
        return (
            "❝ Нет ничего лучше историй, рассказанных ветреной ночью, когда люди находят тёплое укрытие "
            "в холодном мире. ❞\n"
            "📚 Стивен Кинг.\n\n"
            "И как раз под эту цитату подойдет теплый и уютный ПЛЕДИК!! Сегодня, на тебе пару ссылочек "
            "на классные пледы:\n"
            "1. 🪼OZON -- https://www.ozon.ru/product/pled-novogodniy-100h140-sm-selecta-christmas-2639971387/"
            "?from=share_ios&perehod=smm_share_button_productpage_link\n"
            "2. 🦄WB -- https://www.wildberries.ru/catalog/583423660/detail.aspx?size=797534601\n"
            "3. 🐝Yandex Market -- https://market.yandex.ru/cc/8CfCY2"
        )

    # 2 декабря
    if gift_date.month == 12 and gift_date.day == 2:
        return (
            "❝Мысли похожи на вязание. Иногда они не вяжутся, а иногда пытаешься вязать свитер, "
            "но все равно получаются носки❝\n"
            "🎸Дубровка Олег\n\n"
            "И сегодня ты получаешь в подарочек.......... СВИТЕР!!!! Зима это самое время закутаться "
            "в своем свитре и пить горячий шоколад, так что выбери его:\n"
            "1. WB -- https://www.wildberries.ru/catalog/297557927/detail.aspx?size=452594941\n"
            "2. OZON -- https://ozon.ru/t/ba1x0uq\n"
            "3. Yandex Market -- https://market.yandex.ru/cc/8CfSXv"
        )

    # 25 декабря
    if gift_date.month == 12 and gift_date.day == 25:
        return (
            "❝ Пожелание «Счастливого Нового года!» чем дальше, тем больше означает триумф надежды над опытом. ❞\n"
            "🧑🏼 Роберт Орбен \n\n"
            "С Католическим рождеством!!!! Сегодня твой подарочек подойдет как раз всех поздравить -- "
            "рождественские и новогодние открытки!!\n"
            "1. Ozon -- https://www.ozon.ru/product/novogodnie-otkrytki-mini-nabor-otkrytok-na-novyy-god-2026-novogodniy-dekor-1256345396/"
            "?at=vQtrz4LzvCPVmnlkfz9G81Ds66N39Dfk0PoVyCo8JXB5 \n"
            "2. WB -- https://www.wildberries.ru/catalog/579276682/detail.aspx?size=792465280 \n"
            "3. Yandex Market -- https://market.yandex.ru/cc/8HyWG8"
        )

    # 26 декабря
    if gift_date.month == 12 and gift_date.day == 26:
        return (
            "❝ Нет лучшего утешения в старости, чем сознание того, что удалось всю силу молодости "
            "воплотить в творения, которые не стареют. ❞\n\n"
            "🎪 Артур Шопенгауэр\n\n"
            "Осталось 5 дней до Нового года!!! И нет ничего лучшего, чем сидеть с новогодним настроением, "
            "попивать какао и писать/рисовать в своем блокнотике♡\n"
            "1. WB --  https://www.wildberries.ru/catalog/8400256/detail.aspx?size=28490911 \n"
            "2. OZON -- https://www.ozon.ru/product/novogodniy-podarochnyy-nabor-6-bloknotov-dlya-detey-na-novyy-god-6-shtuk-30-listov-3200775112/"
            "?at=6WtZYM0YXI53GnEBTP9AqNLtEPLOMPfN42kDqHPQ9Gw1&from_sku=3200775112&oos_search=false \n"
            "3. Yandex Market -- https://market.yandex.ru/cc/8HyW5V"
        )

    # 27 декабря
    if gift_date.month == 12 and gift_date.day == 27:
        return (
            "❝ Невозможно найти счастье в себе, не попробовав его в объятиях хотя бы одного человека. ❞\n\n"
            "📚 Эльчин Сафарли. \n\n"
            "Осталось 4 дня до Нового года!!! И если у вас нет человека, которого вы можете обнять, "
            "обнимите мягкую игрушку✧\n"
            "1. Ozon -- https://www.ozon.ru/product/myagkaya-igrushka-playtown-medved-pekar-25-sm-2968654518/"
            "?at=pZtp3yy4QUW6wvqntvDj3NJsgOJ3Y0TO640GqhJ92E7Y \n"
            "2. WB -- https://www.wildberries.ru/catalog/297834630/detail.aspx?size=452998035 \n"
            "3. Yandex Market -- https://market.yandex.ru/cc/8HyoFt"
        )

    # 28 декабря
    if gift_date.month == 12 and gift_date.day == 28:
        return (
            "❝ Запахи имеют ту особенность, что навевают воспоминания о прошлом с его звуками и ароматами, "
            "несравнимыми с теми, что тебя окружают в настоящем. ❞\n\n"
            "📚 Лаура Эскивель. \n\n"
            "3 дня до Нового года!!! Урааа, теперь надо настроить муд под него, и с этим тебе помогут "
            "ароматические свечи!\n"
            "1. WB -- https://www.wildberries.ru/catalog/297834630/detail.aspx?size=452998035 \n"
            "2. Ozon -- https://ozon.ru/t/fArd3RG \n"
            "3. Yandex Market -- https://market.yandex.ru/cc/8HzGTw"
        )
    
    # 29 декабря
    if gift_date.month == 12 and gift_date.day == 29:
        return (
            "❝ Я должен был пить много чая, ибо без него не мог работать. Чай высвобождает те возможности,"
            " которые дремлют в глубине моей души. ❞\n\n"
            "📚 Лев Николаевич Толстой. \n\n"
            "ДВА ДНЯ ДО НОВОГО ГОДА!! Ура и чтобы отпраздновать это события, посади всех за чашечку чая :3 "
            "ароматические свечи!\n"
            "1. WB -- https://www.wildberries.ru/catalog/690979768/detail.aspx?size=943747644 \n"
            "2. OZON -- https://www.ozon.ru/product/nabor-novogodnih-kruzhek-lefard-shchelkunchik-305-ml-2-shtuki-farfor-1420785313/?at=79tn1yyGEcR92pXPuyP2g8KfPoVn7RtOzv2mGc5KpGW \n"
            "3. Yandex Merket -- https://market.yandex.ru/cc/8Kxm54"
        )
    # 30 декабря
    if gift_date.month == 12 and gift_date.day == 30:
        return (
            "❝ Снег...он ухитряется залететь даже в сны...даже в лето, "
            " потому что зима мне почему-то никогда не снится. ❞\n\n"
            "📚 Ольга Громыко. \n\n"
            "ОДИН ДЕНЬ ДО НОВОГО ГОДА!!! Надеюсь у каждого из нас есть снег сейчас,  "
            "даже если нет, в снежном шаре он будет круглый год!!\n"
            "1. WB -- https://www.wildberries.ru/catalog/187864053/detail.aspx?size=307883201 \n"
            "2. OZON -- https://ozon.ru/t/baEcZb1 \n"
            "3. Yandex Market -- https://market.yandex.ru/cc/8HzmdN"
        )
    # 31 декабря
    if gift_date.month == 12 and gift_date.day == 31:
        return (
            "УРАА, ЗАВТРА НОВЫЙ ГОД!!!!! ❝ Новый год. Время обещаний и веры в то, что с утра всё начнётся заново, "
            "станет лучше и счастливее. ❞\n\n"
            "📚 Януш Леон Вишневский. \n\n"
            "И для праздничного настроения — настоящая магия света ✨"  
            "Пусть в этот вечер вокруг будет тепло, уют и немного новогоднего волшебства!\n"
            "1. WB -- https://www.wildberries.ru/catalog/272518316/detail.aspx?size=420740421 \n"
            "2. OZON -- https://ozon.ru/t/ifPUFxK \n"
            "3. Yandex Market -- https://market.yandex.ru/cc/8KxzbG"
        )

    # Текст по умолчанию для остальных дней
    return f"Вот твой подарочек на {gift_date.strftime('%d.%m')}! 🎁"


def get_user_store(context: ContextTypes.DEFAULT_TYPE) -> Dict[int, UserPlan]:
    store = context.bot_data.setdefault("users", {})
    return store  # type: ignore[return-value]


def make_keyboard(prefix: str, days: range) -> InlineKeyboardMarkup:
    """Формируем клавиатуру с днями."""
    buttons = []
    row = []
    for d in days:
        row.append(InlineKeyboardButton(str(d), callback_data=f"{prefix}_{d}"))
        if len(row) == 7:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(buttons)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = make_keyboard("start", range(1, 32))
    await update.message.reply_text(
        "Приветик!! С наступающим :3 Выбери дату, с которой начнется твой адвент-календарь!",
        reply_markup=keyboard,
    )
    return STATE_START


async def pick_start_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    _, day_str = query.data.split("_")
    day = int(day_str)

    today = datetime.now(MOSCOW_TZ).date()
    year = today.year if today.month == 12 else today.year + 1
    start_dt = date(year, 12, day)

    context.user_data["start_date"] = start_dt

    await query.edit_message_text(
        "Отлично! Теперь, с сегодняшнего дня, каждый день в 12:00 по московскому времени будет приходить твой подарочек!! А теперь выбери конечную дату!",
        reply_markup=make_keyboard("end", range(24, 32)),
    )
    return STATE_END


def schedule_next_gift(
    context: ContextTypes.DEFAULT_TYPE, user_id: int, plan: UserPlan
) -> None:
    """Планируем отправку следующего подарка, если это нужно."""
    job_name = f"gift_{user_id}"
    if context.job_queue is None:
        return

    # Удаляем прошлую задачу пользователя
    for job in context.job_queue.get_jobs_by_name(job_name):
        job.schedule_removal()

    if plan.next_date > plan.end_date:
        return

    # Планируем на 12:00 по московскому времени
    # run_at = datetime.combine(plan.next_date, time(12, 0), tzinfo=MOSCOW_TZ)
    run_at = datetime.combine(plan.next_date, time(19, 20), tzinfo=MOSCOW_TZ)

    # Если время уже прошло сегодня, планируем на завтра в 12:00
    now = datetime.now(MOSCOW_TZ)
    if run_at <= now:
        # Если сегодняшнее время уже прошло, планируем на завтра
        tomorrow = plan.next_date + timedelta(days=1)
        if tomorrow > plan.end_date:
            return
        run_at = datetime.combine(tomorrow, time(12, 0), tzinfo=MOSCOW_TZ)
    
    context.job_queue.run_once(
        send_scheduled_gift,
        when=run_at,
        name=job_name,
        data={"user_id": user_id},
    )


async def send_scheduled_gift(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    if job is None or context.bot_data is None:
        return

    user_id = job.data["user_id"]
    users = get_user_store(context)
    plan: Optional[UserPlan] = users.get(user_id)
    if not plan:
        return

    # Отправляем подарок за текущую дату плана
    text = get_gift_text(plan.next_date)
    await context.bot.send_message(chat_id=user_id, text=text)

    plan.last_gift_date = plan.next_date
    plan.next_date = plan.next_date + timedelta(days=1)
    users[user_id] = plan
    schedule_next_gift(context, user_id, plan)


async def pick_end_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    _, day_str = query.data.split("_")
    end_day = int(day_str)

    start_dt: date = context.user_data["start_date"]
    year = start_dt.year
    end_dt = date(year, 12, end_day)

    if end_dt < start_dt:
        await query.edit_message_text(
            "Конечная дата не может быть раньше начальной. Выбери заново конец (24–31 декабря).",
            reply_markup=make_keyboard("end", range(24, 32)),
        )
        return STATE_END

    today = datetime.now(MOSCOW_TZ).date()
    users = get_user_store(context)

    next_date = max(start_dt, today)
    plan = UserPlan(start_date=start_dt, end_date=end_dt, next_date=next_date)
    users[query.from_user.id] = plan

    # Ответ пользователю - упрощенный текст
    await query.edit_message_text("Ураа! Твой адвент-календарь готов!")

    if start_dt <= today <= end_dt:
        # Отправляем подарок сразу и планируем следующие
        await context.bot.send_message(
            chat_id=query.from_user.id,
            text=get_gift_text(today),
        )
        plan.last_gift_date = today
        plan.next_date = today + timedelta(days=1)
    else:
        plan.next_date = next_date

    users[query.from_user.id] = plan
    schedule_next_gift(context, query.from_user.id, plan)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Диалог завершен. Напиши /start, чтобы начать заново.")
    return ConversationHandler.END


async def gift(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /gift — выдать или повторить подарок за сегодня."""
    users = get_user_store(context)
    user_id = update.effective_user.id if update.effective_user else None
    if user_id is None:
        return

    plan: Optional[UserPlan] = users.get(user_id)
    if not plan:
        await update.message.reply_text(
            "Похоже, ты ещё не настроил свой адвент-календарь. Напиши /start, чтобы выбрать даты!"
        )
        return

    today = datetime.now(MOSCOW_TZ).date()

    # Уже получен подарок за сегодня
    if plan.last_gift_date == today:
        await update.message.reply_text(
            "Сегодня ты уже получил свой подарок, вот повтор этого сообщения!\n\n"
            + get_gift_text(today)
        )
        return

    # Подарок за сегодня ещё не получен — выдаём его сейчас
    await update.message.reply_text(
        "Приветик!! Сегодня твой подарок еще не получен (он появляется сам в 12:00 по московскому времени). "
        "Вот он сейчас :3!!\n\n" + get_gift_text(today)
    )

    # Считаем этот подарок официальным "сегодняшним"
    plan.last_gift_date = today

    # Если по плану следующий подарок должен был прийти сегодня или раньше —
    # сдвигаем на завтра и обновляем задачу в очереди.
    if plan.next_date <= today:
        plan.next_date = today + timedelta(days=1)
        users[user_id] = plan
        schedule_next_gift(context, user_id, plan)
    else:
        users[user_id] = plan


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /help — список команд и поддержка."""
    await update.message.reply_text(
        "Похоже, тебе нужна помощь! Держи список всех команд и что они делают =)\n\n"
        "/start: запуск бота: ты сможешь выбрать дату, с которой начинается твой адвент-календарь "
        "и в этот же день начать получать сообщения!;\n"
        "/gift: бот присылает сегодняшнее сообщение либо, если ты уже получил(-а) его, предлагает подождать до завтра;\n"
        "/help: бот присылает список команд и их функционала, а также контакты службы поддержки;\n"
        "/time: бот предлагает установить время, по которому будет присылать сообщения.\n\n"
        "Если тебе всё ещё что-то непонятно, обратись в нашу службу поддержки, мы с радостью поможем! @rinOkia_3"
    )


async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /time — показать текущее московское время."""
    now_moscow = datetime.now(MOSCOW_TZ).strftime("%H:%M")
    await update.message.reply_text(f"Сейчас в Москве {now_moscow}")


def main() -> None:
    import asyncio

    # Используйте переменную окружения TELEGRAM_TOKEN.
    # Токен ниже оставлен для удобного локального прогона, замените его своим.
    token = os.environ.get(
        "TELEGRAM_TOKEN",
        "7678922998:AAHLQETAuuMRAW_8RWtpU8qzZhOMeD2z5EM",
    )

    # Создаём event loop вручную (для Python 3.14, где по умолчанию его нет)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    application = Application.builder().token(token).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            STATE_START: [CallbackQueryHandler(pick_start_date, pattern=r"^start_\d+$")],
            STATE_END: [CallbackQueryHandler(pick_end_date, pattern=r"^end_\d+$")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )
    application.add_handler(conv)

    # Дополнительные команды
    application.add_handler(CommandHandler("gift", gift))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("time", time_command))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

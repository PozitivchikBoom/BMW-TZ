import json
from aianalyzer import analyze_message
import csv
import matplotlib.pyplot as plt
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from dateutil import parser
import numpy as np

def is_broken_promise(msg_index, messages):
    """
    Перевіряє, чи після msg_index є хоч одне повідомлення від менеджера
    до кінця того ж дня.
    """
    msg = messages[msg_index]
    msg_time = parser.parse(msg["date"])
    end_of_day = msg_time.replace(hour=23, minute=59, second=59)

    for i in range(msg_index + 1, len(messages)):
        m = messages[i]
        author = m.get("from_id") or m.get("sender_id")
        if not author:
            continue
        t = parser.parse(m["date"])
        if t > end_of_day:
            break
        if author == msg.get("from_id") and m.get("text"):
            return True
    return False

def visualize_problems(problems):
    categories = {
        "Обіцянка не виконана": "broken_promise",
        "Нецензурна лексика": "profanity",
        "Негатив клієнта": "negative_feedback",
        "Менеджер ухиляється": "manager_evasive",
        "Погана консультація": "poor_consultation"
    }

    # --- 1. Загальний графік проблем по категоріях ---

    counts = Counter()
    for p in problems:
        if p.get("broken_promise"):
            counts["Обіцянка не виконана"] += 1
        for label, key in categories.items():
            if p["analysis"].get(key):
                counts[label] += 1

    if not counts:
        print("⚠️ Немає даних для побудови графіка.")
        return

    color_map = {
        "Обіцянка не виконана": "#FF6F61",
        "Нецензурна лексика": "#6B5B95",
        "Негатив клієнта": "#88B04B",
        "Менеджер ухиляється": "#F7CAC9",
        "Погана консультація": "#92A8D1"
    }

    labels = list(counts.keys())
    values = [counts[label] for label in labels]
    colors = [color_map.get(label, "gray") for label in labels]

    plt.figure(figsize=(10, 6))
    bars = plt.bar(labels, values, color=colors)
    plt.title("Аналіз проблемних повідомлень", fontsize=14)
    plt.xlabel("Категорії", fontsize=12)
    plt.ylabel("Кількість", fontsize=12)
    plt.xticks(rotation=25)

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height + 0.3, str(height),
                 ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig("analysis_report.png")
    plt.close()

    # --- 2. Графік проблем по чатах ---

    # Збір даних: для кожного чату рахуємо кількість проблем за категоріями
    chat_problems = defaultdict(lambda: Counter())

    for p in problems:
        chat = p.get("chat", "Unknown")
        if p.get("broken_promise"):
            chat_problems[chat]["Обіцянка не виконана"] += 1
        for label, key in categories.items():
            if p["analysis"].get(key):
                chat_problems[chat][label] += 1

    if not chat_problems:
        print("⚠️ Немає даних для графіка по чатах.")
        return

    chats = list(chat_problems.keys())
    chats.sort()
    category_list = list(categories.keys())
    category_list.insert(0, "Обіцянка не виконана")  # вставляємо у початок

    # Підготовка даних для stacked bar chart
    data = []
    for category in category_list:
        data.append([chat_problems[chat].get(category, 0) for chat in chats])

    ind = np.arange(len(chats))
    width = 0.6

    plt.figure(figsize=(12, 8))

    bottom = np.zeros(len(chats))
    for i, category in enumerate(category_list):
        plt.bar(ind, data[i], width, bottom=bottom, label=category, color=color_map.get(category, "gray"))
        bottom += np.array(data[i])

    plt.xlabel("Чати", fontsize=12)
    plt.ylabel("Кількість проблем", fontsize=12)
    plt.title("Розподіл проблем по чатах", fontsize=14)
    plt.xticks(ind, chats, rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()
    plt.savefig("analysis_by_chats.png")
    plt.close()

    print("📊 Графіки збережено у файлах analysis_report.png та analysis_by_chats.png")

def save_detailed_report(problems):
    with open("analysis_report_detailed.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Чат",
            "Дата",
            "Текст (короткий)",
            "Обіцянка",
            "Пропущена обіцянка",
            "Матюки",
            "Негативний відгук",
            "Погана консультація",
            "Ухильна поведінка менеджера"
        ])

        for p in problems:
            analysis = p["analysis"]
            text_short = p["text"][:100].replace("\n", " ")
            writer.writerow([
                p["chat"],
                p["date"],
                text_short,
                analysis.get("promise", False),
                p.get("broken_promise", False),
                analysis.get("profanity", False),
                analysis.get("negative_feedback", False),
                analysis.get("poor_consultation", False),
                analysis.get("manager_evasive", False),
            ])

def save_report(problems, filename="analysis_report.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Chat", "Date", "Message", "Promise", "Negative",
            "Evasive", "Poor Consultation", "Profanity", "Broken Promise"
        ])
        for p in problems:
            writer.writerow([
                p["chat"],
                p["date"],
                p["text"],
                p["analysis"]["promise"],
                p["analysis"]["negative_feedback"],
                p["analysis"]["manager_evasive"],
                p["analysis"]["poor_consultation"],
                p["analysis"]["profanity"],
                p.get("broken_promise", False)
            ])

def extract_text(msg):
    """
    Витягує текст з повідомлення, якщо він є.
    Якщо повідомлення мультимедійне, можна розширити логіку тут.
    """
    # Якщо є поле 'text' і воно рядок — повертаємо його
    text = msg.get("text")
    if isinstance(text, str):
        return text

    # Якщо є 'message' і це рядок (іноді історія може зберігати по-іншому)
    text = msg.get("message")
    if isinstance(text, str):
        return text

    # Тут можна додати обробку інших форматів, якщо треба

    return ""  # Порожній рядок, якщо тексту нема

def analyze_promises():
    with open("data/chat_history.json", encoding="utf-8") as f:
        history = json.load(f)

    problems = []

    for chat_id, chat_data in history.items():
        messages = chat_data.get("messages", [])
        for i, msg in enumerate(messages):
            text = extract_text(msg)
            if not text:
                continue

            analysis = analyze_message(text)

            # Перевірка на непродовжену обіцянку
            if analysis["promise"]:
                broken = not is_broken_promise(i, messages)
                if broken:
                    problems.append({
                        "chat": chat_data.get("name", "Unknown"),
                        "text": text,
                        "date": msg.get("date"),
                        "analysis": analysis,
                        "broken_promise": True
                    })
            elif any(analysis.values()):
                problems.append({
                    "chat": chat_data.get("name", "Unknown"),
                    "text": text,
                    "date": msg.get("date"),
                    "analysis": analysis,
                    "broken_promise": False
                })

    print(f"🔍 Виявлено {len(problems)} проблемних повідомлень:")
    for p in problems:
        print(f"- {p['chat']} | {p['date']} | {p['text']}")
        print(f"  Аналіз: {p['analysis']}")
    save_report(problems)
    print(f"Звіт збережено у файлі analysis_report.csv")
    save_report(problems)
    visualize_problems(problems)
    print(f"📊 Графік збережено у файлі analysis_report.png")
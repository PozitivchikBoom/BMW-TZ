def is_promise(message):
    if not message or len(message.strip()) < 10:
        return False

    message = message.lower()

    keywords = [
        "скину", "відправлю", "надішлю", "прорахунок", "зроблю", "дам відповідь",
        "напишу", "зателефоную", "передзвоню", "надішлемо", "вишлю", "обіцяю",
        "після обіду", "до вечора", "до кінця дня", "завтра"
    ]
    return any(kw in message for kw in keywords)

def is_negative_feedback(message):
    if not message:
        return False
    message = message.lower()
    negative_keywords = [
        "чому", "не отримав", "не працює", "де мій", "ви обіцяли",
        "скільки чекати", "мені не підходить", "погано", "не задоволений", "жах"
    ]
    return any(kw in message for kw in negative_keywords)

def is_manager_evasive(message):
    if not message:
        return False
    message = message.lower()
    evasive_phrases = [
        "не знаю", "напишу потім", "давай завтра", "може пізніше", "не впевнений", "попізніше"
    ]
    return any(kw in message for kw in evasive_phrases)

def is_poor_consultation(message):
    if not message:
        return False
    message = message.strip().lower()
    poor_responses = ["ок", "гуд", "зрозуміло", "ага", "добре", "так", "ні"]
    return message in poor_responses or len(message) <= 3

def analyze_message(message):
    return {
        "promise": is_promise(message),
        "negative_feedback": is_negative_feedback(message),
        "manager_evasive": is_manager_evasive(message),
        "poor_consultation": is_poor_consultation(message),
        "profanity": contains_profanity(message)
    }

def contains_profanity(message):
    if not message:
        return False

    message = message.lower()
    bad_words = [
        # 🇺🇦 українські
        "нах", "бля", "хуй", "пізд", "єб", "срака", "гівно", "дебіл", "ідіот", "тупий", "мудак", "мразь",
        # 🇷🇺 російські
        "пизд", "хуй", "еба", "бля", "муда", "сука", "гандон", "чмо", "мразь", "пидр", "лох", "еблан", "жопа", "гавно",
        "ублюдок", "шлюха", "тварь", "сволочь", "даун", "кретин", "долбо", "тупой", "идиот", "сраный",
        # розширення — фільтрація за коренями
        "fuck", "shit", "asshole", "bitch", "damn", "dick", "bastard", "faggot", "slut", "moron"
    ]

    return any(word in message for word in bad_words)
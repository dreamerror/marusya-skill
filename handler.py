import json


def remove_symbols(string: str):
    symbols = ".! (),?"
    for s in symbols:
        string = string.replace(s, "")
    return string


POSSIBLE_START_PHRASES = ["тупайвездеход", "тупайвездекод", "2pieвездекод",
                          "2pieвездеход", "twopieвездекод", "twopieвездеход",
                          "тупаявездекот", "тупайвездекот"]

QUESTIONS = {"Вы боитесь выйти на фронт?": "Вы боитесь выйти на ^фронт^? ",
             "Сумеете пропатчить KDE2 под FreeBSD?": "Сумеете проп`атчить КаДэЕ два под фри БэЭсДэ? "
                                                     "<speaker audio=marusia-sounds/animals-cuckoo-1>",
             "Вы любите интернет?": "Вы любите интернет? ",
             "У компьютеров есть глаза?": "У компьютеров есть ^глаза^? "
                                          "<speaker audio=marusia-sounds/human-walking-dead-3>",
             "А уши и голос?": "А уши и голос?",
             "Считаете ли вы, что считать — это весело?": "Считаете ли ^вы^, что считать это весело?",
             "Аббревиатура CSS для вас что-то значит?": "Аббревиатура СиЭсЭс для вас что-то значит?",
             "У вас есть 7000 кубков в Brawl Stars?": "У вас есть семь тысяч кубков в бравл старс? "
                                                      "<speaker audio=marusia-sounds/things-cuckoo-clock-1>"}

POSSIBLE_CATEGORIES = ["Backend", "Оптимизация и RL", "Web, VKMA", "Computer vision", "Маруся", "Анализ данных",
                       "Gamedev, Дизайн интерфейсов", "Мобильная разработка"]

POSSIBLE_CATEGORIES_TTS = ["Бэкэнд", "Оптимизация и ЭрЭл", "Вэб, ВэКа МиниАпс", "Компьютэр вижн", "Маруся",
                           "Анализ данных", "Геймдэв, дизайн интерфейсов", "Мобильная разработка"]


def hello_vezdekod(request):
    derived_session_fields = ['session_id', 'user_id', 'message_id']
    response_text = "Привет Вездек`одерам!"
    response_message = {
        "response": {
            "text": response_text,
            "tts": response_text,
            "end_session": False
        },
        "session": {derived_key: request['session'][derived_key] for derived_key in derived_session_fields},
        "version": request['version']
    }

    return {
        "statusCode": 200,
        "body": json.dumps(response_message)
    }


def quiz(request, is_start: bool, is_yes: bool):
    derived_session_fields = ['session_id', 'user_id', 'message_id']
    buttons = ["Да", "Нет"]
    i = request['state']['session']['questions'] if not is_start else 0
    categories = request['state']['session']['categories'] if not is_start else []
    if i > 7:
        result_message_start = ""
        result_message_start_tts = ""
        categories_text, categories_tts = [], []
        categories = categories[1::] + [int(is_yes)]
        for k in range(8):
            if int(categories[k]):
                categories_text.append(POSSIBLE_CATEGORIES[k])
                categories_tts.append(POSSIBLE_CATEGORIES_TTS[k])
        categories_tts = ', '.join(categories_tts)
        categories_text = ', '.join(categories_text)
        if sum(categories) == len(categories):
            result_message_start = "вам подходят все категории, а именно: "
            result_message_start_tts = "^вам^ подходят все категории, а именно — "
        elif sum(categories) == 0:
            result_message_start = "вам не подходит ни одна из представленных категорий, очень жаль("
            result_message_start_tts = "^вам^ не подходит ни одна из представленных категорий, очень ^жаль^"
        else:
            result_message_start = "вам подходят следующие категории: "
            result_message_start_tts = "^вам^ подходят следующие категории — "
        response_message = {
            "response": {
                "text": f"Согласно моим сложным математическим вычислениям, {result_message_start}{categories_text}",
                "tts": f"Согласно маим сложным математическим ^вычислениям^, "
                       f"{result_message_start_tts}: {categories_tts}",
                "end_session": False
            },
            "session": {derived_key: request['session'][derived_key] for derived_key in derived_session_fields},
            "version": request['version']
        }
    else:
        response_message = {
            "response": {
                "text": list(QUESTIONS.keys())[i],
                "tts": list(QUESTIONS.values())[i],
                "end_session": False,
            },
            "session": {derived_key: request['session'][derived_key] for derived_key in derived_session_fields},
            "version": request['version'],
            "session_state": {"questions": i+1, "categories": categories + [is_yes]}
        }
    return {
        "statusCode": 200,
        "body": json.dumps(response_message)
    }


def webhook(event, context):
    request_message = json.loads(event['body'])
    derived_session_fields = ['session_id', 'user_id', 'message_id']
    req_text = remove_symbols(request_message['request']['original_utterance'].lower())
    if req_text in POSSIBLE_START_PHRASES:
        return hello_vezdekod(request_message)
    if req_text in ('выборкатегории', 'да', 'нет'):
        return quiz(request_message, req_text == "выборкатегории", req_text == "да")
    response_message = {
        "response": {
            "text": "Я не знаю, что ответить!",
            "tts": "Я не знаю, что ответить!",
            "end_session": False
        },
        "session": {derived_key: request_message['session'][derived_key] for derived_key in derived_session_fields},
        "version": request_message['version']
    }

    return {
        "statusCode": 200,
        "body": json.dumps(response_message)
    }

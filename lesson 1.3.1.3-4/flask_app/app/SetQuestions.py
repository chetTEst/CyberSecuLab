# -*- cuding: utf-8 -*-
import random
import base64
from .models import db, CipherType, Questions
from . import app

random.seed()

def setQuestions():
    img_table = open("atbash.png", "rb")
    code_img_table_atbash = base64.b64encode(img_table.read()).decode('ascii')
    img_table.close()
    img_table = open("braile.PNG", "rb")
    code_img_table_braile = base64.b64encode(img_table.read()).decode('ascii')
    img_table.close()
    img_table = open("alphabet_morse.png", "rb")
    code_img_table_morse = base64.b64encode(img_table.read()).decode('ascii')
    img_table.close()

    def anagram(d):
        ans = d.strip()
        d_data = d.split()
        for i in range(len(d_data)):
            znak_p = False
            znak_p_str = ""
            if d_data[i][-1] == "," or d_data[i][-1] == ".":
                znak_p = True
                znak_p_str = d_data[i][-1]
                d_data[i] = d_data[i][:-1]
            list_d_data = list(d_data[i])
            random.shuffle(list_d_data)
            if znak_p:
                list_d_data.append(znak_p_str)
            d_data[i] = "".join(list_d_data)
        return "Перед вами простой шифр с анаграммой: <b>{0}</b><br/>Расшифруйте его и запишите ответ, соблюдая знаки препинания.".format(
                " ".join(d_data))

    def cesar(message, n, decrypt=True):
        alphabet = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'
        newMessage = ''
        key = n
        for character in message:
            if character in alphabet:
                position = alphabet.find(character)
                newPosition = (position + key) % 32
                newCharacter = alphabet[newPosition]
                newMessage += newCharacter
            else:
                newMessage += character
        if decrypt:
            return "Вам необходимо <b>расшифровать</b> сообщение <br/><b>{0}</b><br/>используя шифр Цезаря, c ключом <i><b>{1}</b></i>.</br>Используй алфавит: абвгдежзийклмнопрстуфхцчшщъыьэюя".format(
        newMessage, n)
        else:
            return "Вам необходимо <b>зашифровать</b> сообщение <br/><b>{0}</b><br/>используя шифр Цезаря, c ключом <i><b>{1}</b></i>.</br>Используй алфавит: абвгдежзийклмнопрстуфхцчшщъыьэюя".format(
        message, n), newMessage

    def atbash(message, code_img_table, decrypt=True):
        alphabet = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'
        newalphabet = 'яюэьыъщшчцхфутсрпонмлкйизжедгвба'
        newMessage = ''
        for character in message:
            if character in alphabet:
                position = alphabet.find(character)
                newCharacter = newalphabet[position]
                newMessage += newCharacter
            else:
                newMessage += character
        if decrypt:
            return 'Вам необходимо <b>расшифровать</b> сообщение <br/><b>{0}</b><br/>используя шифр Атбаш.</br>Используй алфавит: абвгдежзийклмнопрстуфхцчшщъыьэюя</p><p><img src\\="data:image/png;base64,{1}" class="img-responsive atto_image_button_text-bottom"></p>'.format(
                newMessage, code_img_table)
        else:
            return 'Вам необходимо <b>зашифровать</b> сообщение <br/><b>{0}</b><br/>используя шифр Атбаш.</br>Используй алфавит: абвгдежзийклмнопрстуфхцчшщъыьэюя</p><p><img src\\="data:image/png;base64,{1}" class="img-responsive atto_image_button_text-bottom"></p>'.format(
                message, code_img_table), newMessage

    def morze(message, code_img_table):
        slovar = {'а': '•-', 'б': '-•••', 'в': '•--', 'г': '--•', 'д': '-••', 'е': '•', 'ж': '•••-', 'з': '--••',
                  'и': '••', 'й': '•---', 'к': '-•-', 'л': '•-••', 'м': '--', 'н': '-•', 'о': '---', 'п': '•--•',
                  'р': '•-•', 'с': '•••', 'т': '-', 'у': '••-', 'ф': '••-•', 'х': '••••', 'ц': '-•-•', 'ч': '---•',
                  'ш': '----', 'щ': '--•-', 'ъ': '•--•-•', 'ы': '-•--', 'ь': '-••-', 'э': '••-••', 'ю': '••--',
                  'я': '•-•-'}
        newMessage = ''
        for character in message:
            if character in slovar.keys():
                newMessage += slovar[character] + "&ensp;"
            else:
                newMessage += "&ensp;&ensp;&ensp;"
        return 'Вам необходимо расшифровать сообщение <br/><b><h6>{0}</h6></b><br/>Используя Азбуку Морзе.</br></p><p>\\{{GENERICO:type="toggle",linktext="Посмотреть картинку"\\}}<img src\\="data:image/png;base64,{1}" class="img-responsive atto_image_button_text-bottom"></p>\\{{GENERICO:type="toggle_end"\\}}'.format(newMessage, code_img_table)

    def braile(message, code_img_table):
        slovar = {'а': '⠁', 'б': '⠃', 'в': '⠺', 'г': '⠛', 'д': '⠙', 'е': '⠑', 'ж': '⠚', 'з': '⠵', 'и': '⠊',
                  'й': '⠯',
                  'к': '⠅',
                  'л': '⠇', 'м': '⠍', 'н': '⠝', 'о': '⠕', 'п': '⠏', 'р': '⠗', 'с': '⠎', 'т': '⠞', 'у': '⠥',
                  'ф': '⠋',
                  'х': '⠓',
                  'ц': '⠉', 'ч': '⠟', 'ш': '⠱', 'щ': '⠭', 'ъ': '⠷', 'ы': '⠮', 'ь': '⠾', 'э': '⠪', 'ю': '⠳',
                  'я': '⠫'}
        newMessage = ''
        for character in message:
            if character in slovar.keys():
                newMessage += slovar[character]
            else:
                newMessage += " "
        return 'Вам необходимо расшифровать сообщение <br/><b><h4>{0}</h4></b><br/>Используя шифр Брайля.</br></p><p>\\{{GENERICO:type="toggle",linktext="Посмотреть картинку"\\}}<img src\\="data:image/png;base64,{1}" class="img-responsive atto_image_button_text-bottom"></p>\\{{GENERICO:type="toggle_end"\\}}'.format(newMessage, code_img_table)

    def salt_lang(message):
        glasn = 'аеиоуыэюя'
        soglasn = 'бвгджзйклмнпрстфхцчшщ'
        newMesage = ""
        for ch in message:
            if ch in glasn:
                newMesage += ch + "с" + ch
            elif ch == " ":
                newMesage += " "
            else:
                newMesage += ch
        return 'Вам необходимо расшифровать сообщение <br/><b>{0}</b><br/>Записанное на "соленом языке"'.format(newMesage)

    with app.app_context():
        dataCipherType = ['anagram', 'cesar_e', 'cesar_d', 'morze', 'atbash_e', 'atbash_d', 'braile', 'salt_lang']
        def setCipherType(data):  # Анаграмма, Шифры Цезаря, Атбаш, Азбука морзе, Брайля, избыточная информация (соленый язык)
            for idx, type in enumerate(data):
                type = CipherType(id=idx + 1, type=type)
                db.session.add(type)
        setCipherType(dataCipherType)
        with open('text_for_tasks_poslovica', encoding='utf-8') as f:
            data = f.readlines()
            for line in data:
                line = line.strip()
                question = Questions(type=1, text=anagram(line), answer=line)
                db.session.add(question)
            db.session.commit()
        with open('text_for_tasks', encoding='utf-8') as f:
            data = f.readlines()
            # Зашифровать Шифром Цезаря
            for line in data:
                line = line.strip()
                text, answer = cesar(line, random.randint(6, 16), decrypt=False)
                question = Questions(type=2, text=text, answer=answer)
                db.session.add(question)
            db.session.commit()
            # Расшифровать Шифром Цезаря
            for line in data:
                line = line.strip()
                question = Questions(type=3, text=cesar(line, random.randint(6, 16)), answer=line)
                db.session.add(question)
            db.session.commit()
            # Расшифровать Азбуку Морзе
            for line in data:
                line = line.strip()
                question = Questions(type=4, text=morze(line, code_img_table_morse), answer=line)
                db.session.add(question)
            db.session.commit()
            # Зашифровать Шифром Атбаш
            for line in data:
                line = line.strip()
                text, answer = atbash(line, code_img_table_atbash, decrypt=False)
                question = Questions(type=5, text=text, answer=answer)
                db.session.add(question)
            db.session.commit()
            # Расшифровать Шифром Атбаш
            for line in data:
                line = line.strip()
                question = Questions(type=6, text=atbash(line, code_img_table_atbash), answer=line)
                db.session.add(question)
            db.session.commit()
            # Расшифровать Азбуку Брайля
            for line in data:
                line = line.strip()
                question = Questions(type=7, text=braile(line, code_img_table_braile), answer=line)
                db.session.add(question)
            db.session.commit()
            # Расшифровать Соленый язык
            for line in data:
                line = line.strip()
                question = Questions(type=8, text=salt_lang(line), answer=line)
                db.session.add(question)
            db.session.commit()

# Костыли перезапуска для созданной базы данных
try:
    setQuestions()
except:
    pass




# -*- cuding: utf-8 -*-
def cesar(message, n):
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
            newMessage  += character
    return newMessage


def atbash(message):
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
    return newMessage

def morze(message):
    slovar = {'а': '•-', 'б': '-•••', 'в': '•--', 'г': '--•', 'д': '-••', 'е': '•', 'ж': '•••-', 'з': '--••',
              'и': '••', 'й': '•---', 'к': '-•-', 'л': '•-••', 'м': '--', 'н': '-•', 'о': '---', 'п': '•--•',
              'р': '•-•', 'с': '•••', 'т': '-', 'у': '••-', 'ф': '••-•', 'х': '••••', 'ц': '-•-•', 'ч': '---•',
              'ш': '----', 'щ': '--•-', 'ъ': '•--•-•', 'ы': '-•--', 'ь': '-••-', 'э': '••-••', 'ю': '••--',
              'я': '•-•-'}
    newMessage = ''
    for character in message:
        if character in slovar.keys():
            newMessage += " ".join(slovar[character]) + "  "
        else:
            newMessage += "    "
    return newMessage


def braile(message):
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
            newMessage += slovar[character] + " "
        else:
            newMessage += "   "
    return newMessage

message = ['Сильвер проник в', 'систему банка и перевел', 'сто тысяч рублей', 'кажется оставив следы']
print(cesar(message[0], 5), atbash(message[1]), morze(message[2]), braile(message[3]), sep='\n')

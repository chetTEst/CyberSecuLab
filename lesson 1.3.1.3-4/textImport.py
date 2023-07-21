# -*- cuding: utf-8 -*-
'''
Файл позволяет составить свой список слов из большого словаря
'''
from collections import defaultdict
from random import seed, shuffle


with open('russian_nouns.txt', encoding='utf-8') as f:
    text = f.read()
    words = [x.lower().split()[0] for x in text.split('\n')]
    frequency = defaultdict(int)
    for word in words:
        length = len(word)
        frequency[length] += 1
    sorted_frequency = dict(sorted(frequency.items(), key=lambda item: item[1], reverse=True))
    print(sorted_frequency)
    print(dict(sorted(frequency.items(), key=lambda item: item[0])))
    words = [word for word in words if len(word) == 6 and len(set(word)) == 6 and not "ё" in word]
    seed()
    shuffle(words)
    with open('flask_app/text_for_tasks', 'w', encoding='utf-8') as o:
        o.write('\n'.join(words[:30])) # указать необходимо кол-во слов тут
    
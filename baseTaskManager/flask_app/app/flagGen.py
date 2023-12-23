from random import randint
from time import time


def uniqid(prefix='kaspCTF{', postfix='}'):
    return prefix + hex(int(time()) * randint(1000, 100000))[2:10] + hex(
        int(time() * randint(1000000, 2000000)) % 0x100000)[2:7]+postfix


regular = []
with open('../flags', 'w') as file:
    for _ in range(10):
        u = uniqid()
        file.write(u+'\n')
        regular.append(u.split('{')[1][:-1])

with open('../regular', 'w') as file:
    file.write("|".join(regular))
data = """пусть твоеИмя = спросить("Как тебя зовут?", "Аноним");
кричалка("Привет, " + твоеИмя + "!");

пусть первоеЧисло = спросить("Введите первое число:", "0");
пусть второеЧисло = спросить("Введите второе число:", "0");
пусть сумма = Число(первоеЧисло) + Число(второеЧисло);
кричалка("Сумма чисел: " + сумма);

пусть число = спросить("Введите число:", "0");
развилка (число % 2 === 0) {
    Сообщить("Число " + число + " является четным!");
} второй_путь {
    Сообщить("Число " + число + " является нечетным!");
}

пусть секретноеЧисло =Математика.округлить(Математика.случайное_число() * 10) + 1;
пусть попытка = спросить("Угадай число от 1 до 10:", "5");
развилка (Число(попытка) === секретноеЧисло) {
   кричалка("Ты угадал! Это было число " + секретноеЧисло + "!");
} второй_путь {
    кричалка("Увы! Правильное число было " + секретноеЧисло + ".");
}

пусть первоеЧисло = спросить("Введите первое число:", "1");
пусть второеЧисло = спросить("Введите второе число:", "1");
пусть произведение = Число(первоеЧисло) * Число(второеЧисло);
кричалка("Произведение чисел: " + произведение);

пусть годРождения = спросить("В каком году вы родились?", "2000");
пусть текущийГод = новыйДата().получитьГод();
пусть возраст = текущийГод - Число(годРождения);
Сообщить("Вам " + возраст + " лет!");

пусть число1 = Математика.округлить(Математика.случайное_число() * 10) + 1;
пусть число2 = Математика.округлить(Математика.случайное_число() * 10)+ 1;
развилка (число1 > число2) {
    кричалка(число1 + " больше, чем " + число2);
} развилка (число1 < число2) {
    кричалка(число1 + " меньше, чем " + число2);
} второй_путь {
    кричалка(число1 + " равно " + число2);
}
"""

for textProgram in data.split('\n\n'):
    print("'"+textProgram.replace('\n', '\\n')+"',")
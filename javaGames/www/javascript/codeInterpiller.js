class JavaIgryInterpreter {
    constructor() {
        this.translations = {
            'пусть': 'let',
            'задачка': 'function',
            'Сообщить': 'console.log',
            'спросить': 'prompt',
            'развилка': 'if',
            'второй_путь': 'else',
            'для': 'for',
            'новый': 'new',
            'Дата': 'Date',
            'получитьГод': 'getFullYear',
            'Число': 'Number',
            'Математика\.округлить': 'Math.floor',
            'Математика\.случайное_число': 'Math.random',
            'кричалка': 'alert',
            'повторить': 'while'
        };
    }


    translateToJS(code) {
        let output = '';
        let i = 0;

        while (i < code.length) {
            // Если это начало строкового литерала
            if (code[i] === '"' || code[i] === "'") {
                const delimiter = code[i];
                let j = i + 1;

                // Ищем конец строкового литерала
                while (j < code.length && code[j] !== delimiter) {
                    j++;
                }

                // Копируем строковый литерал в выход без изменений
                output += code.substring(i, j + 1);
                i = j + 1;
            } else {
                let j = i;

                // Ищем начало следующего строкового литерала или конец строки
                while (j < code.length && code[j] !== '"' && code[j] !== "'") {
                    j++;
                }

                let substring = code.substring(i, j);
                // Применяем замены и транслитерацию к подстроке
                for (let keyword in this.translations) {
                    const regex = new RegExp(keyword, 'g');
                    substring = substring.replace(regex, this.translations[keyword]);
                }

                // Транслитерируем переменные
                substring = substring.replace(/([а-яА-Я_]\w*)/g, match => this.transliterate(match));

                output += substring;
                i = j;
            }
        }

        return output;
    }

    transliterate(word) {
        let dictionary = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e',
            'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k',
            'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
            'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c',
            'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '',
            'э': 'e', 'ю': 'yu', 'я': 'ya',
            'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E',
            'Ё': 'YO', 'Ж': 'ZH', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K',
            'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R',
            'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'H', 'Ц': 'C',
            'Ч': 'CH', 'Ш': 'SH', 'Щ': 'SCH', 'Ъ': '', 'Ы': 'Y', 'Ь': '',
            'Э': 'E', 'Ю': 'YU', 'Я': 'YA', '_': '_'
        };

        return word.split('').map(function (char) {
            return dictionary[char] || char;
        }).join("");
    }

    execute(code) {
        const jsCode = this.translateToJS(code);
        new Function(jsCode)();
    }
}


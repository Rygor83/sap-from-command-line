Как и все САП консультанты, я работаю с разными заказчиками в разных системах. У каждой системы свои уровни безопастности. Некоторые заказчики требуют меняют пароль раз в 3 месяца, некоторые раз в месяц. Можно помнить пароли к тем системам, в которых ты работаешь постояно, но что делать с заказчиками, которые обращаются к тебе раз в 2-3 месяца. Да к тому же пробовать синхронизировать все пароли ко всем системам это небезопасно, да и напрасная трата времени. 

Давным давно я захотел создать базу данных, где можно было безопасно хранить все данные о системах, а так же пароли. И запускать системы из командной строки. Так и родился данный инструмент

Что может этот инструмент:
1. Запускать сап системы из командной строки. Это возможно встроенному инструменту САП - sapshcut.exe Детальное описание данного инструмента можно найти в ноте 103019. Я просто взял этот инструмент я адаптировал команды по свой инструмент. 
2. Все данные о системах (Ид. системы, мандант, пользователь, пароль, описане системы, имя заказчика) храняться в базе данных, пароль зашифровон РСА
3. Так же можно хранить ЮРЛ - если САП систему можно запускать в браузере, а так же автотайп последовательность, для автоматического заполнения имени пользователя и пароля в веб версии системы.
4. Возможность запуска транзакции при запуске системы, а также передача параметров этой транзакции. Например, вы запускаете тр. СЕ11 и говорите открыть таблицу Т001. Данные для этого тоже ведутся в базе данных.
5. Запуск сап системы с пользователем/паролем вне базы данных.
6. Запуск САП с дополнительным командами: системные команды (/n, /nend, /nex, /o), отчеты (tr. SE38 -> имя отчета), и т.д. 
7. Копирование пароля для запрошенной системы в буфер обмена. Полезно для случая тр. СТМС, когда импортируешь запрос в другую систему и запрашивается пароль.
8. Создание зашифрованного паролем бэкап архива со следующими файлами внутри: конфигурационный файл, база данных, публичный и приватный ключи шифрования, XML файл со списком всех систем из SAPLogon



Далее описаны команды по мере их использования. С какой нужно начинать и какие дальше использовать
# README. Каталог lab7/app: кодовая часть лабораторной работы 7 (Power Automate Desktop).

## Состав каталога

Шесть файлов .robin: это текстовые исходники классических потоков Power Automate Desktop
на языке скриптов robin (то, что PAD хранит и копирует внутренне, при вставке в designer
поток восстанавливается в графические экшены):

- FromPdf-Pad.robin: диалог ввода имени, приветствие, извлечение текста из PDF
  (Data/Input/SourceText.pdf) и запись текста в Data/Output/TextFromPdf.txt.
- ExcelExamen-Pad.robin: чтение оценок из Data/Examen.xlsx, поиск фамилии,
  вывод оценки студента, закрытие Excel.
- Switch-Pad.robin: ввод четырехзначного числа, проверка четности каждой цифры
  (ветвление по остатку mod 2, выполнено конструкцией IF/ELSE, так как
  в современном PAD экшен Switch отсутствует).
- Analiz-Pad.robin: чтение файлов из Data/Input/Resumes, распознавание сущностей
  типа «адрес электронной почты», вывод найденных значений списком.
- OcrList-Pad.robin: распознавание текста с Data/Input/Student.jpg (Windows OCR),
  разбивка по строкам и запись списка в новую книгу Excel.
- PhonesList-Pad.robin: чтение файлов из Data/Input/PhoneNumbers, распознавание
  сущностей типа «номер телефона», вывод списка и запись в новую книгу Excel.

Файлы Data/Input/PhoneNumbers/*.txt и Data/Output/TextFromPdf.txt создаются или
используются потоками как входные и выходные данные.

## Импорт в Power Automate Desktop

Импорт выполняется вставкой текста файла .robin на холст designer (открыть поток,
скопировать содержимое .robin и вставить на холст: PAD воссоздаст экшены). Это GUI-шаг,
в рамках подготовки кодовой части не выполнялся.

## Запуск потока

Запуск из консоли: ms-powerautomate:/console/flow/run?workflowName=<имя потока>,
где <имя потока> соответствует имени, под которым поток сохранен в PAD
(например, FromPdf-Pad).

## Ограничения

Синтаксис .robin сверялся с paste-validated справочником экшенов PAD 2.73
и примерами из github robin-language/robin, но НЕ валидировался в designer
(GUI недоступен). Возможные расхождения при вставке:

- Switch-Pad: позиция символа в Text.GetSubtext.GetSubtext в разных версиях PAD
  может отсчитываться с 0 или с 1; в потоке использована нумерация с 0 по практикуму,
  при ошибке измените цикл LOOP на FROM 1 TO 4.
- Text.RecognizeEntitiesInText: язык установлен English (в списке языков экшена
  русского нет), режимы Email и PhoneNumber работают и на таких данных.
- Имена переменных совпадают с практикумом (в том числе FileContens у Analiz-Pad
  и PhonesList-Pad).

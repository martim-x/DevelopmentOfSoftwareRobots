# README. Каталог lab8/app: кодовая часть лабораторной работы 8 (Power Automate Desktop).

## Состав каталога

Четыре файла .robin: текстовые заготовки потоков Power Automate Desktop.
Они не являются подтверждёнными экспортами рабочих потоков и не прошли
валидацию в установленном PAD:

- Sreenshot-Pad.robin (задание 8-1, имя проекта по методичке): горячая клавиша
  Ctrl-Q, уникальное имя снимка из переменной CurrentDateTime, сохранение
  .jpg в Data/Output/Скриншоты, открытие снимка в Paint, диалог
  «Продолжать? (1-да, 0-нет)» и переход к метке Begin для серии снимков.
- News2-Pad.robin (задание 8-2): диалог темы, запуск Edge, фокус в поле поиска
  сайта, отправка темы с Enter, чтение атрибута Own Text двух заголовков,
  список, сообщение, закрытие браузера.
- Salary-Pad.robin (задание 8-3): подключение SQL, проверка пустоты БД, очистка
  по подтверждению, цикл добавления записей через диалоги (ФИО, должность,
  стаж, оклад, премия), расчёт начислений восемью update-инструкциями,
  построчный вывод всех сотрудников, закрытие подключения.
- SumOfValues-Pad.robin (задание 8-4, самостоятельная постановка): OCR
  Windows OCR по Data/Input/ValuesForSum.jpg, разбор числовых строк регулярным
  выражением (заголовок изображения отсеивается), суммирование, вывод и запись
  Data/Output/SumResult.txt. Ожидаемый результат: 12 + 8 + 15 + 5 = 40.

Файлы данных:

- Data/Input/ValuesForSum.jpg — исходное изображение для задания 8-4 (не менялся).
- Data/create_salary.sql — скрипт создания базы Salary и таблицы Зарплата
  (дословно по методичке, стр. 51); выполняется один раз в SSMS.
- Data/Output/Скриншоты/ — папка под снимки экрана (создаётся заранее, .gitkeep).

## Перенос в Power Automate Desktop

Файлы .robin служат спецификацией для ручной сборки действий в дизайнере.
Простая вставка текста .robin в установленный PAD ранее не создавала действий;
каждое действие требуется собрать и проверить в GUI. До этого потоки не
считать готовыми и исполняемыми.

## Запуск потоков

Запуск из консоли: ms-powerautomate:/console/flow/run?workflowName=<имя потока>,
например Sreenshot-Pad.

Перед запуском:

- Salary-Pad: выполнить Data/create_salary.sql в SSMS; в строке подключения
  заменить Server=localhost на имя фактического экземпляра SQL Server
  (в исходном отчёте фигурировал чужой сервер STANISLAW).
- Sreenshot-Pad: папка Data/Output/Скриншоты уже в репозитории.
- News2-Pad: требуется подбор элементов в designer (см. Ограничения).

## Ограничения

Синтаксис .robin сверялся с paste-validated примерами PAD (REFramework-for-
Power-Automate-Desktop, qiita, PL-500, gist kinuasa) и справочником экшенов
Microsoft, но НЕ валидировался в designer (GUI недоступен подготовительному
исполнителю). Возможные расхождения при вставке:

- Sreenshot-Pad: у Workstation.TakeScreenshot.TakeScreenshotAndSaveToFile и
  System.RunApplication.ApplicationPath набор параметров в разных версиях PAD
  может отличаться (например, отсутствие AfterWindowClosed) — при ошибке вставки
  укорачивать до проверенной формы `Workstation.TakeScreenshot.TakeScreenshotAndSaveToFile File: ... ImageFormat: System.ImageFormat.Jpg`.
- News2-Pad: у WebAutomation.LaunchEdge.LaunchEdge набор параметров (TabUrl,
  WindowState и др.) в разных версиях PAD может отличаться от AttachToEdgeByUrl
  (проверенная форма из gist: `WebAutomation.LaunchEdge.AttachToEdgeByUrl TabUrl: ... BrowserInstance=> Browser`).
- Salary-Pad: булевы литералы записаны как %True%/%False% (PAD-стиль
  выражений); если вставка ругается на сравнение `IF AddBool = %True%`,
  заменить на `IF AddBool THEN`.
- News2-Pad: селектор поля поиска input.menu__input-search проверен по HTML
  devby.io; селекторы Header 1 / Header 2 (результаты поиска) — ЗАГЛУШКИ.
  Поиск devby.io ведёт на Google Custom Search (google.com/cse), заголовки
  результатов лежат в iframe и подбираются заново в designer (требуется живой
  подбор элемента, это неизбежный GUI-шаг). Замещающий источник выбран потому,
  что yandex.by/news из методички на этой машине не открывается (TLS-ошибка,
  проверено 18.11.2026); если контроллер решит вернуться к yandex.by, селекторы
  подбираются заново.
- Salary-Pad: результат Database.ExecuteSqlStatement в современных версиях PAD —
  DataTable, поэтому количество строк извлекается как %QueryResult[0][0]%
  (методичка писала о текстовой переменной по старой версии PAD). Имена
  переменных Name, Position и т.д. соответствуют методичке.
- SumOfValues-Pad: если Windows OCR распознает заголовок или шум как строку из
  цифр, регулярное выражение отфильтрует только строки целиком из цифр; при
  необходимости можно дополнительно ограничить диапазон строк.

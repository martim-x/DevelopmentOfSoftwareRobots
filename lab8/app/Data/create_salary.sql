-- Скрипт создания базы данных «Зарплата» и таблицы начислений (задание 8-3).
-- Источник: labs/РПР_Практикум 2023.pdf, стр. 51 (скрипт приведён дословно).
-- Выполняется один раз в SQL Server Management Studio до запуска Salary-Pad.
USE master
CREATE database Salary
GO

USE Salary
GO
CREATE TABLE Зарплата
( [ФИО] nvarchar(50) NOT NULL DEFAULT ('---'),
  [Должность] nvarchar(50) NOT NULL DEFAULT ('---'),
  [Стаж, лет] int NOT NULL DEFAULT ((0)),
  [Оклад, руб] float NOT NULL DEFAULT ((0)),
  [Премия, руб] float NOT NULL DEFAULT ((0)),
  [Надбавка за стаж, руб] float NOT NULL DEFAULT ((0)),
  [Итого, руб] float NOT NULL DEFAULT ((0)),
  [Налоги, руб] float NOT NULL DEFAULT ((0)),
  [Получить, руб] float NOT NULL DEFAULT ((0))
)

INSERT into Зарплата (ФИО, Должность, [Стаж, лет], [Оклад, руб], [Премия, руб])
Values(N'Афанасьева А.И.', N'Генеральный директор', 16, 3000, 105),
(N'Дудин Е.А.', N'Директор отдела маркетинга', 9, 2180, 300),
(N'Ковалев Д.М.', N'HR-менеджер', 5, 1200, 100),
(N'Кежар В.П.', N'Инспектор по кадрам', 20, 2500, 200),
(N'Ивицкая Н.И.', N'Главный бухгалтер', 12, 1700, 655)

-- Проверка: должно вернуть 5
select count(*) from Зарплата

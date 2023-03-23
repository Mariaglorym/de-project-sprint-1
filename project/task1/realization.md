# Витрина RFM

## 1.1. Выясните требования к целевой витрине.

Постановка задачи выглядит достаточно абстрактно - постройте витрину. Первым делом вам необходимо выяснить у заказчика детали. Запросите недостающую информацию у заказчика в чате.

Зафиксируйте выясненные требования. Составьте документацию готовящейся витрины на основе заданных вами вопросов, добавив все необходимые детали.

-----------

Требуеться создать витрину с названием dm_rfm_segments со структурой user_id, recency, frequency, monetary_value в схеме analysis. Она содержит даныне за 2022 год. Обновлять не нужно. Только с заказами в статусе Closed.  
С полями:
Recency (пер. «давность») — сколько времени прошло с момента последнего заказа.
Frequency (пер. «частота») — количество заказов.
Monetary Value (пер. «денежная ценность») — сумма затрат клиента.
Все данные должны быть поделены на 5 категорий. В recency поле last_order_dt = NULL если не было сделанно заказов. В frequency количество заказов не может быть NULL, должно быть 0.
Все данныне находяться в схеме production. Нужно создать витрины данных в схеме analysis, которые будут содержать данные таблиц из схемы production



## 1.2. Изучите структуру исходных данных.

Полключитесь к базе данных и изучите структуру таблиц.

Если появились вопросы по устройству источника, задайте их в чате.

Зафиксируйте, какие поля вы будете использовать для расчета витрины.

-----------

production.orders (
	order_id, -- можно подсчитать количество
	order_ts, -- предпологаю, что время заказа
	user_id, -- id клиента
	payment, -- сумма затрат клиента
	status, -- статус заказа, нужен 4 (close)
);


## 1.3. Проанализируйте качество данных

Изучите качество входных данных. Опишите, насколько качественные данные хранятся в источнике. Так же укажите, какие инструменты обеспечения качества данных были использованы в таблицах в схеме production.

-----------

В таблице orderitems колонка id имеет формат данных int4 NOT, так же автоматически присваивается новой записи уникальный номер, являеться PRIMARY KEY,
	product_id int4 NOT NULL, уникальное значение, имеет внешни ключ на products(id)
	order_id int4 NOT NULL,уникальное значение, имеет внешни ключ на orders(order_id)
	"name" varchar(2048) NOT NULL,
	price numeric(19, 5) NOT NULL DEFAULT 0, больше или равна нулю
	discount numeric(19, 5) NOT NULL DEFAULT 0, скидка не может быть меньше 0 и больше цены товара,
	quantity int4 NOT NULL, количество больше нуля.


В таблице orders:
	order_id int4 NOT NULL, являеться PRIMARY KEY,
	order_ts timestamp NOT NULL,
	user_id int4 NOT NULL,
	bonus_payment numeric(19, 5) NOT NULL DEFAULT 0,
	payment numeric(19, 5) NOT NULL DEFAULT 0,
	"cost" numeric(19, 5) NOT NULL DEFAULT 0, есть проверка, что cost = payment + bonus_payment
	bonus_grant numeric(19, 5) NOT NULL DEFAULT 0,
	status int4 NOT NULL.

В таблице orderstatuses:
	id int4 NOT NULL, являеться PRIMARY KEY
	"key" varchar(255) NOT NULL.

В таблице orderstatuslog:
	id int4 NOT NULL , автоматически присваивается новой записи уникальный номер, являеться PRIMARY KEY,
	order_id int4 NOT NULL, внешний ключ orders(order_id), уникальыне значения,
	status_id int4 NOT NULL, внкшний ключ orderstatuses(id), уникальыне значения,
	dttm timestamp NOT NULL.

В таблице products:
	id int4 NOT NULL, являеться PRIMARY KEY,
	"name" varchar(2048) NOT NULL,
	price numeric(19, 5) NOT NULL DEFAULT 0, условие price >= 0,

В таблице users:
	id int4 NOT NULL, являеться PRIMARY KEY,
	"name" varchar(2048) NULL,
	login varchar(2048) NOT NULL.


## 1.4. Подготовьте витрину данных

Теперь, когда требования понятны, а исходные данные изучены, можно приступить к реализации.

### 1.4.1. Сделайте VIEW для таблиц из базы production.**

Вас просят при расчете витрины обращаться только к объектам из схемы analysis. Чтобы не дублировать данные (данные находятся в этой же базе), вы решаете сделать view. Таким образом, View будут находиться в схеме analysis и вычитывать данные из схемы production. 

Напишите SQL-запросы для создания пяти VIEW (по одному на каждую таблицу) и выполните их. Для проверки предоставьте код создания VIEW.

```SQL
create or replace view analysis.v_orderitems as
select * from production.orderitems o

create or replace view analysis.v_orders as
select * from production.orders
 
create or replace view analysis.v_orderstatuses as
select * from production.orderstatuses 

create or replace view analysis.v_products as
select * from production.products 

create or replace view analysis.v_users as
select * from production.users 
```

### 1.4.2. Напишите DDL-запрос для создания витрины.**

Далее вам необходимо создать витрину. Напишите CREATE TABLE запрос и выполните его на предоставленной базе данных в схеме analysis.

```SQL
CREATE TABLE analysis.dm_rfm_segments (
 user_id INT NOT NULL PRIMARY KEY,
 recency INT NOT NULL CHECK(recency >= 1 AND recency <= 5),
 frequency INT NOT NULL CHECK(frequency >= 1 AND frequency <= 5),
 monetary_value INT NOT NULL CHECK(monetary_value >= 1 AND monetary_value <= 5)
);
```

### 1.4.3. Напишите SQL запрос для заполнения витрины

Наконец, реализуйте расчет витрины на языке SQL и заполните таблицу, созданную в предыдущем пункте.

Для решения предоставьте код запроса.

```SQL
CREATE OR REPLACE VIEW v_dm_rfm_segments as (
select user_id,
NTILE(5) OVER(ORDER BY count_order asc) as count_order,
NTILE(5) OVER(ORDER BY sum_payment  asc) as sum_payment,
NTILE(5) OVER(ORDER BY last_date  asc) as last_date
from(
select user_id, 
sum(case when status = 4 then 1 else 0 end) "count_order",
sum(case when status = 4 then payment else 0 end) "sum_payment",
max(case when status = 4 then order_ts else TIMESTAMP '2020-01-01 00:00:00' end) "last_date" -- Вместо Null сделал TIMESTAMP '2020-01-01 00:00:00', потому что NULL уходит в категорию 5
from analysis.v_orders vo
group by user_id
 ) v_1 );
 
INSERT INTO analysis.dm_rfm_segments (user_id, recency, frequency, monetary_value)
SELECT user_id,last_date, count_order, sum_payment FROM analysis.v_dm_rfm_segments
```
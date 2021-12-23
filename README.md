# Идея

## Основа

Изначально идея заключается в реализации экономической игры.   
Случайным образом задается список компаний с некоторым количество акций, имеющих определенную стоимость, которые игроки могут покупать, выигрывая на разнице цен.    

## Цены акций

Цены на акции формируются исходя из выбранных случайным образом коэффициентов, характеризующих дисперсию и средний прирост акций.   

## Ход игры

- Раунд 1 - "Покупка". Игроки приобретают акции доступных компаний. Принимать решения можно на основе исторических данных о ценах. В случае покупки большего числа акций компании, чем доступно на данный момент, акции уходят тому, кто раньше их купил.
- Раунд 2 - "Продажа". Игроки продают акции по их стоимости. Подводится итоговый счет. Выигрывает тот, кто имеет на балансе больше средств.

## Идеи для модификаций

- Реализация игры в несколько ходов (несколько ходов для покупки, несколько ходов с возможностью выбора когда продавать акции)
- Реализация торговли акциями между игроками
- Реализация симуляции экономики (вбросы, влияние спроса/предложения, деление компаний на группы компаний по отраслям деятельности с разным экономическим поведением)
- Реализация проекта в виде бота-игры в Telegram

# Архитектура

1. gateway - proxy и load balancer на основе Nginx. Проксирует запросы на stateful (endpoint - /api/v1/stats/) и worker (остальные endpoint - /api/v1/).
2. worker - python (Flask API) + gunicorn, реализует набор API:
- /api/v1/start-game/ - начало одной из игр
- /api/v1/stop-game/ - конец одной из игр
- /api/v1/auction/ - покупка акций
- /api/v1/company/info/ - получить информацию по компании (история и цена на акции)
- /api/v1/gamer/info/ - получить информацию об игроке (баланс и количество акций)
3. mysql - база, которая хранит всю инфу по текущим играм
4. stateful - сервис, который хранит метаинфу между играми (статистика + потенциально может использоваться для организации серии игр) - python (Flask API) + gunicorn, реализует entrypoint:
- /api/v1/stats/

Схема: https://miro.com/app/board/uXjVOZ0rN-w=/?invite_link_id=798804507188

# Сборка и запуск

1. `docker-compose build worker && docker-compose build stateful`

2. `docker-compose up -d`

3. `curl 127.0.0.1:4000/api/v1/...`

4. enjoy

# exchange_bot

## Prestart config
- Для вывода логов в `systemd` необходим пакет `python3-systemd`. Установка командой:  
```
apt update
apt install python3-systemd
```
- Далее устанавливаем виртуальное окружение (при необходимости, любым удобным способом)  
- и зависимости:  
`pip install -r requirements.txt`

## Start and Config
- В корне необходимо скопировать файл `example.env` и вставить в ту же папку с именем `.env`.
- Указать корректные токены в соответствующие переменные.  
`TG_BOT_TOKEN`- токен ТГ бота  

## Features
- Получить имя пользователя:
```
updates = bot.get_updates()
firts_name = updates[-1].message.from_user.first_name
```

## Демонизация  
https://github.com/Eugene-Fed/daemonizer

## TODO  
- [ ] Перенести настройки в config файл.
- [ ] Протестировать и активировать логи демона в системный журнал.

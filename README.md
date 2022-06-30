# Вступительное задание в Летнюю Школу Бэкенд Разработки Яндекса 2022

## Создать виртуальное окружение и установить зависимости

```
make venv
```

## Запустить проект локально

```
make start-local
```
Сервис запустится на 8000 порту, а база данных - на 5432. Также будет доступна [документация в формате OpenAPI](http://localhost:8000/docs).

## Протестировать

```
make test
```
Предполагается, что установлены зависимости и проект запущен локально

## Остановить запущенный локально проект

```
make stop-local
```

## Задеплоить

```
cd deploy
ansible-playbook -i hosts.ini deploy.yml
```

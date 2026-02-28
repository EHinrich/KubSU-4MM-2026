# KubSU-4MM-2026

`Hello, World!`

## Установка браузерного расширения

1. Откройте Google Chrome и перейдите в `chrome://extensions/`.
2. Включите **Режим разработчика**.
3. Нажмите **Загрузить распакованное расширение** и выберите папку `extension`.
4. Нажмите `Отладка страниц service worker` для просмотра логов и отладки расширения.

```bash
$ python -m venv .venv

$ source .venv/bin/activate

$ source .venv/scripts/activate

$ where python3
$ python main.py
```
```bash
$ pip install "fastapi[standard]"
$ pip freeze > requirements.txt
```
```bash
$ fastapi dev main.py
```

```bash
$ pip install ruff
$ ruff check --verbose
$ ruff format --verbose
```
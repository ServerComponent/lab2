# Лабораторна робота №2: RESTful API обліку витрат (In-Memory)

## Сутності

| Сутність | Поля |
|---|---|
| User | `id`, `name` |
| Category | `id`, `name` |
| Record | `id`, `user_id`, `category_id`, `created_at` (ISO-8601), `amount` (decimal) |

## Структура проєкту

```
.
├── app.py
├── storage.py
├── requirements.txt
├── bruno_collection/
└── README.md
```

## Встановлення та запуск

Потрібен Python 3.10 або новіший.

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload
```

Сервер стартує на `http://localhost:8000`. Інтерактивна документація Swagger доступна за адресою `http://localhost:8000/docs`.

## Маршрути

| Метод | Шлях | Опис | Успішний код |
|---|---|---|---|
| GET | `/users` | Список користувачів | 200 |
| GET | `/user/<user_id>` | Користувач за id | 200 |
| POST | `/user` | Створити користувача | 201 |
| DELETE | `/user/<user_id>` | Видалити користувача | 204 |
| GET | `/category` | Список категорій | 200 |
| POST | `/category` | Створити категорію | 201 |
| DELETE | `/category/<category_id>` | Видалити категорію | 204 |
| POST | `/record` | Створити запис | 201 |
| GET | `/record/<record_id>` | Запис за id | 200 |
| DELETE | `/record/<record_id>` | Видалити запис | 204 |
| GET | `/record?user_id=X&category_id=Y` | Фільтрація записів | 200 |

### Приклади тіл запитів

```json
POST /user        {"name": "Ivan"}
POST /category    {"name": "Food"}
POST /record      {"user_id": 1, "category_id": 1, "amount": 150.50}
```

Поле `created_at` встановлюється сервером автоматично (UTC, ISO-8601).

### Фільтрація записів

`GET /record` приймає query-параметри `user_id` та `category_id`. Якщо передано обидва, повертаються записи, що задовольняють обидві умови. Якщо не передано жодного, сервіс повертає `400 Bad Request`:

```json
{
    "error": "invalid_request",
    "message": "At least one query parameter ('user_id' or 'category_id') is required for filtration"
}
```

## Обробка помилок

Усі помилки повертаються у форматі JSON:

```json
{"error": "<код помилки>", "message": "<опис>"}
```

| Код | Коли виникає |
|---|---|
| 400 | Невалідне тіло запиту (немає поля, порожнє `name`, `amount` не число), невалідні query-параметри, відсутні параметри фільтрації |
| 404 | Об'єкт з указаним id не знайдено, а також неіснуючі `user_id` або `category_id` під час створення запису |

Стандартну відповідь FastAPI `422 Unprocessable Entity` замінено на `400 Bad Request` відповідно до технічного завдання.

## Прийняті рішення

- Під час видалення користувача або категорії всі пов'язані з ними записи видаляються каскадно.
- Лічильники id лише зростають: після видалення об'єкта його id не використовується повторно.
- `POST /record` з неіснуючим `user_id` або `category_id` повертає `404`.
- Сума (`amount`) обробляється як `Decimal`, у JSON-відповіді подається числом.

## Bruno-колекція

Колекція запитів лежить у `bruno_collection/` і зберігається в Git.

1. Запустіть сервер (`uvicorn app:app --reload`).
2. Відкрийте Bruno → **Open Collection** → оберіть папку `bruno_collection/`.
3. Виберіть окруження **local** у правому верхньому куті.

Базовий URL винесено у змінну `baseUrl` (за замовчуванням `http://localhost:8000`). Щоб протестувати розгорнутий сервер, створіть нове окруження з іншим значенням `baseUrl` і виберіть його, а самі запити змінювати не потрібно.

Запити згруповано за папками `User`, `Category`, `Record` та `Errors` (негативні сценарії: 400 і 404). Перед повним прогоном колекції перезапустіть сервер, щоб пам'ять була порожньою й id збігалися.

Прогін колекції з командного рядка:

```bash
cd bruno_collection
npx @usebruno/cli run --env local -r
```
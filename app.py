from datetime import datetime, timezone
from decimal import Decimal

from fastapi import FastAPI, HTTPException, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

import storage

app = FastAPI(title="Expense Tracker API")


class UserCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(min_length=1)


class CategoryCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(min_length=1)


class RecordCreate(BaseModel):
    user_id: int
    category_id: int
    amount: Decimal



ERROR_NAMES = {
    400: "invalid_request",
    404: "not_found",
    405: "method_not_allowed",
}


def error_response(status_code: int, error: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": error, "message": message},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    error = ERROR_NAMES.get(exc.status_code, "error")
    return error_response(exc.status_code, error, str(exc.detail))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    parts = []
    for err in exc.errors():
        loc = ".".join(str(p) for p in err["loc"] if p not in ("body", "query", "path"))
        parts.append(f"{loc}: {err['msg']}" if loc else err["msg"])
    return error_response(400, "invalid_request", "; ".join(parts))


def get_or_404(table: dict, item_id: int, label: str) -> dict:
    item = table.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"{label} with id {item_id} not found")
    return item



@app.get("/users")
def list_users():
    return list(storage.users.values())


@app.get("/user/{user_id}")
def get_user(user_id: int):
    return get_or_404(storage.users, user_id, "User")


@app.post("/user", status_code=201)
def create_user(body: UserCreate):
    user = {"id": storage.next_id("user"), "name": body.name}
    storage.users[user["id"]] = user
    return user


@app.delete("/user/{user_id}", status_code=204)
def delete_user(user_id: int):
    get_or_404(storage.users, user_id, "User")
    del storage.users[user_id]
    for rid in [r["id"] for r in storage.records.values() if r["user_id"] == user_id]:
        del storage.records[rid]
    return Response(status_code=204)



@app.get("/category")
def list_categories():
    return list(storage.categories.values())


@app.post("/category", status_code=201)
def create_category(body: CategoryCreate):
    category = {"id": storage.next_id("category"), "name": body.name}
    storage.categories[category["id"]] = category
    return category


@app.delete("/category/{category_id}", status_code=204)
def delete_category(category_id: int):
    get_or_404(storage.categories, category_id, "Category")
    del storage.categories[category_id]
    for rid in [r["id"] for r in storage.records.values() if r["category_id"] == category_id]:
        del storage.records[rid]
    return Response(status_code=204)



@app.post("/record", status_code=201)
def create_record(body: RecordCreate):
    get_or_404(storage.users, body.user_id, "User")
    get_or_404(storage.categories, body.category_id, "Category")

    record = {
        "id": storage.next_id("record"),
        "user_id": body.user_id,
        "category_id": body.category_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "amount": body.amount,
    }
    storage.records[record["id"]] = record
    return record


@app.get("/record/{record_id}")
def get_record(record_id: int):
    return get_or_404(storage.records, record_id, "Record")


@app.delete("/record/{record_id}", status_code=204)
def delete_record(record_id: int):
    get_or_404(storage.records, record_id, "Record")
    del storage.records[record_id]
    return Response(status_code=204)


@app.get("/record")
def list_records(user_id: int | None = None, category_id: int | None = None):
    if user_id is None and category_id is None:
        return error_response(
            400,
            "invalid_request",
            "At least one query parameter ('user_id' or 'category_id') is required for filtration",
        )

    result = list(storage.records.values())
    if user_id is not None:
        result = [r for r in result if r["user_id"] == user_id]
    if category_id is not None:
        result = [r for r in result if r["category_id"] == category_id]
    return result
from itertools import count

users: dict[int, dict] = {}
categories: dict[int, dict] = {}
records: dict[int, dict] = {}

_counters = {
    "user": count(1),
    "category": count(1),
    "record": count(1),
}


def next_id(kind: str) -> int:
    return next(_counters[kind])
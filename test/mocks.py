"""Mock objects for testing."""

from typing import Optional

from pydantic import BaseModel


class User(BaseModel):  # noqa: D101
    name: str


class SessionStore:  # noqa: D101
    def __init__(self):  # noqa: D107
        self._ids = {}

    def __contains__(self, item):  # noqa: D105
        return item in self._ids

    def __len__(self):  # noqa: D105
        return len(self._ids)

    def new(self, session_id: str, user: User) -> None:  # noqa: D102
        assert session_id not in self._ids

        self._ids[session_id] = user

    def remove(self, session_id: str) -> None:  # noqa: D102
        del self._ids[session_id]

    def get(self, session_id: str) -> Optional[User]:  # noqa: D102
        return self._ids.get(session_id, None)

    def keys(self):  # noqa: D102
        return list(self._ids.keys())

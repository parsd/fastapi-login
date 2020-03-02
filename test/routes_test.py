"""Integration test for the `routes` module."""

from dataclasses import dataclass
from http import HTTPStatus
from typing import Callable, Generator, MutableMapping, Protocol
from unittest.mock import MagicMock

import pytest
from assertpy import assert_that
from fastapi import FastAPI
from pytest_mock import MockFixture
from requests.models import Response
from starlette.testclient import TestClient

import fastapi_login

from . import mocks

# make fixtures work without warning:
# pylint: disable=redefined-outer-name

USERNAME = "user@test.net"
PASSWORD = "secret"

ERROR_TEXT = "the error"

TEST_USER = mocks.User(name=USERNAME)


@dataclass
class LoggedOutApp:  # noqa: D101
    client: TestClient
    store: mocks.SessionStore
    authenticate: Callable[[str, str], mocks.User]


@pytest.fixture
def logged_out_app() -> Generator[LoggedOutApp, None, None]:
    """Create the test web app for `fastapi_login.UsersRoutes."""

    def auth(username: str, password: str) -> mocks.User:
        if username != USERNAME or password != PASSWORD:
            raise Exception(ERROR_TEXT)
        return TEST_USER

    store = mocks.SessionStore()
    authenticate = MagicMock(side_effect=auth)
    routes = fastapi_login.UsersRoutes(store, authenticate)

    app = FastAPI(debug=True)
    app.include_router(routes.router)
    yield LoggedOutApp(client=TestClient(app), store=store, authenticate=authenticate)


def test_valid_login(logged_out_app: LoggedOutApp):
    """Test a valid login request."""
    response = logged_out_app.client.post(
        "/login", data={"username": USERNAME, "password": PASSWORD}
    )

    assert_that(response.status_code).is_equal_to(HTTPStatus.CREATED)
    logged_out_app.authenticate.assert_called_once_with(USERNAME, PASSWORD)  # type: ignore
    assert_that(logged_out_app.store).is_length(1)

    reference_token = fastapi_login.Token.from_session_id(
        logged_out_app.store.keys()[0]
    )
    session_token = fastapi_login.Token.parse_obj(response.json())
    assert_that(session_token).is_equal_to(reference_token)


def test_invalid_login(logged_out_app: LoggedOutApp):
    """Test an invalid login request."""
    response = logged_out_app.client.post(
        "/login", data={"username": "not@present.net", "password": "..."}
    )

    assert_that(response.status_code).is_equal_to(HTTPStatus.BAD_REQUEST)
    logged_out_app.authenticate.assert_called_once()  # type: ignore
    assert_that(logged_out_app.store).is_empty()

    result = response.json()
    assert_that(result).has_detail([ERROR_TEXT])

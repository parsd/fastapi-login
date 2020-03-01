"""Unit test of the `session` module."""

import base64

import pytest
from assertpy import assert_that

from . import session

TEST_SESSION_ID = "session-id"


def test_create_session_token():
    """Test to create a session `Token`."""
    token = session.Token.from_session_id(TEST_SESSION_ID)
    assert_that(token.token_type).is_same_as(session.TokenType.BEARER)

    payload = token.decode()
    assert_that(payload).is_length(1)
    assert_that(payload).has_session(TEST_SESSION_ID)


def test_create_token_with_invalid_header():
    """Test to decode an invalid token header."""
    token = session.Token(access_token=b"invalid.token")
    with pytest.raises(session.TokenError):
        _ = token.decode()


def test_create_token_with_invalid_payload():
    """Test to decode an invalid token payload."""
    token = session.Token(access_token=session.SESSION_HEADER + b".")
    with pytest.raises(session.TokenError):
        _ = token.decode()

    token = session.Token(access_token=b"invalid")
    with pytest.raises(session.TokenError):
        _ = token.decode()


def test_create_token_with_empty_payload():
    """Test to decode an empty payload."""
    token = session.Token(
        access_token=session.SESSION_HEADER + b"." + base64.b64encode(b"{}")
    )

    payload = token.decode()
    assert_that(payload).is_empty()

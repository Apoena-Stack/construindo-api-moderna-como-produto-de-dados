import pytest
from unittest.mock import MagicMock, patch, call

from source.gateway.sqlite_client import SQLiteClient


@pytest.fixture
def mock_session():
    return MagicMock()


@pytest.fixture
def client(mock_session):
    with patch("source.gateway.sqlite_client.create_engine"), \
         patch("source.gateway.sqlite_client.sessionmaker") as mock_sm:
        mock_sm.return_value.return_value = mock_session
        yield SQLiteClient(), mock_session


def test_engine_criado_com_caminho_correto():
    with patch("source.gateway.sqlite_client.create_engine") as mock_engine, \
         patch("source.gateway.sqlite_client.sessionmaker"):
        SQLiteClient()
        mock_engine.assert_called_once_with("sqlite:///db/database.db")


def test_get_session_retorna_sessao(client):
    sqlite_client, mock_session = client
    session = sqlite_client._get_session()
    assert session is mock_session


def test_call_fecha_sessao_apos_uso(client):
    sqlite_client, mock_session = client
    gen = sqlite_client()
    session = next(gen)

    assert session is mock_session
    mock_session.close.assert_not_called()

    try:
        next(gen)
    except StopIteration:
        pass

    mock_session.close.assert_called_once()


def test_call_fecha_sessao_mesmo_com_excecao(client):
    sqlite_client, mock_session = client
    gen = sqlite_client()
    next(gen)

    try:
        gen.throw(RuntimeError("erro simulado"))
    except RuntimeError:
        pass

    mock_session.close.assert_called_once()

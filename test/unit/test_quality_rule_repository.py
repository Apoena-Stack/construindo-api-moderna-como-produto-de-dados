import pytest
from unittest.mock import MagicMock, patch

from source.repository.sqlite_quality_rule_repository import SQLiteQualityRuleRepository
from source.exceptions.repo_exceptions import (
    DeleteIsNotActive,
    RevertDeleteIsActive,
    UpdateIsNotActive,
)


@pytest.fixture
def session():
    mock = MagicMock()
    mock.__enter__ = MagicMock(return_value=mock)
    mock.__exit__ = MagicMock(return_value=False)
    return mock


@pytest.fixture
def sqlite_client(session):
    client = MagicMock()
    client._get_session.return_value = session
    return client


@pytest.fixture
def repo(sqlite_client):
    return SQLiteQualityRuleRepository(sqlite_client=sqlite_client)


# ─────────────────────────────────────────────────────
# create
# ─────────────────────────────────────────────────────

def test_create_adiciona_e_retorna_regra(repo, session):
    """Cenário: Criar regra de unicidade com sucesso"""
    mock_rule = MagicMock()

    with patch("source.repository.sqlite_quality_rule_repository.QualityRuleModel") as MockModel:
        MockModel.return_value = mock_rule

        result = repo.create(
            rule_type="unicity",
            target_table="vendas",
            target_column="id_pedido",
        )

    session.add.assert_called_once_with(mock_rule)
    session.commit.assert_called_once()
    session.refresh.assert_called_once_with(mock_rule)
    assert result is mock_rule


def test_create_repassa_atributos_opcionais(repo, session):
    """Verifica que min_value, max_value, enum_value e regex_expr são repassados ao modelo"""
    mock_rule = MagicMock()

    with patch("source.repository.sqlite_quality_rule_repository.QualityRuleModel") as MockModel:
        MockModel.return_value = mock_rule

        repo.create(
            rule_type="precision",
            target_table="produtos",
            target_column="preco",
            min_value=0.01,
            max_value=9999.99,
        )

        MockModel.assert_called_once_with(
            rule_type="precision",
            target_table="produtos",
            target_column="preco",
            min_value=0.01,
            max_value=9999.99,
            enum_value=None,
            regex_expr=None,
            is_active=True,
        )


# ─────────────────────────────────────────────────────
# read
# ─────────────────────────────────────────────────────

def test_read_retorna_regra_existente(repo, session):
    """Cenário: Buscar regra existente pelo ID"""
    rule = MagicMock(id=1)
    session.query.return_value.filter.return_value.first.return_value = rule

    result = repo.read(rule_id=1)

    assert result is rule


def test_read_retorna_none_quando_nao_encontrada(repo, session):
    """Cenário: Buscar regra inexistente pelo ID"""
    session.query.return_value.filter.return_value.first.return_value = None

    result = repo.read(rule_id=9999)

    assert result is None


# ─────────────────────────────────────────────────────
# read_by_target_table
# ─────────────────────────────────────────────────────

def test_read_by_table_com_filtro_is_active(repo, session):
    """Cenário: Buscar regras ativas de uma tabela"""
    rules = [MagicMock(is_active=True), MagicMock(is_active=True)]
    session.query.return_value.filter.return_value.all.return_value = rules

    result = repo.read_by_target_table(target_table="vendas", is_active=True)

    assert result == rules


def test_read_by_table_com_is_active_false(repo, session):
    """Cenário: Buscar regras inativas de uma tabela"""
    rules = [MagicMock(is_active=False)]
    session.query.return_value.filter.return_value.all.return_value = rules

    result = repo.read_by_target_table(target_table="vendas", is_active=False)

    assert result == rules


def test_read_by_table_sem_filtro_retorna_todas(repo, session):
    """Cenário: Buscar todas as regras de uma tabela sem filtro de status"""
    rules = [MagicMock(is_active=True), MagicMock(is_active=False)]
    session.query.return_value.filter.return_value.all.return_value = rules

    result = repo.read_by_target_table(target_table="vendas", is_active=None)

    assert result == rules


def test_read_by_table_sem_regras_retorna_lista_vazia(repo, session):
    """Cenário: Buscar regras de tabela sem registros"""
    session.query.return_value.filter.return_value.all.return_value = []

    result = repo.read_by_target_table(target_table="historico_acesso")

    assert result == []


# ─────────────────────────────────────────────────────
# update
# ─────────────────────────────────────────────────────

def test_update_regra_ativa_sucesso(repo, session):
    """Cenário: Atualizar regra ativa com sucesso"""
    rule_original = MagicMock(is_active=True)
    rule_atualizada = MagicMock(target_column="novo_campo")
    query_mock = session.query.return_value.filter.return_value
    query_mock.first.side_effect = [rule_original, rule_atualizada]

    result = repo.update(rule_id=1, new_rule_data={"target_column": "novo_campo"})

    query_mock.update.assert_called_once_with({"target_column": "novo_campo"})
    session.commit.assert_called_once()
    assert result is rule_atualizada


def test_update_regra_inativa_levanta_update_is_not_active(repo, session):
    """Cenário: Tentar atualizar regra inativa"""
    rule = MagicMock(is_active=False)
    session.query.return_value.filter.return_value.first.return_value = rule

    with pytest.raises(UpdateIsNotActive):
        repo.update(rule_id=2, new_rule_data={"target_column": "x"})


# ─────────────────────────────────────────────────────
# delete  (desativar)
# ─────────────────────────────────────────────────────

def test_delete_regra_ativa_sucesso(repo, session):
    """Cenário: Desativar regra ativa com sucesso"""
    rule_ativa = MagicMock(is_active=True)
    rule_inativa = MagicMock(is_active=False)
    query_mock = session.query.return_value.filter.return_value
    query_mock.first.side_effect = [rule_ativa, rule_inativa]

    result = repo.delete(rule_id=1)

    query_mock.update.assert_called_once_with({"is_active": False})
    session.commit.assert_called_once()
    assert result is rule_inativa


def test_delete_regra_ja_inativa_levanta_delete_is_not_active(repo, session):
    """Cenário: Tentar desativar regra que já está inativa"""
    rule = MagicMock(is_active=False)
    session.query.return_value.filter.return_value.first.return_value = rule

    with pytest.raises(DeleteIsNotActive):
        repo.delete(rule_id=2)


# ─────────────────────────────────────────────────────
# revert_delete  (ativar)
# ─────────────────────────────────────────────────────

def test_revert_delete_regra_inativa_sucesso(repo, session):
    """Cenário: Ativar regra inativa com sucesso"""
    rule_inativa = MagicMock(is_active=False)
    rule_ativa = MagicMock(is_active=True)
    query_mock = session.query.return_value.filter.return_value
    query_mock.first.side_effect = [rule_inativa, rule_ativa]

    result = repo.revert_delete(rule_id=2)

    query_mock.update.assert_called_once_with({"is_active": True})
    session.commit.assert_called_once()
    assert result is rule_ativa


def test_revert_delete_regra_ja_ativa_levanta_revert_delete_is_active(repo, session):
    """Cenário: Tentar ativar regra que já está ativa"""
    rule = MagicMock(is_active=True)
    session.query.return_value.filter.return_value.first.return_value = rule

    with pytest.raises(RevertDeleteIsActive):
        repo.revert_delete(rule_id=1)

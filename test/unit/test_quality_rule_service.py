import pytest
from unittest.mock import MagicMock
from sqlalchemy.exc import IntegrityError

from source.service.quality_rule_service import QualityRuleService
from source.model.quality_rule_model import QualityRuleModel
from source.exceptions.quality_rule_exceptions import (
    QualityRuleNotFound,
    QualityRuleExists,
    QualityRuleIsActivated,
    QualityRuleIsDeactivated,
)
from source.exceptions.repo_exceptions import (
    DeleteIsNotActive,
    RevertDeleteIsActive,
    UpdateIsNotActive,
)


def _make_rule(**kwargs) -> QualityRuleModel:
    defaults = dict(
        id=1,
        rule_type="unicity",
        target_table="vendas",
        target_column="id_pedido",
        min_value=None,
        max_value=None,
        enum_value=None,
        regex_expr=None,
        is_active=True,
    )
    defaults.update(kwargs)
    rule = MagicMock(spec=QualityRuleModel)
    for attr, value in defaults.items():
        setattr(rule, attr, value)
    return rule


@pytest.fixture
def repo():
    return MagicMock()


@pytest.fixture
def service(repo):
    return QualityRuleService(quality_rule_repo=repo)


# ─────────────────────────────────────────────────────
# create_rule
# ─────────────────────────────────────────────────────

def test_create_rule_unicity_sucesso(service, repo):
    """Cenário: Criar regra de unicidade com sucesso"""
    rule = _make_rule()
    repo.create.return_value = rule

    result = service.create_rule(
        rule_type="unicity",
        target_table="vendas",
        target_column="id_pedido",
    )

    repo.create.assert_called_once_with(
        rule_type="unicity",
        target_table="vendas",
        target_column="id_pedido",
        min_value=None,
        max_value=None,
        enum_value=None,
        regex_expr=None,
    )
    assert result.rule_type == "unicity"
    assert result.is_active is True


def test_create_rule_precision_com_intervalo(service, repo):
    """Cenário: Criar regra de precisão com intervalo numérico"""
    rule = _make_rule(rule_type="precision", target_column="preco", min_value=0.01, max_value=9999.99)
    repo.create.return_value = rule

    result = service.create_rule(
        rule_type="precision",
        target_table="vendas",
        target_column="preco",
        min_value=0.01,
        max_value=9999.99,
    )

    assert result.min_value == 0.01
    assert result.max_value == 9999.99


def test_create_rule_validity_com_regex(service, repo):
    """Cenário: Criar regra de validade com expressão regular"""
    rule = _make_rule(rule_type="validity", target_column="cpf", regex_expr=r"^\d{3}")
    repo.create.return_value = rule

    result = service.create_rule(
        rule_type="validity",
        target_table="vendas",
        target_column="cpf",
        regex_expr=r"^\d{3}",
    )

    assert result.regex_expr == r"^\d{3}"


def test_create_rule_duplicada_levanta_quality_rule_exists(service, repo):
    """Cenário: Tentar criar regra duplicada"""
    repo.create.side_effect = IntegrityError("", {}, Exception())

    with pytest.raises(QualityRuleExists):
        service.create_rule(
            rule_type="unicity",
            target_table="vendas",
            target_column="id_pedido",
        )


# ─────────────────────────────────────────────────────
# read_rule_by_id
# ─────────────────────────────────────────────────────

def test_read_rule_by_id_existente(service, repo):
    """Cenário: Buscar regra existente pelo ID"""
    rule = _make_rule(id=1)
    repo.read.return_value = rule

    result = service.read_rule_by_id(rule_id=1)

    repo.read.assert_called_once_with(1)
    assert result.id == 1


def test_read_rule_by_id_inexistente_levanta_not_found(service, repo):
    """Cenário: Buscar regra inexistente pelo ID"""
    repo.read.return_value = None

    with pytest.raises(QualityRuleNotFound):
        service.read_rule_by_id(rule_id=9999)


# ─────────────────────────────────────────────────────
# read_rule_by_target_table
# ─────────────────────────────────────────────────────

def test_read_rule_by_table_apenas_ativas(service, repo):
    """Cenário: Buscar regras ativas de uma tabela"""
    rules = [_make_rule(is_active=True), _make_rule(id=2, is_active=True)]
    repo.read_by_target_table.return_value = rules

    result = service.read_rule_by_target_table(target_table="vendas", is_active=True)

    repo.read_by_target_table.assert_called_once_with(target_table="vendas", is_active=True)
    assert all(r.is_active is True for r in result)


def test_read_rule_by_table_apenas_inativas(service, repo):
    """Cenário: Buscar regras inativas de uma tabela"""
    rules = [_make_rule(is_active=False)]
    repo.read_by_target_table.return_value = rules

    result = service.read_rule_by_target_table(target_table="vendas", is_active=False)

    repo.read_by_target_table.assert_called_once_with(target_table="vendas", is_active=False)
    assert all(r.is_active is False for r in result)


def test_read_rule_by_table_sem_filtro_retorna_todas(service, repo):
    """Cenário: Buscar todas as regras de uma tabela sem filtro de status"""
    rules = [_make_rule(is_active=True), _make_rule(id=2, is_active=False)]
    repo.read_by_target_table.return_value = rules

    result = service.read_rule_by_target_table(target_table="vendas", is_active=None)

    repo.read_by_target_table.assert_called_once_with(target_table="vendas", is_active=None)
    assert len(result) == 2


def test_read_rule_by_table_sem_regras_retorna_lista_vazia(service, repo):
    """Cenário: Buscar regras de uma tabela sem nenhuma regra cadastrada"""
    repo.read_by_target_table.return_value = []

    result = service.read_rule_by_target_table(target_table="historico_acesso")

    assert result == []


# ─────────────────────────────────────────────────────
# update_rule
# ─────────────────────────────────────────────────────

def test_update_rule_ativa_sucesso(service, repo):
    """Cenário: Atualizar regra ativa com sucesso"""
    original = _make_rule(id=1, target_column="id_pedido")
    updated = _make_rule(id=1, target_column="novo_campo")
    repo.read.return_value = original
    repo.update.return_value = updated

    result = service.update_rule(rule_id=1, new_rule_data={"target_column": "novo_campo"})

    repo.update.assert_called_once_with(rule_id=1, new_rule_data={"target_column": "novo_campo"})
    assert result.target_column == "novo_campo"


def test_update_rule_inexistente_levanta_not_found(service, repo):
    """Cenário: Tentar atualizar regra inexistente"""
    repo.read.return_value = None

    with pytest.raises(QualityRuleNotFound):
        service.update_rule(rule_id=9999, new_rule_data={"target_column": "x"})


def test_update_rule_inativa_levanta_is_deactivated(service, repo):
    """Cenário: Tentar atualizar regra inativa"""
    rule = _make_rule(id=2, is_active=False)
    repo.read.return_value = rule
    repo.update.side_effect = UpdateIsNotActive()

    with pytest.raises(QualityRuleIsDeactivated):
        service.update_rule(rule_id=2, new_rule_data={"target_column": "x"})


# ─────────────────────────────────────────────────────
# deactivate_by_id
# ─────────────────────────────────────────────────────

def test_deactivate_regra_ativa_sucesso(service, repo):
    """Cenário: Desativar regra ativa com sucesso"""
    rule_ativa = _make_rule(id=1, is_active=True)
    rule_inativa = _make_rule(id=1, is_active=False)
    repo.read.return_value = rule_ativa
    repo.delete.return_value = rule_inativa

    result = service.deactivate_by_id(rule_id=1)

    repo.delete.assert_called_once_with(rule_id=1)
    assert result.is_active is False


def test_deactivate_regra_inexistente_levanta_not_found(service, repo):
    """Cenário: Tentar desativar regra inexistente"""
    repo.read.return_value = None

    with pytest.raises(QualityRuleNotFound):
        service.deactivate_by_id(rule_id=9999)


def test_deactivate_regra_ja_inativa_levanta_is_deactivated(service, repo):
    """Cenário: Tentar desativar regra que já está inativa"""
    rule = _make_rule(id=2, is_active=False)
    repo.read.return_value = rule
    repo.delete.side_effect = DeleteIsNotActive()

    with pytest.raises(QualityRuleIsDeactivated):
        service.deactivate_by_id(rule_id=2)


# ─────────────────────────────────────────────────────
# activate_by_id
# ─────────────────────────────────────────────────────

def test_activate_regra_inativa_sucesso(service, repo):
    """Cenário: Ativar regra inativa com sucesso"""
    rule_inativa = _make_rule(id=2, is_active=False)
    rule_ativa = _make_rule(id=2, is_active=True)
    repo.read.return_value = rule_inativa
    repo.revert_delete.return_value = rule_ativa

    result = service.activate_by_id(rule_id=2)

    repo.revert_delete.assert_called_once_with(rule_id=2)
    assert result.is_active is True


def test_activate_regra_inexistente_levanta_not_found(service, repo):
    """Cenário: Tentar ativar regra inexistente"""
    repo.read.return_value = None

    with pytest.raises(QualityRuleNotFound):
        service.activate_by_id(rule_id=9999)


def test_activate_regra_ja_ativa_levanta_is_activated(service, repo):
    """Cenário: Tentar ativar regra que já está ativa"""
    rule = _make_rule(id=1, is_active=True)
    repo.read.return_value = rule
    repo.revert_delete.side_effect = RevertDeleteIsActive()

    with pytest.raises(QualityRuleIsActivated):
        service.activate_by_id(rule_id=1)

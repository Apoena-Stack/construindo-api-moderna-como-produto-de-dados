import pytest
from unittest.mock import MagicMock
from dependency_injector import providers
from fastapi.testclient import TestClient

from source.app import app
from source.service.interface.interface_quality_rule_service import IQualityRuleService
from source.exceptions.quality_rule_exceptions import (
    QualityRuleNotFound,
    QualityRuleExists,
    QualityRuleIsActivated,
    QualityRuleIsDeactivated,
)


def _rule_dict(**kwargs):
    base = {
        "id": 1,
        "rule_type": "unicity",
        "target_table": "vendas",
        "target_column": "id_pedido",
        "min_value": None,
        "max_value": None,
        "enum_value": None,
        "regex_expr": None,
        "is_active": True,
    }
    base.update(kwargs)
    return base


@pytest.fixture
def mock_service():
    return MagicMock(spec=IQualityRuleService)


@pytest.fixture
def client(mock_service):
    with app.container.services.quality_rule_service.override(providers.Object(mock_service)):
        yield TestClient(app)


# ─────────────────────────────────────────────────────
# POST /api/v1/rule/
# ─────────────────────────────────────────────────────

def test_post_rule_unicity_retorna_201(client, mock_service):
    """Cenário: Criar regra de unicidade com sucesso"""
    mock_service.create_rule.return_value = _rule_dict()

    response = client.post("/api/v1/rule/", json={
        "rule_type": "unicity",
        "target_table": "vendas",
        "target_column": "id_pedido",
    })

    assert response.status_code == 201
    data = response.json()
    assert data["rule_type"] == "unicity"
    assert data["is_active"] is True
    assert data["id"] == 1


def test_post_rule_precision_com_intervalo_retorna_201(client, mock_service):
    """Cenário: Criar regra de precisão com intervalo numérico"""
    mock_service.create_rule.return_value = _rule_dict(
        rule_type="precision", target_column="preco", min_value=0.01, max_value=9999.99
    )

    response = client.post("/api/v1/rule/", json={
        "rule_type": "precision",
        "target_table": "vendas",
        "target_column": "preco",
        "min_value": 0.01,
        "max_value": 9999.99,
    })

    assert response.status_code == 201
    data = response.json()
    assert data["min_value"] == 0.01
    assert data["max_value"] == 9999.99


def test_post_rule_validity_com_regex_retorna_201(client, mock_service):
    """Cenário: Criar regra de validade com expressão regular"""
    mock_service.create_rule.return_value = _rule_dict(
        rule_type="validity", target_column="cpf", regex_expr=r"^\d{3}"
    )

    response = client.post("/api/v1/rule/", json={
        "rule_type": "validity",
        "target_table": "vendas",
        "target_column": "cpf",
        "regex_expr": r"^\d{3}",
    })

    assert response.status_code == 201
    assert response.json()["regex_expr"] == r"^\d{3}"


def test_post_rule_duplicada_retorna_409(client, mock_service):
    """Cenário: Tentar criar regra duplicada"""
    mock_service.create_rule.side_effect = QualityRuleExists("Regra já existe.")

    response = client.post("/api/v1/rule/", json={
        "rule_type": "unicity",
        "target_table": "vendas",
        "target_column": "id_pedido",
    })

    assert response.status_code == 409


def test_post_rule_schema_invalido_retorna_422(client, mock_service):
    """Cenário: Tentar criar regra de unicidade com parâmetros extras não permitidos"""
    response = client.post("/api/v1/rule/", json={
        "rule_type": "unicity",
        "target_table": "vendas",
        "target_column": "id_pedido",
        "min_value": 10.0,
    })

    assert response.status_code == 422
    mock_service.create_rule.assert_not_called()


# ─────────────────────────────────────────────────────
# GET /api/v1/rule/{rule_id}
# ─────────────────────────────────────────────────────

def test_get_rule_por_id_existente_retorna_200(client, mock_service):
    """Cenário: Buscar regra existente pelo ID"""
    mock_service.read_rule_by_id.return_value = _rule_dict()

    response = client.get("/api/v1/rule/1")

    assert response.status_code == 200
    mock_service.read_rule_by_id.assert_called_once_with(rule_id=1)


def test_get_rule_por_id_inexistente_retorna_404(client, mock_service):
    """Cenário: Buscar regra inexistente pelo ID"""
    mock_service.read_rule_by_id.side_effect = QualityRuleNotFound("Regra 9999 não encontrada.")

    response = client.get("/api/v1/rule/9999")

    assert response.status_code == 404


# ─────────────────────────────────────────────────────
# GET /api/v1/rule/table/{target_table}
# ─────────────────────────────────────────────────────

def test_get_rules_por_tabela_retorna_200(client, mock_service):
    """Cenário: Buscar regras ativas de uma tabela"""
    mock_service.read_rule_by_target_table.return_value = [_rule_dict(), _rule_dict(id=2)]

    response = client.get("/api/v1/rule/table/vendas?is_active=true")

    assert response.status_code == 200
    assert len(response.json()) == 2
    mock_service.read_rule_by_target_table.assert_called_once_with(
        target_table="vendas", is_active=True
    )


def test_get_rules_por_tabela_sem_filtro_retorna_200(client, mock_service):
    """Cenário: Buscar todas as regras de uma tabela sem filtro de status"""
    mock_service.read_rule_by_target_table.return_value = []

    response = client.get("/api/v1/rule/table/historico_acesso")

    assert response.status_code == 200
    mock_service.read_rule_by_target_table.assert_called_once_with(
        target_table="historico_acesso", is_active=None
    )


# ─────────────────────────────────────────────────────
# PUT /api/v1/rule/{rule_id}
# ─────────────────────────────────────────────────────

def test_put_rule_ativa_retorna_201(client, mock_service):
    """Cenário: Atualizar regra ativa com sucesso"""
    mock_service.update_rule.return_value = _rule_dict(target_column="nova_coluna")

    response = client.put("/api/v1/rule/1", json={
        "rule_type": "unicity",
        "target_table": "vendas",
        "target_column": "nova_coluna",
    })

    assert response.status_code == 201
    assert response.json()["target_column"] == "nova_coluna"


def test_put_rule_inexistente_retorna_404(client, mock_service):
    """Cenário: Tentar atualizar regra inexistente"""
    mock_service.update_rule.side_effect = QualityRuleNotFound("Regra 9999 não encontrada.")

    response = client.put("/api/v1/rule/9999", json={
        "rule_type": "unicity",
        "target_table": "vendas",
        "target_column": "id_pedido",
    })

    assert response.status_code == 404


def test_put_rule_inativa_retorna_409(client, mock_service):
    """Cenário: Tentar atualizar regra inativa"""
    mock_service.update_rule.side_effect = QualityRuleIsDeactivated("Regra 2 está inativa.")

    response = client.put("/api/v1/rule/2", json={
        "rule_type": "unicity",
        "target_table": "vendas",
        "target_column": "id_pedido",
    })

    assert response.status_code == 409


# ─────────────────────────────────────────────────────
# PATCH /api/v1/rule/{rule_id}
# ─────────────────────────────────────────────────────

def test_patch_desativar_regra_ativa_retorna_200(client, mock_service):
    """Cenário: Desativar regra ativa com sucesso"""
    mock_service.deactivate_by_id.return_value = _rule_dict(is_active=False)

    response = client.patch("/api/v1/rule/1?is_active=false")

    assert response.status_code == 200
    mock_service.deactivate_by_id.assert_called_once_with(rule_id=1)


def test_patch_ativar_regra_inativa_retorna_200(client, mock_service):
    """Cenário: Ativar regra inativa com sucesso"""
    mock_service.activate_by_id.return_value = _rule_dict(is_active=True)

    response = client.patch("/api/v1/rule/2?is_active=true")

    assert response.status_code == 200
    mock_service.activate_by_id.assert_called_once_with(rule_id=2)


def test_patch_desativar_regra_ja_inativa_retorna_409(client, mock_service):
    """Cenário: Tentar desativar regra que já está inativa"""
    mock_service.deactivate_by_id.side_effect = QualityRuleIsDeactivated("Regra 2 já está inativada.")

    response = client.patch("/api/v1/rule/2?is_active=false")

    assert response.status_code == 409


def test_patch_ativar_regra_ja_ativa_retorna_409(client, mock_service):
    """Cenário: Tentar ativar regra que já está ativa"""
    mock_service.activate_by_id.side_effect = QualityRuleIsActivated("Regra 1 já está ativada.")

    response = client.patch("/api/v1/rule/1?is_active=true")

    assert response.status_code == 409


def test_patch_ativar_regra_inexistente_retorna_404(client, mock_service):
    """Cenário: Tentar ativar regra inexistente"""
    mock_service.activate_by_id.side_effect = QualityRuleNotFound("Regra 9999 não encontrada.")

    response = client.patch("/api/v1/rule/9999?is_active=true")

    assert response.status_code == 404


def test_patch_desativar_regra_inexistente_retorna_404(client, mock_service):
    """Cenário: Tentar desativar regra inexistente"""
    mock_service.deactivate_by_id.side_effect = QualityRuleNotFound("Regra 9999 não encontrada.")

    response = client.patch("/api/v1/rule/9999?is_active=false")

    assert response.status_code == 404

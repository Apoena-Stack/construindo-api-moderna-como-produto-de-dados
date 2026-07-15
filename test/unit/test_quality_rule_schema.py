import pytest
from pydantic import ValidationError

from source.schema.quality_rule_schema import QualityRuleSchema


# ─────────────────────────────────────────────────────
# Cenários: criação válida por tipo de regra
# ─────────────────────────────────────────────────────

def test_schema_unicity_valido():
    """Cenário: Criar regra de unicidade com sucesso"""
    schema = QualityRuleSchema(
        rule_type="unicity",
        target_table="vendas",
        target_column="id_pedido",
    )
    assert schema.rule_type == "unicity"
    assert schema.min_value is None
    assert schema.max_value is None
    assert schema.enum_value is None
    assert schema.regex_expr is None


def test_schema_completeness_valido():
    """Cenário: Criar regra de completude com sucesso"""
    schema = QualityRuleSchema(
        rule_type="completeness",
        target_table="clientes",
        target_column="email",
    )
    assert schema.rule_type == "completeness"


def test_schema_precision_com_intervalo_numerico():
    """Cenário: Criar regra de precisão com intervalo numérico"""
    schema = QualityRuleSchema(
        rule_type="precision",
        target_table="produtos",
        target_column="preco",
        min_value=0.01,
        max_value=9999.99,
    )
    assert schema.min_value == 0.01
    assert schema.max_value == 9999.99
    assert schema.enum_value is None


def test_schema_precision_com_enum_value():
    """Cenário: Criar regra de precisão com lista de valores permitidos"""
    schema = QualityRuleSchema(
        rule_type="precision",
        target_table="pedidos",
        target_column="status",
        enum_value=["pendente", "pago", "cancelado"],
    )
    assert schema.enum_value == ["pendente", "pago", "cancelado"]
    assert schema.min_value is None
    assert schema.max_value is None


def test_schema_validity_com_regex_valida():
    """Cenário: Criar regra de validade com expressão regular"""
    schema = QualityRuleSchema(
        rule_type="validity",
        target_table="clientes",
        target_column="cpf",
        regex_expr=r"^\d{3}\.\d{3}\.\d{3}-\d{2}$",
    )
    assert schema.regex_expr == r"^\d{3}\.\d{3}\.\d{3}-\d{2}$"


# ─────────────────────────────────────────────────────
# Cenários: parâmetros inválidos por tipo de regra
# ─────────────────────────────────────────────────────

def test_schema_unicity_rejeita_parametros_extras():
    """Cenário: Tentar criar regra de unicidade com parâmetros extras não permitidos"""
    with pytest.raises(ValidationError):
        QualityRuleSchema(
            rule_type="unicity",
            target_table="vendas",
            target_column="id_pedido",
            min_value=10.0,
        )


def test_schema_completeness_rejeita_parametros_extras():
    """Cenário: Regra de completude não aceita parâmetros adicionais"""
    with pytest.raises(ValidationError):
        QualityRuleSchema(
            rule_type="completeness",
            target_table="clientes",
            target_column="email",
            enum_value=["a", "b"],
        )


def test_schema_precision_sem_parametros_obrigatorios():
    """Cenário: Tentar criar regra de precisão sem os parâmetros obrigatórios"""
    with pytest.raises(ValidationError):
        QualityRuleSchema(
            rule_type="precision",
            target_table="produtos",
            target_column="preco",
        )


def test_schema_precision_com_apenas_min_value():
    """Cenário: precision com apenas min_value (falta max_value) é inválido"""
    with pytest.raises(ValidationError):
        QualityRuleSchema(
            rule_type="precision",
            target_table="produtos",
            target_column="preco",
            min_value=10.0,
        )


def test_schema_validity_sem_regex_expr():
    """Cenário: Tentar criar regra de validade sem expressão regular"""
    with pytest.raises(ValidationError):
        QualityRuleSchema(
            rule_type="validity",
            target_table="clientes",
            target_column="cpf",
        )


def test_schema_validity_com_regex_invalida():
    """Cenário: Tentar criar regra de validade com expressão regular inválida"""
    with pytest.raises(ValidationError):
        QualityRuleSchema(
            rule_type="validity",
            target_table="clientes",
            target_column="cpf",
            regex_expr="[abc",
        )

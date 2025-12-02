from pydantic import BaseModel, model_validator
from enum import Enum
from typing import Optional
import re


class RuleTypeEnum(str, Enum):
    unicity = "unicity"
    precision = "precision"
    validity = "validity"
    completeness = "completeness"

class QualityRuleSchema(BaseModel):
    rule_type: RuleTypeEnum
    target_table: str
    target_column: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    enum_value: Optional[list[str]] = None
    regex_expr: Optional[str] = None

    @property
    def provided_params(self) -> set[str]:
        """Retorna os parâmetros opcionais que foram preenchidos."""
        return {
            name
            for name, value in {
                "min_value": self.min_value,
                "max_value": self.max_value,
                "enum_value": self.enum_value,
                "regex_expr": self.regex_expr,
            }.items()
            if value is not None
        }

    @classmethod
    def _check_simple_rule(cls, instance):
        if instance.provided_params:
            raise ValueError(f"Regra do tipo '{instance.rule_type.value}' não aceita parâmetros adicionais: {instance.provided_params}")

    @classmethod
    def _validate_regex(cls, pattern: str):
        try:
            re.compile(pattern)
        except re.error as e:
            raise ValueError(f"Regex inválida: {e}")

    @classmethod
    def _check_precision(cls, instance: "QualityRuleSchema"):
        params = instance.provided_params
        if params in ({"min_value", "max_value"}, {"enum_value"}):
            return
        raise ValueError(
            "A regra 'precision' precisa de ('min_value' e 'max_value') ou apenas 'enum_value'."
        )

    @classmethod
    def _check_validity(cls, instance: "QualityRuleSchema"):
        if instance.provided_params != {"regex_expr"}:
            raise ValueError("A regra 'validity' requer apenas o parâmetro 'regex_expr'.")
        cls._validate_regex(instance.regex_expr)
    
    @model_validator(mode="after")
    def check_rule_params(self):
        match self.rule_type:
            case RuleTypeEnum.precision:
                self._check_precision(self)
            case RuleTypeEnum.unicity:
                self._check_simple_rule(self)
            case RuleTypeEnum.validity:
                self._check_validity(self)
            case RuleTypeEnum.completeness:
                self._check_simple_rule(self)
        return self

if __name__ == "__main__":
    quality_rule_schema = QualityRuleSchema(
        rule_type="validity",
        target_table="test",
        target_column="columnA",
        regex_expr="iury"
    )
    print(quality_rule_schema)


class QualityRuleUpdateSchema(QualityRuleSchema):
    rule_type: Optional[RuleTypeEnum] = None
    target_table: Optional[str] = None
    target_column: Optional[str] = None
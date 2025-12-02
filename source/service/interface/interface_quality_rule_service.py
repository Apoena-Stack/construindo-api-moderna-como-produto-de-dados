from abc import ABC, abstractmethod
from source.model.quality_rule_model import QualityRuleModel


class IQualityRuleService(ABC):
    """
        Interface para repositório da entidade regra de qualidade.
    """

    @abstractmethod
    def create_rule(self,
                    rule_type: str,
                    target_table: str,
                    target_column: str,
                    min_value: float | None = None,
                    max_value: float | None = None,
                    enum_value: str | None = None,
                    regex_expr: str | None = None) -> QualityRuleModel:
        pass

    @abstractmethod
    def read_rule_by_id(self,
             rule_id: int) -> QualityRuleModel:
        pass
    
    @abstractmethod
    def read_rule_by_target_table(self,
                             target_table: str,
                             is_active: bool | None = True) -> list[QualityRuleModel]:
        pass

    @abstractmethod
    def update_rule(self,
               rule_id: int,
               new_rule_data: dict) -> QualityRuleModel:
        pass

    @abstractmethod
    def deactivate_by_id(self,
                         rule_id: int) -> QualityRuleModel:
        pass

    @abstractmethod
    def activate_by_id(self,
                       rule_id: int) -> QualityRuleModel:
        pass
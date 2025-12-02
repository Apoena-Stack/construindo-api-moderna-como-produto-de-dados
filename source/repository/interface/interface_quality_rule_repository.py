from abc import ABC, abstractmethod
from source.model.quality_rule_model import QualityRuleModel


class IQualityRuleRepository(ABC):
    """
        Interface para repositório da entidade regra de qualidade.
    """

    @abstractmethod
    def create(self,
               rule_type: str,
               target_table: str,
               target_column: str,
               min_value: float | None = None,
               max_value: float | None = None,
               enum_value: str | None = None,
               regex_expr: str | None = None) -> QualityRuleModel:
        """_summary_

        Args:
            rule_type (str): _description_
            target_table (str): _description_
            target_column (str): _description_
            min_value (float | None, optional): _description_. Defaults to None.
            max_value (float | None, optional): _description_. Defaults to None.
            enum_value (str | None, optional): _description_. Defaults to None.
            regex_expr (str | None, optional): _description_. Defaults to None.

        Returns:
            QualityRuleModel: _description_
        """
        pass

    @abstractmethod
    def read(self,
             rule_id: int) -> QualityRuleModel:
        pass
    
    @abstractmethod
    def read_by_target_table(self,
                             target_table: str,
                             is_active: bool | None = True) -> list[QualityRuleModel]:
        pass

    @abstractmethod
    def update(self,
               rule_id: int,
               new_rule_data: dict) -> QualityRuleModel:
        pass

    @abstractmethod
    def delete(self,
               rule_id: int) -> QualityRuleModel:
        pass

    @abstractmethod
    def revert_delete(self,
                      rule_id: int) -> QualityRuleModel:
        pass
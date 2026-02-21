from sqlalchemy.exc import IntegrityError

from source.service.interface.interface_quality_rule_service import IQualityRuleService
from source.repository.interface.interface_quality_rule_repository import IQualityRuleRepository
from source.model.quality_rule_model import QualityRuleModel
from source.exceptions.quality_rule_exceptions import (QualityRuleNotFound,
                                                       QualityRuleExists,
                                                       QualityRuleIsActivated,
                                                       QualityRuleIsDeactivated)
from source.exceptions.repo_exceptions import RevertDeleteIsActive, DeleteIsNotActive, UpdateIsNotActive


class QualityRuleService(IQualityRuleService):
    def __init__(self, quality_rule_repo: IQualityRuleRepository):
        self.quality_rule_repo = quality_rule_repo

    def create_rule(self,
                    rule_type: str,
                    target_table: str,
                    target_column: str,
                    min_value: float | None = None,
                    max_value: float | None = None,
                    enum_value: str | None = None,
                    regex_expr: str | None = None) -> QualityRuleModel:
        try:
            # Tabela tem que existir...
            # Coluna tem que existir...
            # Você implementaria um check utilizando um repository especifico para tabela e coluna.
            rule = self.quality_rule_repo.create(
                rule_type = rule_type,
                target_table = target_table,
                target_column = target_column,
                min_value = min_value,
                max_value = max_value,
                enum_value = enum_value,
                regex_expr = regex_expr
            )
            return rule
        except IntegrityError as error:
            raise QualityRuleExists(f"Regra do tipo {rule_type} na tabela {target_table} para coluna {target_column} já existe.")
        except Exception as error:
            raise error
        

    def read_rule_by_id(self,
             rule_id: int) -> QualityRuleModel:
        
        rule = self.quality_rule_repo.read(rule_id)
        if not rule:
            raise QualityRuleNotFound(f"Regra {rule_id} não encontrada.")
        return rule
    
    def read_rule_by_target_table(self,
                                    target_table: str,
                                    is_active: bool | None = True) -> list[QualityRuleModel]:
        rules = self.quality_rule_repo.read_by_target_table(target_table = target_table, 
                                                            is_active = is_active)
        return rules
    
    def update_rule(self,
               rule_id: int,
               new_rule_data: dict) -> QualityRuleModel:
        try:
            rule = self.quality_rule_repo.read(rule_id=rule_id)
            
            if not rule:
                raise QualityRuleNotFound(f"Regra {rule_id} não encontrada.")
            
            rule = self.quality_rule_repo.update(rule_id=rule_id,
                                                new_rule_data=new_rule_data)
            return rule
        except UpdateIsNotActive:
            raise QualityRuleIsDeactivated(f"Regra {rule_id} está inativa. Certifique-se de ativar a regra antes de atualizá-la.")
        except Exception as error:
            raise error
    
    def deactivate_by_id(self,
                        rule_id: int) -> QualityRuleModel:
        try:
            rule = self.quality_rule_repo.read(rule_id=rule_id)
            
            if not rule:
                raise QualityRuleNotFound(f"Regra {rule_id} não encontrada.")

            rule = self.quality_rule_repo.delete(rule_id=rule_id)
            
            return rule
        except DeleteIsNotActive:
            raise QualityRuleIsDeactivated(f"Regra {rule_id} já está inativada.")
        except Exception as error:
            raise error
    
    def activate_by_id(self, rule_id: int) -> QualityRuleModel:
        try:
            rule = self.quality_rule_repo.read(rule_id=rule_id)
            
            if not rule:
                raise QualityRuleNotFound(f"Regra {rule_id} não encontrada.")

            rule = self.quality_rule_repo.revert_delete(rule_id=rule_id)

            return rule
        except RevertDeleteIsActive:
            raise QualityRuleIsActivated(f"Regra {rule_id} já está ativada.")
        except Exception as error:
            raise error
        
if __name__ == "__main__":
    from source.repository.sqlite_quality_rule_repository import SQLiteQualityRuleRepository

    sqlite_quality_rule_repo = SQLiteQualityRuleRepository()
    quality_rule_service = QualityRuleService(quality_rule_repo=sqlite_quality_rule_repo)
    # print(quality_rule_service.read_rule_by_id(rule_id=10))
    # print(quality_rule_service.read_rule_by_target_table(target_table="test"))
    # print(quality_rule_service.update_rule(rule_id=2, new_rule_data={"target_column": "columnD"}))
    print(quality_rule_service.deactivate_by_id(rule_id=2))
    # print(quality_rule_service.activate_by_id(rule_id=2))
    # print(quality_rule_service.create_rule(
    #     rule_type = "unicity",
    #     target_table = "test",
    #     target_column = "columnB"
    # ))
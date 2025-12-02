from source.repository.interface.interface_quality_rule_repository import IQualityRuleRepository
from source.model.quality_rule_model import QualityRuleModel
from source.gateway.sqlite_client import SQLiteClient
from source.exceptions.repo_exceptions import RevertDeleteIsActive, DeleteIsNotActive, UpdateIsNotActive


class SQLiteQualityRuleRepository(IQualityRuleRepository):
    def __init__(self):
        self.sqlite_client = SQLiteClient()

    def create(self,
               rule_type: str,
               target_table: str,
               target_column: str,
               min_value: float | None = None,
               max_value: float | None = None,
               enum_value: str | None = None,
               regex_expr: str | None = None) -> QualityRuleModel:

        with self.sqlite_client._get_session() as db_session:
            rule = QualityRuleModel(
                rule_type = rule_type,
                target_table = target_table,
                target_column = target_column,
                min_value = min_value,
                max_value = max_value,
                enum_value = enum_value,
                regex_expr = regex_expr,
                is_active = True
            )
            db_session.add(rule)
            db_session.commit()
            db_session.refresh(rule)
            return rule
    
    def read(self,
             rule_id: int) -> QualityRuleModel:
        with self.sqlite_client._get_session() as db_session:
            rule = (db_session
                     .query(QualityRuleModel)
                     .filter(QualityRuleModel.id == rule_id)
                     .first())
            return rule
    
    def read_by_target_table(self,
                             target_table: str,
                             is_active: bool | None = True) -> list[QualityRuleModel]:
        with self.sqlite_client._get_session() as db_session:
            query = db_session.query(QualityRuleModel)
            if is_active is not None:
                query = query.filter(QualityRuleModel.target_table == target_table,
                                     QualityRuleModel.is_active == is_active)
            else:
                query = query.filter(QualityRuleModel.target_table == target_table)
            return query.all()

    def update(self,
               rule_id: int,
               new_rule_data: dict) -> QualityRuleModel:
        with self.sqlite_client._get_session() as db_session:
            query = (db_session
                     .query(QualityRuleModel)
                     .filter(QualityRuleModel.id == rule_id)
            )

            rule = query.first()
            
            if not rule.is_active:
                raise UpdateIsNotActive(f"Regra {rule_id} está inativa. Só é possível atualizar regras ativas.")
            
            query.update(
                {key: value for key, value in new_rule_data.items() if value is not None and key != "is_active"}
            )

            db_session.commit()
            
            rule = query.first()

            return rule

    def delete(self,
               rule_id: int) -> QualityRuleModel:
         with self.sqlite_client._get_session() as db_session:
            query = db_session.query(QualityRuleModel).filter(QualityRuleModel.id == rule_id)
            rule = query.first()

            if not rule.is_active:
                raise DeleteIsNotActive(f"Rule {rule_id} is deactivated.")
            
            query.update({"is_active": False})
            db_session.commit()

            rule = query.first()
            return rule

    def revert_delete(self,
                      rule_id: int) -> QualityRuleModel:
        with self.sqlite_client._get_session() as db_session:
            query = db_session.query(QualityRuleModel).filter(QualityRuleModel.id == rule_id)
            rule = query.first()

            if rule.is_active:
                raise RevertDeleteIsActive(f"Rule {rule_id} is activated.")
            
            query.update({"is_active": True})
            db_session.commit()

            rule = query.first()
            return rule

if __name__ == "__main__":
    sqlite_quality_rule_repo = SQLiteQualityRuleRepository()
    print(sqlite_quality_rule_repo.create(
        rule_type = "unicity",
        target_table = "test",
        target_column = "columnB"
    ))
    # print(sqlite_quality_rule_repo.read(rule_id=1))
    # print(sqlite_quality_rule_repo.read_by_target_table(target_table="test", is_active=None))
    # print(sqlite_quality_rule_repo.update(rule_id=2, new_rule_data={"target_column": "columnE", "is_active": False}))
    # print(sqlite_quality_rule_repo.delete(rule_id=2))
    # print(sqlite_quality_rule_repo.revert_delete(rule_id=2))
    # print(sqlite_quality_rule_repo.read(rule_id=10))
from sqlalchemy import PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy import Column, String, Float, JSON, Integer, Boolean

from source.gateway.sqlite_client import SQLiteBase


class QualityRuleModel(SQLiteBase):
    __tablename__ = "quality_rule"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_quality_rule"),
        UniqueConstraint("rule_type", "target_table", "target_column", name="unique_rule")
    )

    id = Column(Integer, primary_key = True, autoincrement = True)
    rule_type = Column(String, nullable = False)
    target_table = Column(String, nullable = False)
    target_column = Column(String, nullable = False)
    min_value = Column(Float, nullable = True)
    max_value = Column(Float, nullable = True)
    enum_value = Column(JSON, nullable = True)
    regex_expr = Column(String, nullable = True)
    is_active = Column(Boolean, nullable = False)

    def __repr__(self) -> str:
        return f"""QualityRuleModel(
            id={self.id},
            rule_type={self.rule_type},
            target_table={self.target_table},
            target_column={self.target_column},
            min_value={self.min_value},
            max_value={self.max_value},
            enum_value={self.enum_value},
            regex_expr={self.regex_expr},
            is_active={self.is_active})
        )"""
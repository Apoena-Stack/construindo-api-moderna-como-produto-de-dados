from source.schema.quality_rule_schema import QualityRuleSchema


class QualityRuleObjectResponse(QualityRuleSchema):
    id: int
    is_active: bool
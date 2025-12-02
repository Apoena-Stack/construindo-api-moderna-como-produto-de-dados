class QualityRuleError(Exception):
    pass

class QualityRuleIsDeactivated(QualityRuleError):
    pass

class QualityRuleIsActivated(QualityRuleError):
    pass

class QualityRuleNotFound(QualityRuleError):
    pass

class QualityRuleExists(QualityRuleError):
    pass
from dependency_injector import containers, providers
from source.service.quality_rule_service import QualityRuleService
from source.service.interface.interface_quality_rule_service import IQualityRuleService
from source.repository import RepositoryContainer

class ServiceContainer(containers.DeclarativeContainer):
    repositories = providers.Container(RepositoryContainer)

    quality_rule_service: IQualityRuleService = providers.Factory(
        QualityRuleService, 
        quality_rule_repo=repositories.sqlite_quality_rule_repository
    )
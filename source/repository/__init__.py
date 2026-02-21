from dependency_injector import containers, providers
from source.repository.sqlite_quality_rule_repository import SQLiteQualityRuleRepository
from source.repository.interface.interface_quality_rule_repository import IQualityRuleRepository
from source.gateway import GatewayContainer

class RepositoryContainer(containers.DeclarativeContainer):
    gateway = providers.Container(GatewayContainer)
    sqlite_quality_rule_repository: IQualityRuleRepository = providers.Factory(
        SQLiteQualityRuleRepository,
        sqlite_client=gateway.sqlite_client
    )
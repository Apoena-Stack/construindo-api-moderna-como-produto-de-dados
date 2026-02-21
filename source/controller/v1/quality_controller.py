from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from dependency_injector.wiring import inject, Provide

from source.service.interface.interface_quality_rule_service import IQualityRuleService
from source.service.quality_rule_service import QualityRuleService
from source.repository.sqlite_quality_rule_repository import SQLiteQualityRuleRepository
from source.exceptions.quality_rule_exceptions import QualityRuleNotFound, QualityRuleExists
from source.schema.quality_rule_schema import QualityRuleSchema
from source.schema.response_schema import QualityRuleObjectResponse
from source.config.containers import ApplicationContainer


class QualityController:
    router = APIRouter()
    
    @router.post("/rule/", status_code = 201, response_model = QualityRuleObjectResponse)
    @inject
    async def create_quality_rule(rule: QualityRuleSchema, quality_rule_service: IQualityRuleService = Depends(Provide[ApplicationContainer.services.quality_rule_service])):
        try:
            response = quality_rule_service.create_rule(**rule.dict())
            return response
        except QualityRuleExists as error:
            return JSONResponse(
                status_code = status.HTTP_409_CONFLICT,
                content = str(error)
            )
    
    @router.get("/rule/{rule_id}")
    @inject
    async def get_quality_rule(rule_id: int, quality_rule_service: IQualityRuleService = Depends(Provide[ApplicationContainer.services.quality_rule_service])):
        try:
            response = quality_rule_service.read_rule_by_id(rule_id=rule_id)
            return response
        except QualityRuleNotFound as error:
            return JSONResponse(
                status_code = status.HTTP_404_NOT_FOUND,
                content = str(error)
            )
        
    @router.get("/rule/table/{target_table}")
    @inject
    def get_rules_by_table(target_table: str, is_active: bool = None, quality_rule_service: IQualityRuleService = Depends(Provide[ApplicationContainer.services.quality_rule_service])):
        return quality_rule_service.read_rule_by_target_table(target_table=target_table, is_active=is_active)

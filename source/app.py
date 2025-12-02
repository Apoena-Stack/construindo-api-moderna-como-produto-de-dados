from fastapi import FastAPI

from source.controller.v1.quality_controller import QualityController

app = FastAPI()

app.include_router(QualityController.router, prefix="/api/v1", tags=["quality_rule"])
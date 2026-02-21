from fastapi import FastAPI

from source.controller.v1.quality_controller import QualityController
from source.config.containers import ApplicationContainer

app = FastAPI()
container = ApplicationContainer.wire_controllers()
app.container = container

app.include_router(QualityController.router, prefix="/api/v1", tags=["quality_rule"])
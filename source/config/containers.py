from dependency_injector import containers, providers
from source.service import ServiceContainer

class ApplicationContainer(containers.DeclarativeContainer):
    services = providers.Container(ServiceContainer)

    @classmethod
    def wire_controllers(cls):
        container = cls()

        container.wire(modules=["source.controller.v1.quality_controller"])

        return container
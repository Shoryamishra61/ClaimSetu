"""Shared dependencies for the service layer.

Assembled once at application start and passed explicitly. No module-level
singletons and no service locator: a test builds its own context against a
temporary database and its own registries, which is what makes the API tests fast
and independent.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..adapters.mock_dealer_registry import MockDealerRegistry
from ..adapters.mock_form29c_adapter import MockForm29CAdapter
from ..adapters.mock_vehicle_registry import MockVehicleRegistry
from ..config import Settings
from ..db import Database
from ..domain.policies import registry
from ..domain.policy_types import PolicyDefinition
from .events import EventBus


@dataclass(frozen=True, slots=True)
class ServiceContext:
    settings: Settings
    db: Database
    vehicles: MockVehicleRegistry
    dealers: MockDealerRegistry
    adapter: MockForm29CAdapter
    policy: PolicyDefinition
    events: EventBus

    @classmethod
    def build(cls, settings: Settings) -> ServiceContext:
        database = Database(settings.database_path)
        database.initialise()
        return cls(
            settings=settings,
            db=database,
            vehicles=MockVehicleRegistry(),
            dealers=MockDealerRegistry(),
            adapter=MockForm29CAdapter(),
            # Routed through the registry, which refuses anything not in force, so
            # the running instance cannot end up evaluating draft rules.
            policy=registry.get(settings.policy_version),
            events=EventBus(),
        )

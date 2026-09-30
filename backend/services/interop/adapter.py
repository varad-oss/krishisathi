"""Country adapter contract.

    national data sources -> CountryAdapter -> schema v1.0 objects -> /api/interoperability

A BRICS member joins by implementing CountryAdapter over its own sources (weather service, disease surveillance,
advisory records) and registering it. Domain services and the API stay unchanged. Adapters must publish only
aggregates that satisfy `privacy` and must label every value with its provenance kind.
"""
from datetime import date
from typing import Protocol, runtime_checkable

from models.interop_v1 import CropV1, DiseaseV1, ObservationV1, PrivacyV1, RiskSignalV1


@runtime_checkable
class CountryAdapter(Protocol):
    country_code: str          # ISO 3166-1 alpha-2
    name: str
    privacy: PrivacyV1

    def describe(self) -> dict:
        """Sources, coverage and limitations, for partners deciding how to use the signals."""

    async def crops(self) -> list[CropV1]: ...

    async def diseases(self) -> list[DiseaseV1]: ...

    async def weather_signals(self) -> list[RiskSignalV1]: ...

    async def observations(self, since: date) -> list[ObservationV1]: ...

    async def risk_signals(self, since: date) -> list[RiskSignalV1]: ...


_REGISTRY: dict[str, CountryAdapter] = {}


def register(adapter: CountryAdapter) -> None:
    if not isinstance(adapter, CountryAdapter):
        raise TypeError("adapter does not implement CountryAdapter")
    _REGISTRY[adapter.country_code] = adapter


def get(country_code: str) -> CountryAdapter | None:
    return _REGISTRY.get(country_code.upper())


def registered() -> list[CountryAdapter]:
    return list(_REGISTRY.values())

import asyncio
from functools import partial
from typing import cast

from geopy.geocoders import Nominatim
from geopy.location import Location
from src.application.interfaces import GeoLocator


class OSMGeoLocator(GeoLocator):
    def __init__(self) -> None:
        self._geolocator = Nominatim(user_agent="Stroy Bazar")

    async def get_region(self, lat: float, lng: float) -> str | None:
        location = cast(
            Location | None,
            await asyncio.to_thread(
                partial(self._geolocator.reverse, language="ru"), f"{lat}, {lng}"
            ),
        )

        if location is None:
            return None
        address: dict = location.raw.get("address", {})
        return address.get("state") or address.get("city")

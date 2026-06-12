"""Semantic World Identity Schemas."""

from pydantic import BaseModel, Field
from typing import List, Optional

class ZoneProfile(BaseModel):
    id: str
    name: str
    zone_type: str
    capacity: int = 1
    adjacent: List[str] = Field(default_factory=list)

class AmbienceProfile(BaseModel):
    time_of_day: str = "day"
    weather: str = "clear"
    crowd_density: float = 0.5
    noise_profile: str = "ambient"

class FormationRef(BaseModel):
    formation_id: str
    supported_zone_types: List[str] = Field(default_factory=list)

class PropRef(BaseModel):
    prop_id: str
    required: bool = False

class WorldConnection(BaseModel):
    target_world: str
    connection_type: str # walking_distance, road_connected, adjacent_market

class WorldProfile(BaseModel):
    id: str
    name: str
    archetype: str # commercial, residential, institutional
    description: str
    zones: List[ZoneProfile] = Field(default_factory=list)
    formations: List[FormationRef] = Field(default_factory=list)
    props: List[PropRef] = Field(default_factory=list)
    ambience: AmbienceProfile = Field(default_factory=AmbienceProfile)
    connected_worlds: List[WorldConnection] = Field(default_factory=list)

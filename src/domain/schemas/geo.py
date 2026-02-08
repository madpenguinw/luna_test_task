from pydantic import BaseModel, Field, model_validator


class GeoCircleParams(BaseModel):
    """Search within a radius (km) from a point."""

    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_km: float = Field(..., gt=0, le=1000)

    @property
    def radius_meters(self) -> float:
        return self.radius_km * 1000.0


class GeoRectParams(BaseModel):
    """Search within a bounding rectangle."""

    min_latitude: float = Field(..., ge=-90, le=90)
    max_latitude: float = Field(..., ge=-90, le=90)
    min_longitude: float = Field(..., ge=-180, le=180)
    max_longitude: float = Field(..., ge=-180, le=180)

    @model_validator(mode="after")
    def check_coordinates_order(self) -> "GeoRectParams":
        if self.min_latitude > self.max_latitude:
            raise ValueError("Minimum latitude must be less than or equal to maximum latitude.")
        return self

    @property
    def longitude_span(self) -> float:
        diff = self.max_longitude - self.min_longitude
        if diff < 0:
            diff += 360
        return diff

    @property
    def is_too_wide(self) -> bool:
        return self.longitude_span >= 180

    @property
    def crosses_antimeridian(self) -> bool:
        return self.min_longitude > self.max_longitude

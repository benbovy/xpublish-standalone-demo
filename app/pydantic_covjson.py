from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field


class I18NText(BaseModel):
    """Multi-language text."""

    __root__: Dict[str, str]

    # TODO: validate language keys?


class Category(BaseModel):
    id: str
    label: I18NText
    description: Optional[I18NText] = None


class CategoryEncoding(BaseModel):
    """Map category id to data value."""

    __root__: Dict[str, Union[int, List[int]]]

    # TODO: validate each encoding value mapped to only one category id


class ObservedProperty(BaseModel):
    id: Optional[str] = None
    label: I18NText
    description: Optional[I18NText] = None
    categories: Optional[List[Category]] = None


class Symbol(BaseModel):
    type: str = Field("http://www.opengis.net/def/uom/UCUM/", const=True)
    value: str


class Unit(BaseModel):
    id: Optional[str] = None
    label: Optional[I18NText] = None
    symbol: Optional[Union[str, Symbol]] = None

    # TODO: validate at least label or symbol defined


class Parameter(BaseModel):
    type: str = Field("Parameter", const=True)
    id: Optional[str] = None
    label: Optional[I18NText] = None
    description: Optional[I18NText] = None
    observed_property: ObservedProperty = Field(..., alias="observedProperty")
    category_encoding: Optional[CategoryEncoding] = None
    unit: Optional[Unit] = None

    # TODO: validate unit must be None if observed_property.categories is not None


class ReferenceSystem(BaseModel):
    type: str
    id: Optional[str] = None


class GeographicCRS(ReferenceSystem):
    type: str = Field("GeographicCRS", const=True)


class ProjectedCRS(ReferenceSystem):
    type: str = Field("ProjectedCRS", const=True)


class VerticalCRS(ReferenceSystem):
    type: str = Field("VerticalCRS", const=True)


class TemporalRS(ReferenceSystem):
    type: str = Field("TemporalRS", const=True)
    calendar: str = "Gregorian"


class Reference(BaseModel):
    coordinates: List[str]
    system: ReferenceSystem


class SpatialReference2D(Reference):
    coordinates: List[str] = ["x", "y"]
    system: ReferenceSystem = GeographicCRS(
        id="http://www.opengis.net/def/crs/OGC/1.3/CRS84"
    )


class SpatialReference3D(Reference):
    coordinates: List[str] = ["x", "y", "z"]
    system: ReferenceSystem = GeographicCRS(
        id="http://www.opengis.net/def/crs/EPSG/0/4979"
    )


class TemporalReference(Reference):
    coordinates: List[str] = ["t"]
    system: ReferenceSystem = TemporalRS()


class AxisDataType(str, Enum):
    PRIMITIVE = "primitive"
    TUPLE = "tuple"
    POLYGON = "polygon"


NumType = Union[int, float]
# str is for date/time values
StrNumType = Union[str, NumType]

PrimitiveValuesType = List[StrNumType]
TupleValuesType = List[List[StrNumType]]
PolygonValuesType = List[List[List[NumType]]]

AxisValuesType = Union[PrimitiveValuesType, TupleValuesType, PolygonValuesType]


class Axis(BaseModel):
    values: Optional[AxisValuesType] = Field(None, min_items=1)
    bounds: Optional[PrimitiveValuesType] = Field(None, min_items=2)
    start: Optional[NumType] = None
    stop: Optional[NumType] = None
    num: Optional[int] = None
    datatype: AxisDataType = Field(AxisDataType.PRIMITIVE, alias="dataType")
    coordinates: Optional[List[str]] = Field(None, min_items=1)

    # TODO: validate if bounds is set len(bounds) == 2* len(values)
    # TODO: validate if values not set -> start, stop and num must be set
    # TODO: validate values nested list level depending on datatype


class DomainType(str, Enum):
    GRID = "Grid"
    VERTICAL_PROFILE = "VerticalProfile"
    TRAJECTORY = "Trajectory"

    # TODO: add more domain types https://covjson.org/domain-types/


class Domain(BaseModel):
    type: str = Field("Domain", const=True)
    domain_type: Optional[DomainType] = Field(None, alias="domainType")
    axes: Dict[str, Axis]
    referencing: Reference

    # TODO: make referencing optional
    # TODO: validate referencing must be set if not part of or not defined in coverage collection


class NdArrayDataType(str, Enum):
    INTERGER = "integer"
    FLOAT = "float"
    STRING = "string"


class NdArray(BaseModel):
    type: str = Field("NdArray", const=True)
    datatype: NdArrayDataType = Field(..., alias="dataType")
    shape: List[int] = Field(default_factory=list)
    axis_names: List[str] = Field(default_factory=list, alias="axisNames")
    values: List[Union[None, StrNumType]]

    # TODO: validate len(shape) == len(axis_names)
    # TODO: validate product(shape) == len(values)


class Coverage(BaseModel):
    type: str = Field("Coverage", const=True)
    id: Optional[str] = None
    domain: Union[str, Domain]
    parameters: Dict[str, Parameter]
    ranges: Dict[str, NdArray]

    # TODO: make parameters optional
    # TODO: validate parameters must be set if not part of or not defined in coverage collection
    # TODO: validate ranges shape/axis_names vs domain coordinates
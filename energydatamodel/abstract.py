import dataclasses
from dataclasses import dataclass, field, fields
from abc import ABC, abstractmethod

import pandas as pd
import matplotlib.pyplot as plt
import shapely
from shapely.geometry import mapping, Point, Polygon, LineString


@dataclass
class AbstractClass(ABC):

    def to_dataframe(self):
        """Convert data class to a pandas DataFrame."""

        data = {field.name: getattr(self, field.name) for field in fields(self)}
        df = pd.DataFrame({self.__class__.__name__: data})

        return df
    
    def _serialize(self, include_none: bool) -> dict:
        serialized_data = {}
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)

            if value is None and not include_none:
                continue 

            if isinstance(value, pd.DataFrame):
                serialized_data['pd.DataFrame'] = 'pd.DataFrame'
            elif dataclasses.is_dataclass(value):
                key = value.__class__.__name__
                serialized_data[key] = value._serialize(include_none)
            elif isinstance(value, list):
                serialized_data[field.name] = [self._serialize_list_item(item, include_none) for item in value]
            else:
                serialized_data[field.name] = value
        return serialized_data

    @staticmethod
    def _serialize_list_item(item, include_none):
        if dataclasses.is_dataclass(item):
            return {item.__class__.__name__: item._serialize(include_none)}
        return item

    def to_json(self, include_none: bool=True) -> str:
        class_name = self.__class__.__name__
        serialized_data = {class_name: self._serialize(include_none)}
        return serialized_data

    def geometry_to_geojson(self, geometry):
        if isinstance(geometry, shapely.geometry.Point):
            return {"type": "Point", "coordinates": list(geometry.coords)[0]}
        elif isinstance(geometry, shapely.geometry.Polygon):
            return {"type": "Polygon", "coordinates": [list(geometry.exterior.coords)]}
        elif isinstance(geometry, shapely.geometry.LineString):
            return {"type": "LineString", "coordinates": list(geometry.coords)}
        else:
            return None

    def to_geojson(self, exclude_none=True):
        if hasattr(self, 'assets'):  # Check for the presence of an 'assets' attribute
            # Handle container classes: create a FeatureCollection
            features = [asset.to_geojson(exclude_none=exclude_none) for asset in self.assets]
            geojson_obj = {"type": "FeatureCollection", "features": features}
            return geojson_obj

#            return json.dumps(geojson_obj, indent=4)
        else:
            # Handle single asset classes
            geojson_geometry, geojson_properties = self._extract_geojson_data(self, exclude_none)
            if not geojson_geometry:
                raise ValueError("No valid geometry found for GeoJSON conversion")

            geojson_obj = {
                "type": "Feature",
                "geometry": geojson_geometry,
                "properties": geojson_properties
            }
            return geojson_obj

          #  return json.dumps(geojson_obj, indent=4)
        
    def _extract_geojson_data(self, obj, exclude_none=True):
        geojson_geometry = None
        geojson_properties = {}

        for attr_name, attr_value in obj.__dict__.items():
            if isinstance(attr_value, (Point, Polygon, LineString)):
                geojson_geometry = mapping(attr_value)
            elif isinstance(attr_value, pd.DataFrame):
                # Skip pandas DataFrame attributes
                continue
            elif hasattr(attr_value, '__dict__'):  # Check for nested objects
                nested_geometry, nested_properties = self._extract_geojson_data(attr_value)
                if nested_geometry:
                    geojson_geometry = nested_geometry
                geojson_properties.update(nested_properties)
            else:
                if not (exclude_none and attr_value is None):
                    geojson_properties[attr_name] = attr_value
        return geojson_geometry, geojson_properties

    def __repr__(self):
        attrs = []
        for field, value in self.__dict__.items():
            if (value is not None) and (type(value) not in set([pd.DataFrame, Point, LineString, Polygon])):
                attrs.append(f"{field}={value!r}")
        return f"{self.__class__.__name__}({', '.join(attrs)})"
    

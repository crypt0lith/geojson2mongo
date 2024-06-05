from abc import ABC


class GeoShape(ABC):
    @staticmethod
    def validate(coordinates) -> bool:
        pass

    @staticmethod
    def get_centroid(coordinates):
        pass


class Polygon(GeoShape):
    """An array of LinearRing coordinate arrays"""

    def __new__(cls, __coords):
        if not cls.validate(__coords):
            raise ValueError(
                'Invalid Polygon coordinates')
        instance = super().__new__(cls)
        instance.coordinates = __coords
        return instance

    @staticmethod
    def validate(coordinates):
        if not isinstance(coordinates, list) or len(coordinates) == 0:
            return False
        for ring in coordinates:
            if not isinstance(ring, list) or len(ring) < 4:
                return False
            if ring[0] != ring[-1]:
                return False
        return True

    @staticmethod
    def get_centroid(coordinates):
        x_coords, y_coords = zip(*coordinates[0])
        x_coords = list(x_coords)
        y_coords = list(y_coords)
        area = 0.0
        cx = 0.0
        cy = 0.0
        for i in range(len(x_coords) - 1):
            xi = x_coords[i]
            yi = y_coords[i]
            xi1 = x_coords[i + 1]
            yi1 = y_coords[i + 1]
            common_factor = xi * yi1 - xi1 * yi
            area += common_factor
            cx += (xi + xi1) * common_factor
            cy += (yi + yi1) * common_factor
        area *= 0.5
        cx /= (6 * area)
        cy /= (6 * area)
        return abs(area), (cx, cy)


class MultiPolygon(GeoShape):
    """An array of Polygon coordinate arrays"""

    def __new__(cls, __coords, __bbox):
        if not cls.validate(__coords):
            raise ValueError(
                'Invalid MultiPolygon coordinates')
        if not (isinstance(__bbox, list) and len(__bbox) == 2 * len(__coords[0][0][0])):
            raise ValueError(
                'Invalid bounding box')
        instance = super().__new__(cls)
        instance.coordinates = __coords
        instance.polygons = [Polygon(polygon_coords) for polygon_coords in __coords]
        instance.centroid = cls.get_centroid(instance.polygons)
        instance.bbox = __bbox
        return instance

    @staticmethod
    def validate(coordinates):
        if not isinstance(coordinates, list) or len(coordinates) == 0:
            return False
        for polygon_coords in coordinates:
            if not Polygon.validate(polygon_coords):
                return False
        return True

    @staticmethod
    def get_centroid(polygons):
        total_area = 0.0
        centroid_x = 0.0
        centroid_y = 0.0
        for polygon in polygons:
            area, (cx, cy) = Polygon.get_centroid(polygon.coordinates)
            total_area += area
            centroid_x += cx * area
            centroid_y += cy * area
        if total_area == 0:
            return (0, 0)
        centroid_x /= total_area
        centroid_y /= total_area
        return (centroid_x, centroid_y)

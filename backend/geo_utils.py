import math

def move_point(lat0, lon0, north_m, east_m):
    """Calculates a new geographic point by moving a certain distance north and east.

    Args:
        lat0 (float): Initial latitude in decimal degrees.
        lon0 (float): Initial longitude in decimal degrees.
        north_m (float): Distance to move north in metres. Can be negative.
        east_m (float): Distance to move east in metres. Can be negative.

    Returns:
        tuple[float, float]: A tuple `(new_lat, new_lon)` representing the new
        latitude and longitude in decimal degrees.
    """
    meters_per_degree_lat = 111319
    new_lat = lat0 + north_m / meters_per_degree_lat
    delta_lon = east_m / (111319 * math.cos(math.radians(lat0)))
    new_lon = lon0 + delta_lon
    return new_lat, new_lon
    
def create_polygon(lat, lon, px_per_m):
    """Creates a square geographic polygon centered on a point with a given resolution.

    Args:
        lat (float): Latitude of the center point in decimal degrees.
        lon (float): Longitude of the center point in decimal degrees.
        px_per_m (tuple[float, float]): Pixels per metre in the x and y directions
            as `(x_ppm, y_ppm)`.

    Returns:
        list[list[float]]: List of four `[lat, lon]` coordinates representing
        the corners of the polygon.
    """
    x_ppm, y_ppm = px_per_m
    d_x = 256 / x_ppm
    d_y = 256 / y_ppm
    min_lat, min_lon = move_point(lat, lon, -d_y, -d_x)
    max_lat, max_lon = move_point(lat, lon, d_y, d_x)
    polygon = [[max_lat, min_lon],
               [max_lat, max_lon],
               [min_lat, max_lon],
               [min_lat, min_lon]]
    return polygon

def find_polygons_bounds(polygons, max_bounds):
    """Calculates the bounding box for a set of polygons, constrained by maximum bounds.

    Args:
        polygons (list[list[list[float]]]): A list of polygons, where each
            polygon is a list of `[lat, lon]` coordinates.
        max_bounds (dict): Dictionary specifying maximum allowed bounds with keys:
            - "min": [min_lat, min_lon] for the southwestern corner.
            - "max": [max_lat, max_lon] for the northeastern corner.

    Returns:
        list[list[float]]: A list containing two coordinates:
            - Southwestern corner `[lat, lon]`.
            - Northeastern corner `[lat, lon]`.
    """
    min_lat = 1000000.0
    min_lon = 1000000.0
    max_lat = -1000000.0
    max_lon = -1000000.0

    for polygon in polygons:
        for coord in polygon:
            for lat, lon in polygon:
                if lat < min_lat:
                    min_lat = lat
                if lon < min_lon:
                    min_lon = lon
                if lat > max_lat:
                    max_lat = lat
                if lon > max_lon:
                    max_lon = lon

    sw = [max(max_bounds["min"][0], min_lat), 
          max(max_bounds["min"][1], min_lon)]

    ne = [min(max_bounds["max"][0], max_lat),
          min(max_bounds["max"][1], max_lon)]
    
    return [sw, ne]

def web_mercator_tile_bounds(x, y, z):
    """Calculates the Web Mercator bounds of a map tile.

    Args:
        x (int): X coordinate of the tile (column index, 0-based).
        y (int): Y coordinate of the tile (row index, 0-based).
        z (int): Zoom level of the tile (non-negative integer).

    Returns:
        tuple[float, float, float, float]: `(x_min, y_min, x_max, y_max)` representing
        the bounding box of the tile in metres in Web Mercator coordinates.
    """
    tile_size = 256
    initial_resolution = 2 * math.pi * 6378137 / tile_size
    origin_shift = 2 * math.pi * 6378137 / 2.0

    n = 2 ** z
    x_min = x / n * 2 * math.pi * 6378137 - origin_shift
    y_max = origin_shift - y / n * 2 * math.pi * 6378137
    x_max = (x + 1) / n * 2 * math.pi * 6378137 - origin_shift
    y_min = origin_shift - (y + 1) / n * 2 * math.pi * 6378137

    return (x_min, y_min, x_max, y_max)
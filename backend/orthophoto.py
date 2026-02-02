import rasterio
from pyproj import Transformer

class Orthophoto():
    """Represents an orthophoto raster image and provides geographic metadata.

    Attributes:
        raster (rasterio.io.DatasetReader): Open raster dataset.
        max_bounds (dict): Dictionary containing the geographic bounds of the image
            in latitude and longitude (EPSG:4326):
                - "min": [min_lat, min_lon] for the southwestern corner.
                - "max": [max_lat, max_lon] for the northeastern corner.
        px_per_m (tuple[float, float]): Pixels per metre in the x and y directions
            based on the raster resolution.
    """
    def __init__(self, path):
        """Initializes an Orthophoto by reading a raster file and computing metadata.

        Args:
            path (str): Path to the orthophoto raster file.
        """
        self.raster = rasterio.open(path)
        bounds = self.raster.bounds
        sw = (bounds.left, bounds.bottom)
        ne = (bounds.right, bounds.top)
        transformer = Transformer.from_crs(self.raster.crs, "EPSG:4326", always_xy=True)
        lon1, lat1 = transformer.transform(bounds.left, bounds.bottom)
        lon2, lat2 = transformer.transform(bounds.right, bounds.top)
        self.max_bounds = {"min": [lat1, lon1], "max": [lat2, lon2]}

        res_x, res_y = self.raster.res
        self.px_per_m = (1 / res_x, 1 / res_y)

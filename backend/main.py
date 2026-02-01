import io
import math
import numpy as np
import os
import rasterio
import threading

from backend.clip_service import ClipService
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from backend.geo_utils import create_polygon, find_polygons_bounds, move_point, web_mercator_tile_bounds
from backend.orthophoto import Orthophoto
from PIL import Image
from rasterio.windows import Window
from rasterio.enums import Resampling
from rasterio.windows import from_bounds

# Load default environment variables
load_dotenv()
orthophoto_path = os.getenv("ORTHOPHOTO_PATH", "backend/data/source_full.tif")
clip_model = os.getenv("CLIP_MODEL", "backend/data/source_full.tif")

# Initialise FastAPI
app = FastAPI()
app.state.clip_service = ClipService(clip_model)
app.state.orthophoto = Orthophoto(orthophoto_path)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

@app.on_event("startup")
def startup():
    """Initializes the CLIP service in a background thread when the FastAPI app starts."""
    threading.Thread(
        target=app.state.clip_service.load,
        daemon=True
    ).start()

@app.get("/search")
def search(q: str = Query(...)):
    """
    Searches for image tiles that match a given query using the CLIP service.

    Args:
        q (str): The search query string.

    Raises:
        HTTPException: 
            - 503 Service Unavailable if the CLIP model is still loading.

    Returns:
        dict: A dictionary containing:
            - "tiles" (List[dict]): A list of tile dictionaries, each including:
                - Original tile metadata (e.g., "lat", "lon").
                - "polygon" (object): The polygon representing the tile's footprint.
            - "bounds" (object): The bounding box encompassing all returned polygons,
              constrained by `app.state.orthophoto.max_bounds`.
    """
    if not app.state.clip_service.ready:
        raise HTTPException(503, "Model warming up")
    coords = app.state.clip_service.query_index(q)
    tiles = []
    polygons = []
    for coord in coords:
        polygon = create_polygon(coord["lat"], coord["lon"], app.state.orthophoto.px_per_m)
        polygons.append(polygon)
        coord["polygon"] = polygon
        tiles.append(coord)
    bounds = find_polygons_bounds(polygons, app.state.orthophoto.max_bounds)
    return {"tiles": tiles, "bounds": bounds}

@app.get("/bounds")
def get_bounds():
    """
    Returns the maximum geographic bounds of the orthophoto dataset.

    Returns:
        dict: The maximum bounds of the orthophoto dataset as latitude 
        and longitude limits {"min": [lat, lon], "max": [lat, lon]}.
    """
    return app.state.orthophoto.max_bounds

@app.get("/tiles")
def get_tile(z: int = Query(...), x: int = Query(...), y: int = Query(...)):
    """
    Retrieves a 256x256 PNG tile from an orthophoto based on Web Mercator tile coordinates.

    Args:
        z (int): Zoom level of the tile.
        x (int): X-coordinate of the tile.
        y (int): Y-coordinate of the tile.

    Returns:
        StreamingResponse: A PNG image of the requested tile, ready to be streamed 
        to the client.
    """
    bounds = web_mercator_tile_bounds(x, y, z)
    with rasterio.open(orthophoto_path) as src:
        window = from_bounds(*bounds, transform=src.transform)

        data = src.read(
            window=window,
            out_shape=(src.count, 256, 256),
            boundless=True,
            fill_value=0
        )
        arr = np.transpose(data[:3], (1,2,0))
        img = Image.fromarray(arr)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return StreamingResponse(buf, media_type="image/png")

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    return FileResponse("frontend/dist/index.html")




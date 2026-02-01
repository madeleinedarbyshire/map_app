import clip
import faiss
import torch

import threading
import torch
import clip

class ClipService():
    """Service for querying image embeddings using CLIP and Faiss.

    Attributes:
        model_name (str): Name of the CLIP model to load (default "ViT-B/32").
        num_results (int): Maximum number of results to return per query (default 100).
        similarity_threshold (float): Minimum cosine similarity to consider a match (default 0.27).
        device (str): Device to run the model on ("cuda" if available, else "cpu").
        model (clip.model.CLIP): Loaded CLIP model instance.
        index (faiss.IndexFlatIP): Faiss index of image embeddings.
        image_names (list[str]): List of image file names corresponding to embeddings.
        ready (threading.Event): Event flag indicating when the index is ready.
    """
    def __init__(self, model_name="ViT-B/32", num_results=100, similarity_threshold=0.27):
        """Initializes the ClipService with model and search parameters.

        Args:
            model_name (str, optional): CLIP model to load. Defaults to "ViT-B/32".
            num_results (int, optional): Number of search results to return. Defaults to 100.
            similarity_threshold (float, optional): Minimum similarity score for results. Defaults to 0.27.
        """
        self.model = None
        self.index = None
        self.num_results = 100
        self.similarity_threshold = 0.27
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.ready = threading.Event()

    def _load_model(self):
        """Loads the CLIP model onto the specified device and sets it to evaluation mode."""
        print('Loading CLIP model...')
        self.model, _ = clip.load(
            self.model_name,
            device=self.device
        )
        self.model.eval()

    def _create_index(self):
        """Creates a Faiss index from precomputed image embeddings."""
        print('Creating index...')
        data = torch.load("backend/models/image_embeddings.pt")
        image_features = data["features"].numpy().astype("float32")
        self.image_names = data["names"]

        # Build a Faiss index
        dimension = image_features.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        faiss.normalize_L2(image_features)

        self.index.add(image_features)
        self.ready.set()
        print("Application ready! \U0001F389")

    def load(self):
        """Loads the CLIP model and builds the Faiss index."""
        self._load_model()
        self._create_index()

    def query_index(self, query):
        """Queries the Faiss index with a text prompt and returns matching images.

        Args:
            query (str): Text string to search for in the image embeddings.

        Returns:
            list[dict]: List of matching image metadata, each containing:
                - 'name' (str): Identifier for the image tile.
                - 'lat' (float): Latitude extracted from the image file name.
                - 'lon' (float): Longitude extracted from the image file name.
                - 'score' (float): Cosine similarity score between text and image embeddings.
        """
        text_tokens = clip.tokenize([query]).to(self.device)

        with torch.no_grad():
            text_features = self.model.encode_text(text_tokens)

        text_features_np = text_features.cpu().numpy().astype("float32")
        faiss.normalize_L2(text_features_np)

        distances, indices = self.index.search(text_features_np, self.num_results)

        coords = []

        for i, idx in enumerate(indices[0]):
            _, tile_index, _, lat, _, lng = self.image_names[idx].split('.png')[0].split('_')
            if distances[0][i] > self.similarity_threshold:
                coords.append({'name': f'tile {tile_index}', 'lat': float(lat), 'lon': float(lng), 'score': float(distances[0][i])})
        return coords
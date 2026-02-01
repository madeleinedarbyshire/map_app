import argparse
import clip
import os
import torch
from PIL import Image
from pathlib import Path
from tqdm import tqdm

def main(model_name, tile_path, batch_size=32):
    """
    Extracts image embeddings using a CLIP model and saves them to backend/models/image_embeddings.pt.

    Args:
        model_name (str): The name of the CLIP model to load (e.g., "ViT-B/32").
        tile_path (str or Path): Path to the folder containing PNG images to embed.
        batch_size (int, optional): Number of images to process in a single batch. Defaults to 32.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    print("Loading CLIP model...")
    model, preprocess = clip.load(model_name, device=device)
    model.eval()

    image_folder = Path(tile_path)
    image_paths = list(image_folder.glob("*.png"))

    features_list = []
    names_list = []

    print("\nCreating image embeddings...")
    with torch.no_grad():
        for i in tqdm(range(0, len(image_paths), batch_size)):
            batch_paths = image_paths[i:i+batch_size]
            images = [preprocess(Image.open(p).convert("RGB")) for p in batch_paths]
            images = torch.stack(images).to(device)

            features = model.encode_image(images)
            features /= features.norm(dim=-1, keepdim=True)

            features_list.append(features.cpu())
            names_list.extend([p.name for p in batch_paths])

    all_features = torch.cat(features_list, dim=0)
    os.makedirs("backend/models", exist_ok=True)
    torch.save({
        "features": all_features,
        "names": names_list
    }, "backend/models/image_embeddings.pt")

    print("\nSaved embeddings for", len(names_list), "images.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create embedding using a given CLIP model")
    parser.add_argument("--model-name", type=str, default="ViT-B/32", help="Name of CLIP model to use")
    parser.add_argument("--tile-path", type=str, default="backend/data/tiles", help="Name of CLIP model to use")

    args = parser.parse_args()

    main(args.model_name, args.tile_path)


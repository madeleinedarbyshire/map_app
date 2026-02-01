# CLIP Map App

This app allows users to search for features in aerial imagery using natural language. It uses a CLIP model to pre-compute embeddings for a set of image tiles, which are then indexed with Faiss. Faiss enables efficient nearest-neighbor searches, allowing the app to quickly compare a user’s text query embedding with the pre-computed image embeddings and identify the most relevant images.

When a user searches, the relevant tiles are retrieved by searching the index. The boundaries on the map are then set to diplay just the area containing these results. The user can then click on the tiles in the map or in the side bar to zoom to that specific tile.

<p float="left">
  <img src="./docs/images/canal_boats.png" width="600" />
  <img src="./docs/images/canal_boat.png" width="600" />
</p>

## Overview of Design
1. Python Server. Best for use with PyTorch, the OpenAI CLIP library and geospatial libraries like RasterIO.
2. React Typescript frontend. React is a popular frontend framework, used with styled components for quick modular styling. For this project, I was keen to experiment with TypeScript for the first time.

## Improvements
1. **Speed up tile loading.** The tile loading is currently quite slow because the orthophoto is being opened for each new request.
2. **Group together overlapping tiles.** Where tiles overlap, it's probably more intuitive to treat these tiles as one area that resolves to one result in side bar and one polygon on the map.
    <p float="left">
        <img src="./docs/images/swimming_pool.png" width="600" />
    </p>
3. **Improve accuracy of the model.** At the moment, the model often surfaces false positives for some searches and misses some features in other searches. Other models may produce better performance and prompt engineering may help to refine results. Creating a test set of phrase/image pairs may help to identify the best model, prompt and similarity threshold.
    <p float="left">
        <img src="./docs/images/not_swimming_pool.png" width="600" />
        <img src="./docs/images/car_park.png" width="600" />
    </p>

## Run in Docker
The whole app can be run with a few docker commands. The docker container is built on [Nvidia Pytorch Docker Containers](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/pytorch). Using these mitigates most of the dependency conflicts that can occur with different versions of CUDA and PyTorch. The one downside is they are quite large so it can take several minutes to pull the base container on first build. Also note that to use the GPUs inside a docker container, you need to ensure you have [Nvidia Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) installed on your machine.

To build docker container:
```
docker build -t map .
```

To run the container, make sure the paths to the repository and the data are correct. The data directory should contain a directory called `tiles` and an orthophoto called `source_full.tif`.
```
export SRC_PATH=/home/user/workspace/map_app
export DATA_PATH=/home/user/workspace/labs-take-home-data
```

Finally, run the docker container. It will take a couple of minutes to install everything, load the model and create the embeddings. Once it says application ready, the app should be available at `http://localhost:8080` .

```
docker run -it --rm --gpus all --shm-size=4g -p 8080:8080 \
    --ulimit memlock=-1 \
    --ulimit stack=67108864 \
    -v $SRC_PATH:/workspace/map_app \
    -v $DATA_PATH:/workspace/map_app/backend/data \
    map:latest \
    bash -c "source /usr/local/nvm/nvm.sh \
            && nvm use default \
            && npm install --prefix frontend \
            && npm run build --prefix frontend \
            && python backend/create_embeddings.py \
            && uvicorn backend.main:app --host 0.0.0.0 --port 8080 --log-level warning"

```

FROM nvcr.io/nvidia/pytorch:23.08-py3

RUN pip install \
    git+https://github.com/openai/CLIP.git \
    faiss-cpu==1.8 \
    rasterio==1.3 \
    fastapi \
    uvicorn \
    pyproj \
    python-dotenv

WORKDIR /workspace/map_app/frontend

COPY frontend/ ./

ENV NODE_VERSION=24
RUN . /usr/local/nvm/nvm.sh \
    && nvm install $NODE_VERSION \
    && nvm use $NODE_VERSION \
    && nvm alias default $NODE_VERSION \
    && npm install \
    && npm run build

WORKDIR /workspace/map_app
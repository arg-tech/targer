FROM python:3.11-slim@sha256:0b23cfb7425d065008b778022a17b1551c82f8b4866ee5a7a200084b7e2eafbf
COPY --from=ghcr.io/astral-sh/uv:0.10.1 /uv /uvx /bin/

ENV UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/usr/local/ \
    PATH="/usr/local/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends wget git && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --frozen --no-install-project --no-dev

RUN python -m nltk.downloader -d /usr/local/nltk_data punkt_tab

RUN git clone https://github.com/UKPLab/emnlp2017-bilstm-cnn-crf.git

COPY . .

RUN mv backend.py Model.py ModelNewES.py ModelNewWD.py Segmenter.py emnlp2017-bilstm-cnn-crf/

RUN wget -q -O models/IBM.h5 "https://huggingface.co/debela-arg/segmenter/resolve/main/IBM.h5?download=true" || \
    (echo "Download failed! Check URL or authentication." && exit 1)

RUN mv models/* emnlp2017-bilstm-cnn-crf/models/
RUN mv -f BiLSTM.py emnlp2017-bilstm-cnn-crf/neuralnets/

# Patch cloned repo keras imports for TF 2.x compatibility
RUN sed -i \
    -e 's/^import keras/from tensorflow import keras/' \
    -e 's/^from keras import/from tensorflow.keras import/' \
    -e 's/^from keras.engine import Layer, InputSpec/from tensorflow.keras.layers import Layer, InputSpec/' \
    -e 's/self.add_weight((/self.add_weight(shape=(/' \
    emnlp2017-bilstm-cnn-crf/neuralnets/keraslayers/ChainCRF.py

RUN mkdir emnlp2017-bilstm-cnn-crf/lstm && \
    git clone https://github.com/achernodub/bilstm-cnn-crf-tagger.git emnlp2017-bilstm-cnn-crf/lstm

EXPOSE 6000

WORKDIR /app/emnlp2017-bilstm-cnn-crf

CMD ["gunicorn", "--workers", "1", "--bind", "0.0.0.0:6000", "--timeout", "300", "--access-logfile", "-", "--error-logfile", "-", "backend:app"]

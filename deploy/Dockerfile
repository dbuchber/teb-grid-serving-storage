# gridsim-API: Rechenläufe für das Regionen-Dashboard. Eingaben (prepared/) und Cache werden gemountet.
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
    GRIDSIM_PREPARED=/prepared GRIDSIM_CACHE=/cache GRIDSIM_MAX_JOBS=2 GRIDSIM_WORKERS=4 GRIDSIM_REPLAY_DELAY_S=0.4
WORKDIR /app
COPY pyproject.toml README.md ./
COPY gridsim ./gridsim
COPY api ./api
ARG GRIDSIM_VERSION=unknown
ENV GRIDSIM_VERSION=${GRIDSIM_VERSION}
RUN pip install --no-cache-dir . && useradd -u 10001 -M -s /usr/sbin/nologin gridsim
USER 10001
EXPOSE 8000
CMD ["uvicorn", "api.app:app_from_env", "--factory", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]

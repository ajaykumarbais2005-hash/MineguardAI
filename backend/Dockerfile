FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN groupadd --system --gid 10001 mineguard \
    && useradd --system --uid 10001 --gid mineguard --home-dir /app mineguard \
    && mkdir -p /app/data/uploads \
    && chown -R mineguard:mineguard /app

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY --chown=mineguard:mineguard app ./app

USER 10001:10001

EXPOSE 8000

CMD ["sh", "-c", "python -m app.init_db && exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips='*'"]

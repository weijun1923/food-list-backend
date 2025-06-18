# ---------- Stage 1: deps ----------
FROM python:3.12-slim AS base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

FROM base AS deps
WORKDIR /app

# 1) 下載 uv 二進位
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv  

# 2) 複製鎖檔與專案元資料
COPY pyproject.toml uv.lock README.md ./

# 3) 複製源碼目錄
COPY src/ ./src

# 4) 安裝依賴到系統解釋器
ENV UV_SYSTEM_PYTHON=1
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# ---------- Stage 2: runtime ----------
FROM base
WORKDIR /app

# 複製已解析好的 site-packages 與腳本
COPY --from=deps /usr/local/lib/python3.12/site-packages \
               /usr/local/lib/python3.12/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# 最後再複製程式碼
COPY src/ ./src

ENV PORT 5000
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-k", "gthread", "-b", "0.0.0.0:5000", "src.app:create_app()"]

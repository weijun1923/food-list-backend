# syntax=docker/dockerfile:1
###############################################################################
# Stage 0 ── 基礎映像：共用設定                                             #
###############################################################################
FROM python:3.12-slim AS base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

###############################################################################
# Stage 1 ── deps：使用 uv 建立虛擬環境 .venv，安裝所有依賴                  #
###############################################################################
FROM base AS deps

# ① 複製 uv 二進位（官方 distroless 映像只含 /uv）                          #
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv               

# ② 複製鎖檔後先安裝 transitive 依賴                                        #
COPY pyproject.toml uv.lock ./
# 在專案路徑內建立 .venv（uv 預設），不碰系統 Python                         #
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project                                   

# ③ 再複製源碼並安裝本專案（含 gunicorn 等可執行檔）                       #
COPY src/ ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen                                                      

###############################################################################
# Stage 2 ── runtime：只帶 .venv 與程式碼，映像更小                          #
###############################################################################
FROM python:3.12-slim AS runtime
WORKDIR /app

# ① 複製整個 .venv 及 uv（方便日後 sync）                                   #
COPY --from=deps /app/.venv /app/.venv
COPY --from=deps /usr/local/bin/uv /usr/local/bin/uv

# ② 複製應用程式碼                                                         #
COPY src/ ./src

# ③ 把 .venv/bin 加進 PATH 以使用 gunicorn 等指令                            #
ENV PATH="/app/.venv/bin:$PATH"                                            
ENV PORT=5000
EXPOSE 5000

# ④ 使用 --factory 啟動工廠函式                                            #
CMD ["gunicorn","-w", "4", "-k", "gthread","-b", "0.0.0.0:5000", "src.app:create_app()"]

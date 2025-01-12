# ベースイメージを指定
FROM python:3.10-slim

# 作業ディレクトリを作成
WORKDIR /app

# Poetry のインストール
RUN pip install poetry

# 必要なファイルをコピー
COPY pyproject.toml poetry.lock ./

# Poetry を使用して依存関係をインストール
RUN poetry config virtualenvs.create false && poetry install --no-dev

# アプリケーションファイルをコピー
COPY . .

# エントリーポイントを指定
CMD ["python", "bot.py"]

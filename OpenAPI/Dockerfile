# ベースイメージを指定
FROM node:latest

# 作業ディレクトリを設定
WORKDIR /app

# モックサーバーのインストール
RUN npm install -g @stoplight/prism-cli@5

# ポートの公開（prism のデフォルトポート）
EXPOSE 4010

# コンテナ起動時に実行されるコマンドを設定
CMD ["prism", "mock", "-d", "-h", "0.0.0.0", "/app/OpenAPI/jsc.openapi.json"]
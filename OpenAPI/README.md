# backend に実装される API の仕様書です

# Language/framework

- json
- nodejs
- npm

# 記法

json による OpenAPI 3.0

# Requirement

- @redocly/cli

### パッケージ URL

https://www.npmjs.com/package/@redocly/cli

### グローバルインストール

```bash
npm i @redocly/cli -g
```

# Usage

openapi 仕様で書いた json ファイルを html に出力

```bash
npx @redocly/cli build-docs jsc.openapi.json -o jsc.openapi.html
```

# モックサーバ

prism でのモックサーバが http://localhost:4010 で立ち上がります。

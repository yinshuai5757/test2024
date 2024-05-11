# JSColipot_dev
JS Copilotの開発用リポジトリです。
＊アプリ名変更の可能性があります。

# DEMO

https://www.notion.so/JS-Copilot-874fd654f341429fb34b2b0f8d72d234

# Features

JS Copilotは、弁護士業務の書面作成を支援するツールです。

アプリを用いることによって、工数削減や休出減少、顧客誘引などの課題解決ができると考えています。

# Language/framework
* python3.11
* flask3.0.2
* Node.js 18
* Next.js(App Router) 14.1

# Styles/framework
* TailwindCSS
* shadcn/ui

# Requirement
docker上のlinuxで動かすことを想定している。
多分macでも動くはず...

* docker
* docker compose


# Usage


```bash
git clone URL
cd JSCopilot_dev
```

dockerを起動する際
```bash
docker compose up --build
```

dockerを終了する
```bash
docker compose down
```

dockerの中に入る
```bash
docker exec -it container_name bash
```

その他便利なコマンドはいかにまとめています。
よかったらいいねよろしくお願いします！
https://qiita.com/ponponnsan/items/0a353b1cdd5be6ba2f87


# Note

frontendのアプリはnext JS以外でも構いません。
その際は、# Language/framework を書き換えていただけると助かります。

ホスト側でbackendのURLを見れるようにする

## フロント側の確認方法
下記のコマンドを実行
```
cd frontend/dev/
```
```
yarn install  // 初回のみ
yarn run dev
```


# License


JS Copilot is Confidential.

# text-generation-WebUI
- 参考URL[1](https://note.com/bakushu/n/na4e51d377ae7),[2](https://zenn.dev/saldra/articles/090c120b49e38c)
## ENVIRONMENT（ここでは WSL 上の作業について説明する）
- ホストマシン
  - Windows11
  - NVIDIA cuDNN v8.8
  - NVIDIA CUDA ツールキット 11.8
  - NVIDIA ドライバ:536.67
- WSL
  - Ubuntu-22.04
  - NVIDIA cuDNN v8.9.7
  - NVIDIA CUDA ツールキット 12.3
  - NVIDIA ドライバ:536.67
- Docker Container
  - nvidia/cuda:12.2.2-cudnn8-runtime-ubuntu22.04
### 外部に公開する port
- 7004:WebUI の API
- 7005:llama.cpp の API
- 7860:WebApp(WebUI の default)
- 7861:API(不使用)
## SETUP
### 仮想環境構築
- python -m venv linux
- source ./linux/bin/activate
- python -m pip install --upgrade pip
- pip install -r requirements.txt
### モデルのダウンロード（DL先は「D:/tool/text-generation-webui-main/models/model」とする）
#### CPU+llama.cpp(port 7005)を使う場合（①が開発用モック、②が本番用）
- venv の中に入って以下を実行（とりあえず①だけ DL すれば動作確認可能）
  - ①WSL で MiniCPM model を DL する場合（Let's note で動作可能、DL:1GB、DRAM:1GB）（デフォルトではこれを利用している）
    ```
    curl -L https://huggingface.co/runfuture/MiniCPM-2B-dpo-q4km-gguf/resolve/main/MiniCPM-2B-dpo-q4km-gguf.gguf?download=true -o /mnt/d/tool/text-generation-webui-main/models/MiniCPM-2B-dpo-q4km-gguf.gguf
    ```
  - ②WSL で VB-7B iq4 model を DL する場合（RTX4090で動作可能、DL:4GB、VRAM:4GB
    ```
    gdown https://drive.google.com/file/d/1SGLmz-qRtndTJB5uGyRsKdY8bN6rownc/view -O /mnt/d/tool/text-generation-webui-main/models/VB-7B-v0.2-IQ4_XS.gguf --fuzzy
    ```
#### [obsolete]GPU+WebUI(port 7004)を使う場合
- venv の中に入って以下を実行
  - ③WSL で 2.0b model を DL する場合（RTX4090で動作可能、DL:18GB、VRAM:23GB）
    ```
    gdown https://drive.google.com/drive/folders/1XRBkcEV2wB7D8uLxVrM_88VTXb-qAeh0 -O /mnt/d/tool/text-generation-webui-main/models/ --folder
    ```
  - ④WSL で 4.0b model を DL する場合（RTX4090で動作不可、DL:33GB、VRAM:35GB）
    ```
    gdown https://drive.google.com/drive/folders/1xzzZGi2Lk4iXzK141S91WtSiKe2HH4nP -O /mnt/d/tool/text-generation-webui-main/models/ --folder
    ```
#### huggingface model の場合
- Win のターミナルから huggingface-cli で download(推奨。WSL だと 5MB を超えるファイルが 0KB になる)
  - genv/scripts/activate
  - huggingface-cli login
    - token の入力を求められたら、[ここ](https://huggingface.co/settings/tokens)から token をコピペする
  - フォルダ全体を download する場合(DLフォルダはSSDの方がいい？)
    - huggingface-cli download {model} --local-dir /mnt/d/tool/text-generation-webui-main/models/{model}
  - ファイル単位で download する場合
    - huggingface-cli download {model} --local-dir /mnt/d/tool/text-generation-webui-main/models/{model}
- Browser の WebUI から次を実行すると、"./text-generation-webui-main/models" に download される。(非推奨)
>[Model][Download model or LoRA]:TheBloke/Xwin-LM-13B-V0.2-GPTQ  
>[Download]  
### docker での利用
#### llama.cpp を使う
- WSL で次を使えるようにしておく
  - docker(composerも)
- yaml を利用する場合
  - 次を実行し、サーバを起動
  ```
  docker compose up -d
  ```
  - AI Model を読み込み終わると、自動的に "http://localhost:7005/v1/chat/completions" を利用可能になっている
- yaml を利用しない場合は、ターミナルで以下を実行し、サーバを起動
```
docker run -p 7005:8080 -v /mnt/d/tool/text-generation-webui-main/models:/models --gpus all ghcr.io/ggerganov/llama.cpp:server-cuda -m models/tokyotech-llm-Swallow-MX-8x7b-NVE-v0.1-q4_K_M.gguf -c 512 --host 0.0.0.0 --port 8080
```
#### WebUI を使う
- WSL で次を使えるようにしておく
  - CUDA12.3
  - cuDNN8.9.7
  - docker(composerも)
- compose.yaml を次のように書き換える
```
services:
  AISERVER:
    image: ai_i
    build:
      context: .
      dockerfile: Dockerfile.webui
    environment:
      MODEL_PATH: /app/text-generation-webui-main/models/Xwin-LM-70B-V0.1-fp16-safetensors-EXL2-2.0b
      N_GPU_LAYERS: 0
      N_CONTEXT: 8192
      N_CTX_SIZE: 8192
    container_name: ai_c
    stdin_open: true
    tty: true
    volumes:
      - /mnt/d/tool/text-generation-webui-main/models/:/app/text-generation-webui-main/models/
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ['0']
              capabilities: [gpu]
    ports:
      - "7004:7004"
      - "7005:7005"
      - "7860:7860"
      - "7861:7861"
```
- ターミナルで以下を実行し、docker container を build してサーバを起動（VB model は RTX4090 以上でないと動作しないので注意）
```
docker compose up
```
  - VRAM に AI Model を読み込むまで、WSL から Win の HDD を読む場合、10分程待つ（"nvidia-smi" コマンドで読込状況を監視できる）
  - VRAM に AI Model を読み込み終わると、自動的に "http://localhost:7004/v1/chat/completions" を利用可能になっている
  - ホストマシンからも、適切にポートフォワードすれば、"http://localhost:7004/v1/chat/completions" を利用可能になっている
- (必要なら)実行中のコンテナに入る
  - docker compose -f compose.yaml exec AISERVER /bin/bash
- container から exit する // コンテナは stop しない（∵compose.yaml で "tty" と "stdin_open: true" を指定）
- stop していないことを確認
  - docker ps
>CONTAINER ID   IMAGE     COMMAND                  CREATED          STATUS          PORTS                                                                                                       NAMES
>9b437f3dde06   ai_i      "/opt/nvidia/nvidia_…"   35 seconds ago   Up 34 seconds   0.0.0.0:7004->7004/tcp, :::7004->7004/tcp, 0.0.0.0:7860-7861->7860-7861/tcp, :::7860-7861->7860-7861/tcp   ai_c
- 使い終わったら ai_c コンテナを削除
  - docker stop ai_c
  - docker rm ai_c
## USAGE
### API サーバの準備
- コンテナを起動
  - docker compose -f compose.yaml up -d AISERVER
    - VRAM に AI Model を読み込むまで、HDD なら10分、SSD なら10秒程待つ（Win のタスクマネージャから読込状況を監視できる）
    - VRAM に AI Model を読み込み終わると、自動的に "http://localhost:7005/v1/chat/completions" を利用可能になっている
    - ホストマシンからも、適切にポートフォワードすれば、"http://localhost:7005/v1/chat/completions" を利用可能になっている
- VSCode から "sample_generate.py" 構成を F5
  - ホストマシンが Windows なら、VSCode から WSL に接続し、venv に入った後に実行する
- (必要なら)実行中のコンテナの中に入る
  - docker compose -f compose.yaml exec AISERVER /bin/bash
- 使い終わったら ai_c コンテナを削除
  - docker stop ai_c
  - docker rm ai_c
### API サーバの実行確認
- WSL 上で以下を実行（port は、WebUI を使う場合は "7004"、llama.cpp を使う場合は "7005"）
  - Linux の場合（content の中身が日本語だとうまくいかないことがあるので注意）
```
curl http://localhost:7005/v1/chat/completions \
-H "Content-Type: application/json" \
-H "Authorization: Bearer no-key" \
-d '{
"model": "gpt-3.5-turbo",
"messages": [
{
    "role": "system",
    "content": "You are an excellent AI assistant. Your primary mission is to provide answers that are helpful to the requests of user."
},
{
    "role": "user",
    "content": "What is the elevation of Mount Fuji?"
}
]
}'
```
  - Windows の場合（PowerShell）（content の中身が日本語だとうまくいかないことがあるので注意）
  ```
  $uri = "http://localhost:7005/v1/chat/completions"
  $headers = @{
      "Authorization" = "Bearer no-key"
      "Content-Type" = "application/json"
  }
  $body = @{
      model = "gpt-3.5-turbo"
      messages = @(
          @{
              role = "system"
              content = "You are an excellent AI assistant. Your primary mission is to provide answers that are helpful to the requests of user."
          },
          @{
              role = "user"
              content = "What is the elevation of Mount Fuji?"
          }
      )
  } | ConvertTo-Json
  $response = Invoke-WebRequest -Uri $uri -Method "POST" -Headers $headers -Body $body -UseBasicParsing
  $response.Content
  ```
## 困ったときは
- 次のエラー → compose.yaml に deploy がない
```
ai_c  | WARNING: The NVIDIA Driver was not detected.  GPU functionality will not be available.
ai_c  |    Use the NVIDIA Container Toolkit to start this container with GPU support; see
ai_c  |    https://docs.nvidia.com/datacenter/cloud-native/ .
ai_c  |
ai_c  | ./server: error while loading shared libraries: libcuda.so.1: cannot open shared object file: No such file or directory
```
- docker compose up で次が進まない → VPN 接続を切って PC を再起動して試す
```
[AISERVER 3/8] RUN apt-get update && apt-get install -y     wget     build-essential     git     curl     bz  12.3s
```
- docker compose up で以下のエラー → VPN 接続を切って試す
```
sudouser@VLON1563:/mnt/c/dev/WebUI$ docker compose up
[+] Running 1/1
 ! AISERVER Warning Get "https://registry-1.docker.io/v2/": dial tcp: lookup registry-1.docke...                  20.3s
[+] Building 10.1s (2/2) FINISHED                                                                        docker:default
 => [AISERVER internal] load build definition from Dockerfile.llama.nogpu                                          0.1s
 => => transferring dockerfile: 1.11kB                                                                             0.1s
 => ERROR [AISERVER internal] load metadata for docker.io/library/ubuntu:22.04                                    10.0s
------
 > [AISERVER internal] load metadata for docker.io/library/ubuntu:22.04:
------
failed to solve: ubuntu:22.04: failed to resolve source metadata for docker.io/library/ubuntu:22.04: failed to do request: Head "https://registry-1.docker.io/v2/library/ubuntu/manifests/22.04": dial tcp: lookup registry-1.docker.io on 172.26.112.1:53: read udp 172.26.122.185:54268->172.26.112.1:53: i/o timeout
```
- 以下のエラー→ yaml の volume が誤っている
```
ai_c  | llama_load_model_from_file: failed to load model
ai_c  | llama_init_from_gpt_params: error: failed to load model '/app/text-generation-webui-main/models/MiniCPM-2B-dpo-q4km-gguf.gguf'
ai_c  | {"tid":"140112882198336","timestamp":1714435171,"level":"ERR","function":"load_model","line":685,"msg":"unable to load model","model":"/app/text-generation-webui-main/models/MiniCPM-2B-dpo-q4km-gguf.gguf"}
```
- llama.cpp の container に curl しても応答しない→次の point を check
  - 同一モデルの非量子化版で試してみる
  - ひとまず curl の内容に日本語が含まれないようにして動作確認する（特に content の値）
    - 日本語を使ったために一度 AI が長考モードに入ったときは、docker compose down させてやり直した方が早い
  - Dockerfile で llama.cpp を clone している行を次のように修正して再ビルド
  ```
  RUN git clone --branch b2630 https://github.com/ggerganov/llama.cpp
  ```
  - Windows で試している場合は WSL で行う
  - "to the user's requests." のような表現は "'" を使わない表現にする（∵"'"の parse に失敗するため）
  - MiniCPM-2B-dpo-q4km-gguf.gguf 以外の model で試してみる
  - 以上がすべてダメなら、次の手順で Docker Desktop の WSL2 integrate を OFF にし、WSL に docker を install して再実行してみる
    - Docker Desktop 起動→"Extensions" の右の縦の「…」→[Settings][Resources][WSL integration]→チェックボックスとトグルボタンをすべて OFF→[Apply & restart]
    - [このページ](https://qiita.com/studio_haneya/items/0bc57d0c21732fc277fd)を参考に WSL に docker を install
- "ValueError: Unknown quantization type, got exl2 - supported types are: ['awq',...]" → "--loader ExLlamav2_HF"
- "error exited with code 137" はメモリ不足なので Dockerfile の "-c" を "1024" にした
- 次のエラーが出たら通信エラーなので、通信できる環境かどうかを再確認して再実行する（マシンが自動スリープすると起きることがある）
```
42.97 error: RPC failed; curl 56 GnuTLS recv error (-9): Error decoding the received TLS packet.  
42.97 error: 5379 bytes of body are still expected  
42.98 fetch-pack: unexpected disconnect while reading sideband packet  
42.98 fatal: early EOF  
42.98 fatal: fetch-pack: invalid index-pack output  
------  
failed to solve: process "/bin/sh -c git clone https://github.com/ggerganov/llama.cpp" did not complete successfully: exit code: 128  
```
- "huggingface-cli download" で 5MB 以上のファイルのサイズが "0KB" になる（管理者権限で実行してもダメ）
  - Win で次のように更新したらうまくいった(WSL だと更新しても改善しないことがある)
    ```
    pip install --upgrade huggingface-hub
    ```
  - WSL の ~/.cache/以下から Win の .cache にコピーしてから、win で DL を再開する
    ```
    cp -r ~/.cache/huggingface/hub/models--meta-llama--Meta-Llama-3-70B-Instruct/blobs/* /mnt/c/Users/takum/.cache/huggingface/hub/models--meta-llama--Meta-Llama-3-70B-Instruct/
    ```
- text-generation-webui のバージョンを変更したら動かなくなった
  - "installer_files" を削除し、環境を再構築する
- text-generation-webui の install 中に次のメッセージ→clone ではなく Tags から zip を使う
>Downloading and Extracting Packages  
>  
>Preparing transaction: done  
>Verifying transaction: done  
>Executing transaction: done  
>You are not currently on a branch.  
>Please specify which branch you want to merge with.  
>See git-pull(1) for details.  
>  
>    git pull <remote> <branch>  
>  
>Command '"C:\dev\text-generation-webui\installer_files\conda\condabin\conda.bat" activate "C:\dev\text-generation-webui\installer_files\env" >nul && git pull --autostash' failed with exit status code '1'.  
>  
>Exiting now.  
>Try running the start/update script again.  


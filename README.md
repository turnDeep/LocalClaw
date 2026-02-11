# WSL2 Native Docker・Ollama・OpenWebUI・OpenClaw・LangChain 構築マニュアル【RTX 5090対応・完全準拠版】

## 📋 目次
1. [システム概要と準拠基準](#1-システム概要と準拠基準)
2. [WSL2とDocker Engineのインストール（ネイティブ動作）](#2-wsl2とdocker-engineのインストールネイティブ動作)
3. [NVIDIA Container Toolkitの設定](#3-nvidia-container-toolkitの設定)
4. [Docker Composeによる統合環境の起動](#4-docker-composeによる統合環境の起動)
5. [OpenWebUIの設定とRAG機能（LangChain連携）](#5-openwebuiの設定とrag機能langchain連携)
6. [OpenClaw（自律エージェント）の利用](#6-openclaw自律エージェントの利用)
7. [Windows起動時の自動起動（WSL2対応）](#7-windows起動時の自動起動wsl2対応)
8. [動作確認](#8-動作確認)
9. [トラブルシューティング](#9-トラブルシューティング)

---

## 1. システム概要と準拠基準

本システムは、以下の公式ドキュメントおよびベストプラクティス（2026年時点）に完全準拠して構築されています。

- **Ollama**: NVIDIA GPU (RTX 5090) をDockerコンテナから直接利用する公式構成。
- **OpenWebUI**: 公式の「Functions (Pipes)」機能を利用し、LangChain v1 を統合。
- **OpenClaw**: 公式ドキュメント (`docs.openclaw.ai`) の推奨設定（`models.providers.ollama` 形式）に準拠。
- **LangChain v1**: 最新の `langchain-community`, `langchain-ollama` パッケージを使用し、日本の公文書（通達）に最適化されたRAGシステムを実装。

構成図：
```
[Windows 11]
  └─ [WSL2 (Ubuntu)]
       ├─ Docker Engine (Systemd)
       │    ├─ [Container: Ollama] (GPU推論・Embeddings)
       │    ├─ [Container: OpenWebUI] (チャット画面 + LangChain Pipe)
       │    └─ [Container: OpenClaw] (自律エージェント + LangChain Skill)
       └─ ファイルシステム (~/ai-setup): 設定ファイル・ドキュメント
```

---

## 2. WSL2とDocker Engineのインストール（ネイティブ動作）

Docker Desktopではなく、パフォーマンスと安定性に優れる「WSL2ネイティブのDocker Engine」を使用します。

### WSL2のインストール
PowerShell（管理者）で実行：
```powershell
wsl --install
# PC再起動後、Ubuntuのユーザー名・パスワードを設定
```

### Docker Engineのインストール（WSL2 Ubuntu内）
WSL2ターミナルを開き、公式スクリプトでインストール：
```bash
# Docker公式インストールスクリプト
curl -fsSL https://get.docker.com | sh

# ユーザーをdockerグループに追加（sudoなしでdockerコマンドを使うため）
sudo usermod -aG docker $USER

# Dockerサービスの自動起動設定 (Systemd)
sudo systemctl enable docker
sudo systemctl start docker
```

---

## 3. NVIDIA Container Toolkitの設定

RTX 5090をコンテナから利用するために必須です。

```bash
# リポジトリ設定とGPGキー追加
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# インストールとDocker設定
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

**確認:** `docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi` を実行し、RTX 5090が表示されればOK。

---

## 4. Docker Composeによる統合環境の起動

### ファイル配置
WSL2のホームディレクトリ直下に `ai-setup` フォルダを作成し、納品されたファイル群（`docker-compose.yml`, `openclaw/`, `rag_system/`, `openwebui/`）を配置します。

```bash
# フォルダ構造
~/ai-setup/
  ├── docker-compose.yml
  ├── openclaw/
  │   ├── Dockerfile
  │   ├── openclaw.json
  │   └── skills/
  ├── openwebui/
  │   ├── Dockerfile
  │   └── langchain_pipe.py
  └── rag_system/
      ├── ingest.py
      ├── query.py
      └── requirements.txt
```

### 起動
```bash
cd ~/ai-setup
docker compose up -d --build
```
※ 初回はOpenClawとOpenWebUIのカスタムイメージビルドが走るため、数分かかります。

---

## 5. OpenWebUIの設定とRAG機能（LangChain連携）

ブラウザで `http://localhost:3000` にアクセスします。

### LangChain RAGの利用 (Official Docs RAG Pipe)
本システムには、日本の公文書（通達など）を高精度に検索するためのLangChain v1連携機能が組み込まれています。

1. **ドキュメントの登録**:
   - `rag_system/docs` フォルダにPDFファイルを配置します。
   - `docker compose restart openwebui` 等で再起動時、または手動でスクリプトを実行してインデックス化します。

2. **利用方法**:
   - チャット画面で「Models」から通常のモデルではなく、追加された「Functions」または「Tools」として登録された `Official Docs RAG Pipe` を有効にします（またはパイプライン設定で追加）。
   - 質問すると、裏でLangChainが動き、公文書特有の「記」「第１」などの構造を理解した上で回答を生成します。

---

## 6. OpenClaw（自律エージェント）の利用

OpenClawはバックグラウンドで動作し、Ollamaと連携しています。

### 設定確認
`openclaw/openclaw.json` は公式ドキュメント準拠の設定になっています：
```json
{
  "agent": {
    "model": "ollama/gemma3:27b"
  },
  "models": {
    "providers": {
      "ollama": {
        "baseUrl": "http://localhost:11434/v1",
        "apiKey": "ollama-local",
        "api": "openai-completions"
      }
    }
  }
}
```

### スキルの利用
DiscordやSlack連携を行うと、チャットから `@OpenClaw` にメンションすることで、以下のスキルを利用できます：
- **official_docs_rag**: 「通達検索: 〇〇について教えて」のように指示すると、LangChainのRAGシステムを使って回答します。

---

## 7. Windows起動時の自動起動（WSL2対応）

WSL2内のDockerをWindows起動時に自動で立ち上げるため、専用のバッチファイル `start-ai-wsl.bat` を使用します。

1. `start-ai-wsl.bat` をデスクトップなどに配置します。
2. ファイル内のパス（`cd ~/ai-setup`）が正しいか確認します。
3. タスクスケジューラで「ログオン時」にこのバッチファイルを実行するよう設定します（「最上位の特権で実行」にチェック）。

これにより、Windowsにログインすると自動的にWSL2が起動し、Dockerコンテナ群（Ollama, WebUI, OpenClaw）が立ち上がります。

---

## 8. 動作確認

1. **コンテナ状態**: `docker ps` で3つのコンテナ（ollama, open-webui, openclaw）が `Up` であること。
2. **GPU利用**: `docker exec ollama nvidia-smi` でGPUメモリが確保されていること。
3. **WebUI**: `http://localhost:3000` でチャットができること。
4. **LangChain連携**: OpenClawまたはWebUIからドキュメント検索ができること。

---

## 9. トラブルシューティング

- **Ollamaのレスポンスが文字化けする**:
  - OpenClawの設定でストリーミングが無効化されているか確認してください（本構成ではデフォルトで無効化済み）。
- **"Connection refused"**:
  - `network_mode: "host"` のため、コンテナ間通信は `localhost` を使用します。`http://ollama:11434` ではなく `http://localhost:11434` が正解です。
- **ファイルが見つからない**:
  - WSL2側のパス (`/home/user/...`) と Windows側のパス (`C:\Users\...`) を混同していないか確認してください。本システムは **WSL2側にファイルを置くこと** を強く推奨します。

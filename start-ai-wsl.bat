@echo off
echo Starting WSL2 AI Services...

REM 1. WSL2を起動し、Dockerサービスが動いているか確認して起動 (要sudoパスワードなし設定、またはroot実行)
REM 通常のUbuntu環境を想定しています。ディストリビューション名が異なる場合は "Ubuntu" を変更してください。
wsl -d Ubuntu -u root -e sh -c "service docker status > /dev/null 2>&1 || service docker start"

REM 2. 少し待つ（Dockerデーモン起動待ち）
timeout /t 5 /nobreak > nul

REM 3. WSL2内のdocker-composeを使って起動
REM "ai-setup" フォルダがホームディレクトリ直下にあると仮定しています。
wsl -d Ubuntu -e sh -c "cd ~/ai-setup && docker compose up -d"

echo AI Services started via WSL2!
echo Access OpenWebUI at http://localhost:3000
pause

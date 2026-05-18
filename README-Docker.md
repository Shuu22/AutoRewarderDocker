# Docker ARM64 Guide

Este repositório suporta execução em **linux/arm64** com **Chromium + chromedriver**, WebUI e fluxo de login inicial via noVNC.

## 1) Build

```bash
docker compose build
```

## 2) Subir WebUI

```bash
docker compose up -d autorewarder-web
curl http://127.0.0.1:8080/api/status
```

A WebUI fica publicada somente em localhost da VM: `127.0.0.1:8080`.

## 3) Acesso remoto seguro (SSH tunnel)

No seu computador local:

```bash
ssh -L 8080:127.0.0.1:8080 ubuntu@IP_DA_VM
```

Depois abra: `http://127.0.0.1:8080`

## 4) Login inicial Microsoft/Bing via setup-browser + noVNC

Na VM:

```bash
docker compose --profile setup up setup-browser
```

No seu computador local, abra túnel:

```bash
ssh -L 6080:127.0.0.1:6080 ubuntu@IP_DA_VM
```

Acesse: `http://127.0.0.1:6080/vnc.html`

Faça login no Chromium. O perfil persiste em `./data/accounts/<account_id>/EdgeProfile` e será reutilizado pelo Selenium/CLI.

## 5) Execução manual (CLI)

```bash
docker compose run --rm autorewarder-web cli --account main --pc 30 --mobile 20 --force
```

## 6) Logs

- WebUI: endpoint `/api/logs?tail=100`
- Container:

```bash
docker compose logs -f autorewarder-web
```

## 7) Backup

Faça backup/restauração da pasta local `./data`.

## 8) Segurança

- **Não exponha** `8080` e `6080` publicamente.
- Mantenha binds em localhost (`127.0.0.1`) e use SSH tunnel.
- Autenticação básica opcional na WebUI via:
  - `WEBUI_USERNAME`
  - `WEBUI_PASSWORD`
# Docker Usage (ARM64)

This project is Python + Selenium. The container is configured for **linux/arm64** and uses **Chromium + chromedriver** (ARM-compatible) instead of Microsoft Edge.

## Build

```bash
docker build --platform linux/arm64 -t autorewarder:arm64 .
```

## Run

### Show CLI options

```bash
docker run --rm --platform linux/arm64 autorewarder:arm64 --help
```

### Typical headless run

```bash
docker run --rm \
  --platform linux/arm64 \
  -v autorewarder_data:/root/.local/share/AutoRewarder \
  autorewarder:arm64 \
  --account "Main" --pc 30 --mobile 20
```

### Compose

```bash
docker compose up --build
```

Adjust `command:` in `docker-compose.yml` to your desired CLI arguments.

## Environment variables

- `AUTOREWARDER_BROWSER=chromium` (required in container)
- `CHROME_BIN=/usr/bin/chromium`
- `CHROMEDRIVER_PATH=/usr/bin/chromedriver`
- `TZ=UTC` (optional)

Runtime data is stored in `/root/.local/share/AutoRewarder` (mapped to `autorewarder_data` volume in Compose).

## ARM64 notes

- Base image: `python:3.12-slim-bookworm` (multi-arch).
- Browser stack uses Debian ARM64 packages (`chromium`, `chromium-driver`) to avoid amd64-only binaries.
- On non-ARM hosts, use Buildx/QEMU emulation for `--platform linux/arm64` builds.

## Known limitation

The app automates Microsoft Rewards accounts and requires account setup/login state in the persistent profile volume before meaningful runs.

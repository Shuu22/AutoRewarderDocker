# Docker Usage (ARM64)

This project runs on **linux/arm64** with **Chromium + chromedriver** in Docker.

For the full VM flow (WebUI + noVNC setup/login), use **DOCKER_ARM_WEBUI.md**.

## Quick commands

```bash
docker compose build
docker compose up -d autorewarder-web
curl http://127.0.0.1:8080/api/status
```

Run CLI manually:

```bash
docker compose run --rm autorewarder-web cli --account main --pc 30 --mobile 20 --force
```

## Notes

- Container data path: `/home/app/.local/share/AutoRewarder`
- Keep ports bound to localhost (`127.0.0.1`) and use SSH tunneling for remote access.

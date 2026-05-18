# AutoRewarder Docker ARM64 + WebUI

## Requisitos
- Ubuntu ARM64/aarch64 VM
- Docker + Compose plugin

## Build e subida
```bash
docker compose build
docker compose up -d autorewarder-web
curl http://127.0.0.1:8080/api/status
```

## Acesso seguro (SSH tunnel)
```bash
ssh -L 8080:127.0.0.1:8080 ubuntu@IP_DA_VM
```
Abra: http://127.0.0.1:8080

## Login inicial Microsoft/Bing (noVNC)
```bash
ssh -L 6080:127.0.0.1:6080 ubuntu@IP_DA_VM
docker compose --profile setup up setup-browser
```
Abra: http://127.0.0.1:6080/vnc.html

Faça login no Chromium. O perfil fica persistido em `./data/accounts/main/EdgeProfile` e será reutilizado pelo Selenium.

## Rodar manualmente (CLI)
```bash
docker compose run --rm autorewarder-web cli --account main --pc 30 --mobile 20 --force
```

## Logs
- UI lê `./data/background_log.txt`
- Também use:
```bash
docker compose logs -f autorewarder-web
```

## Auth opcional na WebUI
Configure no compose:
- `WEBUI_USERNAME`
- `WEBUI_PASSWORD`

Se vazio, sem autenticação (use apenas com tunnel SSH).

## Backup
Backup da pasta `./data`.


## Segurança
- Não exponha as portas 8080/6080 publicamente na VM.
- Use somente bind localhost + túnel SSH.
- Defina `WEBUI_USERNAME` e `WEBUI_PASSWORD` para habilitar auth básica.

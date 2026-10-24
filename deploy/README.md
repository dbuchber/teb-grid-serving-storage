# gridsim-API auf hetzner

- Code: `/data/infra-kg-austria/work/gridsim/` (rsync aus dem Repo, ohne `.git`).
- Vorbereitete Wetterjahre: `prepared/` (`uv run python -m gridsim prepare --input /data/infra-kg-austria/work/steyr-pv-2026-10-24/input --out prepared`).
- Cache: `cache/` (vom Container beschreibbar, uid 10001). Vorberechnung Pitch-Minimum:
  `docker exec gridsim-api python -m gridsim precompute --prepared /prepared --cache /cache`.
- Start: `GRIDSIM_VERSION=$(git rev-parse --short HEAD) docker compose -f deploy/compose.yaml up -d --build`.
- Lauscht auf `127.0.0.1:17061`, Pfade unter `/api/` (Proxy reicht `/api/...` unverändert durch).
- Zugang nur über teb-hackathon.bbger.at hinter oauth2-proxy (Realm `teb-hackathon`, Gruppe `teb-access`);
  Caddy-Eintrag pflegt Session infra-kg-austria-18.

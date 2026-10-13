# Rowhammer DRAM Mitigation Agent

A Python toolkit and static browser demonstration for **illustrative** DRAM-risk indicator classification. Numerical rules flag elevated primary or secondary inputs, explicit critical conditions, and anomaly descriptors. This code does **not** generate DRAM accesses, measure bit flips, experimentally evaluate TRR, or establish security guarantees.

## Browser demonstration

The self-contained page in [web/index.html](web/index.html) runs with ordinary browser JavaScript. It uses the same nominal/elevated/critical rule structure as the main Python worker implementation. It neither contacts an API nor stores inputs on a server; it creates JSON exports locally. It is **not** a signed audit service or hardware test. GitHub Pages publishing is configured in the repository workflow; do not assume a live URL until deployment has succeeded.

## Features and limitations

- **Primary Python CLI/API**: three rule-based workers, a supervisor and an in-memory HMAC-SHA256 chain. In-memory logs are discarded on process exit; the `verify-audit` CLI only checks that process's current ledger. There is no durable, externally anchored audit store.
- **Legacy CLI**: `rowhammer-dram-mitigation-engine` uses the separate `rowhammer_mitigation` implementation and different historical secondary thresholds. Retained for backwards compatibility; outputs should not be combined without normalizing rule definitions.
- **REST service**: FastAPI `/health`, `/metrics` (JSON), `/api/audit`, `/api/chat` (deterministic mock), and `/api/audit/logs`.
- **Enrichment examples**: generic numeric threshold evaluators, not empirically validated DRAM models.
- The HMAC audit chain verifies record signatures and linkage **within the current process** when a secret is supplied. Treat it as a demonstration, not an append-only audit system.
- The PHI regex guard handles a limited set of patterns and is not a comprehensive identifier or data-loss-prevention system.

## Install and use

Requires Python 3.10 or later.

```bash
git clone https://github.com/abusuraihsakhri/rowhammer-dram-mitigation-agent.git
cd rowhammer-dram-mitigation-agent
python -m pip install -e '.[dev]'
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
python cli.py audit --task-id TASK-001 --target DRAM-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
python cli.py batch --input sample.csv --output results.csv
python cli.py chat "Show the available modes"
python cli.py serve --host 127.0.0.1 --port 8000
```

Use `http://127.0.0.1:8000/docs` for interactive API documentation. Generate and set a unique random signing key rather than using the empty placeholder in `.env.example`. The CLI reads `AUDIT_SECRET_KEY` from its environment; merely copying `.env.example` to `.env` does not load it into a shell. Docker Compose uses `env_file` instead. The API has **no authentication**, so keep it bound to trusted localhost interfaces and do not publish it directly to the Internet.

The package also installs `rowhammer-agent` (primary CLI) and `rowhammer-dram-mitigation-engine` (legacy CLI).

## Checks

```bash
python -m pytest -q
python -m compileall -q agents rowhammer_mitigation cli.py simulator.py
node --check web/app.js
node --test tests/test_frontend.cjs
python -m build --no-isolation
python simulator.py 100
```

Python code runs on the server or local workstation. The browser demonstration uses JavaScript rather than Pyodide, because the calculation is small and deterministic. It can be opened as a static page or deployed to GitHub Pages without exposing HMAC secrets.

## Deployment

`docker compose up --build` serves the Python API on `127.0.0.1:8000` with `AUDIT_SECRET_KEY` supplied via a local `.env` file. GitHub Pages publishes only `web/`, not the Python backend. To use Pages, configure GitHub Settings → Pages → Build and deployment → GitHub Actions. No browser code needs a server token or an HMAC secret.

## License

MIT — see [LICENSE](LICENSE).

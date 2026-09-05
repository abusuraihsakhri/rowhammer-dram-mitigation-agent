# Rowhammer DRAM Mitigation Agent

> **Domain:** Hardware Security & DRAM Vulnerability Assessment  
> **Standard:** JEDEC DRAM Security Guidelines

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

Rowhammer DRAM Mitigation Agent is a security analysis engine that evaluates DRAM bit-flip vulnerability patterns, simulates double-sided rowhammer activation, assesses Target Row Refresh (TRR) mitigation effectiveness, and provides multi-agent consensus-based risk classification.

The system coordinates specialized worker agents to detect anomalies, enforce safety boundaries, and maintain a cryptographically tamper-evident audit trail of all evaluations.

---

## ⚙️ Key Capabilities & Algorithmic Modules

- **Multi-Agent Coordination**: Specialized workers (InvariantQC, SafetyEscalation, ProtocolConformance) evaluate payloads independently
- **Risk & Urgency Classification**: Three-tier categorization (ROUTINE, ELEVATED_RISK, CRITICAL_STAT_PANIC) with automated remediation recommendations
- **Zero-PHI Outbound Guard**: Active regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers from audit logs
- **HMAC-SHA256 Audit Trail**: Chained, cryptographically signed logs for every evaluation and state transition
- **FastAPI REST API**: OpenAPI 3.1 endpoints for programmatic access
- **Prometheus Telemetry**: Operational metrics export
- **Enrichment Suite**: 8 domain-specific evaluation engines for comprehensive DRAM security analysis

---

## 💻 Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/rowhammer-dram-mitigation-agent.git
cd rowhammer-dram-mitigation-agent

# Install dependencies
pip install fastapi uvicorn pydantic pytest

# Configure environment
cp .env.example .env
# Edit .env and set your AUDIT_SECRET_KEY (minimum 16 characters)
```

---

## 🚀 CLI Quickstart & Usage

### 1. Single Task Evaluation
```bash
python cli.py audit --task-id TASK-001 --target TARGET-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. Interactive Chat
```bash
python cli.py chat "What is the system status?"
```

### 3. Batch CSV Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
| Parameter | Description | Default |
|:----------|:------------|:--------|
| `--task-id` | Unique task identifier | TASK-2026-001 |
| `--target` | Target identifier | KEY-TARGET-01 |
| `--primary` | Primary metric value (float) | 28.5 |
| `--secondary` | Secondary metric value (float) | 14.2 |
| `--critical` | Critical flag (boolean) | False |
| `--status` | Status descriptor | DISCORDANT |

---

## 🛡️ Security Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers from audit logs.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation. Requires `AUDIT_SECRET_KEY` environment variable (minimum 16 characters).
* **Input Validation:** Pydantic models enforce bounds checking and sanitize string inputs to prevent injection.
* **No Hardcoded Secrets:** All cryptographic keys must be provided via environment variables.

### Environment Variables
| Variable | Required | Description |
|:---------|:---------|:------------|
| `AUDIT_SECRET_KEY` | Yes | HMAC-SHA256 signing key (min 16 chars) |
| `MODEL_PROVIDER` | No | LLM provider: mock, ollama, claude, openai (default: mock) |

---

## 🧪 Testing & Verification

```bash
# Set test environment variable
export AUDIT_SECRET_KEY="test-audit-secret-key-2026-minimum-16-chars"

# Run full test suite
pytest -v

# Run with coverage
pytest -v --cov=agents --cov=rowhammer_mitigation

# Execute high-throughput simulation benchmark
python simulator.py 1000
```

---

## 🐳 Container Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or manually with Docker
docker build -t rowhammer-dram-mitigation-agent .
docker run -p 8000:8000 --env-file .env rowhammer-dram-mitigation-agent
```

---

## 📁 Project Structure

```
rowhammer-dram-mitigation-agent/
├── agents/                      # Core agent system
│   ├── __init__.py
│   ├── api.py                   # FastAPI REST endpoints
│   ├── base.py                  # Security, PHI guard, audit trail
│   ├── learning.py              # Bayesian calibration engine
│   ├── llm_factory.py           # LLM provider factory
│   ├── metrics.py               # Prometheus metrics
│   ├── models.py                # Pydantic data models
│   ├── streamer.py              # WebSocket telemetry
│   ├── supervisor.py            # Multi-agent orchestrator
│   └── workers.py               # Specialized evaluation workers
├── rowhammer_mitigation/        # DRAM-specific analysis module
│   ├── __init__.py
│   ├── agents.py                # DRAM sub-agents
│   ├── cli.py                   # DRAM CLI interface
│   ├── engine.py                # Core evaluation engine
│   ├── models.py                # DRAM data models
│   └── server.py                # DRAM FastAPI server
├── tests/                       # Test suite
│   ├── test_enrichment.py
│   ├── test_rowhammer_dram_mitigation_agent.py
│   └── test_rowhammer_mitigation.py
├── enrichment.py                # 8 domain enrichment engines
├── cli.py                       # Main CLI entry point
├── simulator.py                 # High-throughput simulation
├── sample.csv                   # Sample batch input
├── sample_payload.json          # Sample API payload
├── benchmark_dataset.json       # Golden benchmark test cases
├── Dockerfile
├── docker-compose.yml
├── .env.example                 # Environment template
└── pyproject.toml
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

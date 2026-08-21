# Passive Income Orchestrator

**Unified passive income monitoring and management system**

## Overview

The Passive Income Orchestrator is a single, unified system for managing passive income providers (Honeygain, Earnapp, Traffmonetizer, etc.) on a Raspberry Pi 5. It combines the best of both `passive-income` and `pino-node` approaches into one clean, maintainable solution.

## Features

- 🍯 **Honeygain Integration** - Monitor and manage your Honeygain earnings
- 🚦 **Traffmonetizer Support** - Track bandwidth sharing revenue
- 📊 **Analytics Dashboard** - View earnings history and projections
- 🔧 **Provider Management** - Add, remove, and configure income providers
- 📈 **Health Monitoring** - Monitor provider status and connectivity
- 🐳 **Docker-native** - All providers run in Docker containers

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Passive Income Orchestrator                    │
│                                                              │
│  ┌──────────────────┐   ┌──────────────────────────────┐    │
│  │  orchestrator.py │   │  credentials.jsonc           │    │
│  │  (main loop)     │   │  (provider credentials)      │    │
│  └────────┬─────────┘   └──────────────┬───────────────┘    │
│           │                           │                     │
│           ▼                           ▼                     │
│  ┌──────────────────┐   ┌──────────────────────────────┐    │
│  │  provider.json   │   │  Docker Containers           │    │
│  │  (config schema) │   │  - honeygain_node            │    │
│  └──────────────────┘   │  - traffmonetizer_node       │    │
│                          │  - earnapp                   │    │
│                          └──────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Quickstart

```bash
# Clone the repository
git clone https://github.com/Aldo-f/06-apps-passive-income.git
cd 06-apps-passive-income

# Edit credentials.jsonc with your provider credentials
vim credentials.jsonc

# Start the orchestrator
docker compose up -d
```

## Provider Configuration

### Honeygain
```jsonc
"honeygain": {
    "email": "your-email@example.com",
    "password": "your-password-here"
}
```

### Traffmonetizer
```jsonc
"traffmonetizer": {
    "token": "your-traffmonetizer-token-here"
}
```

### Earnapp
```jsonc
"earnapp": {
    "email": "your-earnapp-email@example.com",
    "password": "your-earnapp-password-here",
    "device_id": "your-device-id-here"
}
```

## Project Structure

```
├── orchestrator.py          # Main orchestrator script
├── credentials.jsonc        # Provider credentials (JSONC format)
├── docker-compose.yml       # Docker Compose configuration
├── providers/
│   ├── provider.json        # Provider configuration schema
│   ├── earnapp/
│   │   ├── config.env       # Earnapp environment variables
│   │   └── data/            # Earnapp data directory
│   └── honeygain/
│       └── config.env       # Honeygain environment variables
├── docs/                    # Documentation
├── nodes/                   # Node configuration
├── scripts/                 # Helper scripts
├── specs/                   # Specifications
└── tests/                   # Test scripts
```

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python orchestrator.py

# Run tests
pytest tests/
```

## Monitoring

- **Dashboard**: http://localhost:4747
- **Logs**: `docker logs -f pino_orchestrator`
- **Health Check**: `curl http://localhost:4747/health`

## License

Private - For personal use only.
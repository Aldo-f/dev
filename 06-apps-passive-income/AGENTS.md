# AGENTS.md — Passive Income Orchestrator

This file contains the operating rules for the Passive Income Orchestrator repository.

## Repository Context

This repo is a git submodule in `~/dev/06-apps-passive-income`, managed alongside other home lab services. It orchestrates passive income applications (Honeygain, Earnapp, Traffmonetizer, etc.) on a Raspberry Pi 5 running Docker.

## Agent Rules

### Deployment Rules
1. Always verify provider connections before deployment
2. Use `docker compose up -d` for production deployment
3. Monitor logs via `docker logs -f pino_orchestrator`
4. Check container health with `docker ps --filter "name=pino_"`

### Configuration Rules
5. Never modify configs directly — always use scripts/agents to manage settings
6. Store secrets in Docker secrets, not environment variables
7. Use serial wrappers for cron jobs to prevent overlap
8. Verify data persistence before service restart

### Testing and Maintenance Rules
9. Run integration tests before deploying changes
10. Verify data persistence before service restart
11. Check storage metrics weekly with `df -h`
12. Use environment-specific configurations (example provided in `.env.example`)

### Operational Rules
13. Monitor service logs regularly
14. Update documentation after each deployment
15. Test recovery procedures periodically
16. Use version control for all configuration changes

## Verification

After any change:
1. Check container status: `docker ps --filter "name=pino_"`
2. Verify logs: `docker logs -f pino_orchestrator`
3. Confirm service health: `curl -s http://localhost:4747/health`
4. Run tests: `pytest tests/` or run manual verification scripts

## License

Private - For personal use only.
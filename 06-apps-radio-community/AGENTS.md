# AGENTS.md — Radio Community

This file contains the operating rules for the Radio Community repository.

## Repository Context

This repo is a git submodule in `~/dev/06-apps-radio-community`, managed alongside other home lab services. It provides utilities for managing radio-related services, streams, and community features. The repository includes tools for monitoring, configuration, and integration with various radio platforms.

## Agent Rules

### Deployment Rules
1. Always verify provider connections before deployment
2. Use `docker compose up -d` for production deployment
3. Monitor logs via `docker logs -f radio-community`
4. Check container health with `docker ps --filter "name=radio_"`

### Configuration Rules
5. Never modify configs directly — always use scripts/agents to manage settings
6. Store secrets in Docker secrets, not environment variables
7. Use serial wrappers for cron jobs to prevent overlap

### Testing and Maintenance Rules
8. Run integration tests before deploying changes
9. Verify data persistence before service restart
10. Check storage metrics weekly with `df -h`
11. Use environment-specific configurations (.env.example for dev, .env for production)

### Operational Rules
12. Monitor service logs regularly
13. Update documentation after each deployment
14. Test recovery procedures periodically
15. Use version control for all configuration changes

## Verification

After any change:
1. Check container status: `docker ps --filter "name=radio_"`
2. Verify logs: `docker logs -f radio-community`
3. Confirm service health: `curl -s http://localhost:8080/health`
4. Run tests: `npm test` or `pytest`

## License

Private - For personal use only.
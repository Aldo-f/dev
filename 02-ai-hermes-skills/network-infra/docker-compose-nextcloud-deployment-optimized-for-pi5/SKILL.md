---
description: Pi5 Nextcloud Apache memory optimization.
name: docker-compose-nextcloud-deployment-optimized-for-pi5
---

# Docker Compose Nextcloud Memory Optimization for Pi5

## Issue
Default `nextcloud:34-apache` sets `MaxRequestWorkers=150`, causing excessive memory use. Each worker consumes 300-650MB RSS on 8GB Pi 5.

## Apache Tuning
```apache
MaxRequestWorkers 40
MaxConnectionsPerChild 5000
```

## PHP Tuning
```ini
memory_limit = 256M
opcache.memory_consumption = 64
```

## Mount Strategy
Mount configs to `mods-available`, not `mods-enabled`. Entry point handles symlink creation.

## Files
- `templates/apache/mpm_prefork.conf`
- `templates/apache/php-tuning.ini`
- `templates/docker-compose.yml`
---
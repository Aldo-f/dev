# Nextcloud Pi5 Memory Optimization Reference
#
# Apache mpm_prefork.conf — Tuned for Raspberry Pi 5 (8GB RAM):
# - MaxRequestWorkers=40 (reduced from 150)
# - MaxConnectionsPerChild=5000 (recycles workers every 5000 requests)
# - StartServers=3, MinSpare=3, MaxSpare=6
#
# PHP ini tuning:
# - memory_limit=256M
# - upload_max_filesize=512M
# - post_max_size=512M
# - opcache.memory_consumption=64
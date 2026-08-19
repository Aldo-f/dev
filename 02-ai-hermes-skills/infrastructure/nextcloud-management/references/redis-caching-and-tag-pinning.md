# Redis Caching and Image Tag Pinning for Nextcloud Docker Stack

This reference documents the exact Redis container configuration and `occ config:system:set` commands used to add caching and lock Redis to a Nextcloud Docker stack, along with pinning image tags to avoid PHP segfaults on Raspberry Pi.
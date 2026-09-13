---
title: Pivot Demo
hide:
  - toc
  - navigation
  - feedback
  - social
---

# Pivot Demo

[pivot-table]

| Tool       | Ecosystem | Store/cache | Linking | Fallback | Speed  |
|------------|-----------|-------------|---------|----------|--------|
| npm        | JS/TS     | ~/.npm      | Symbolic | npm7     | Slow   |
| pnpm       | JS/TS     | ~/.pnpm     | Hardlink | pnpm8    | Fast   |
| Bun        | JS/TS     | ~/.bun      | Copy     | bun1     | Fastest |
| pip        | Python    | ~/.cache/pip| Symbolic | pip24    | Slow   |
| uv         | Python    | ~/.cache/uv | Symbolic | uv0.4    | Fastest |

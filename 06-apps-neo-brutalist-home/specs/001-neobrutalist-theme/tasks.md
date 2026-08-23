# Tasks: Neobrutalist Theme — specs/001-neobrutalist-theme

Format: `[ID] [P?] [USn|INFRA] description` · `[Vnnn]` = verification task with evidence command.

- [x] [T001] [INFRA] Scaffold spec-kit + write spec.md, checklist, plan.md (this dir).
- [ ] [T002] [US1] Harvest real selectors: download all `/_next/static/chunks/*.js`
      from the live site; grep for service-card, item-group, info-widget,
      bookmark, status-dot class strings → `specs/001-neobrutalist-theme/selectors.md`.
- [ ] [T003] [US1] Write `config/custom.css`: design tokens as CSS custom
      properties (HyperUI values), then card/widget/bookmark/heading overrides.
      Never invent classes — use T002 output only.
- [ ] [T004] [V001] Injection proof: `curl -sk https://aldof.duckdns.org/ | grep -c 'custom.css'` ≥ 1.
- [ ] [T005] [V002] Visual proof: open live site in desktop preview pane,
      screenshot, vision-check borders/shadows/headings on ≥3 element families.
- [ ] [T006] [US2] Interaction pass: verify hover pressed-state + visible focus
      ring in screenshot; fix and re-shoot until clean.
- [ ] [T007] [US3] Durability: `docker compose up -d` recreate → reload → theme
      still applied (screenshot); commit `config/custom.css` (+ template sync)
      and push.
- [ ] [T008] [INFRA] Close kanban `t_cc19c6ee` with evidence summary.

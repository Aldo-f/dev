# AGENTS.md — 02-ai-hermes-skills

A curated library of 45+ agent skill categories. Each directory is a skill
(usually with a `SKILL.md` + supporting assets) rather than application code.

## Structure

Category dirs at top level, e.g. `software-development/`, `devops/`,
`infrastructure/`, `github/`, `creative/`, `productivity/`, `media/`,
`research/`, `network/`, `automation/`, `troubleshooting/`,
`browser-automation/`, `smart-home/`, `hardware/`, `mlops/`, `email/`, etc.

Housekeeping (non-skill): `.archive/`, `.curator_backups/`, `.hub/`.

## Conventions

- One skill = one directory; write a `SKILL.md` marking the skill's trigger
  phrases and procedure. Keep skills self-contained and composable — reference
  `troubleshooting/` or `devops/` from a task instead of copying their content.
- Follow the shared hermes skill schema used across categories (frontmatter +
  markdown body). Match the existing category's structure when adding there.
- Skills are content, not runtime; prefer clarity and reusability over cleverness.

## Notes

- This directory is the workspace's skill source — referenced from the root
  `AGENTS.md` (`Skills: Stored in 02-ai-hermes-skills/`).
- `.archive/` is frozen; do not resurrect archived skills without review.
- Do not edit the Deeezer/media navigation AGENTS unless touching media skills.
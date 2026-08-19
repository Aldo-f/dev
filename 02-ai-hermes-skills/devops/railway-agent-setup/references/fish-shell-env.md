# Fish Shell Environment Configuration

## Context

The Railway CLI installer writes configuration to `~/.config/fish/config.fish` using fish-compatible syntax. When using bash or other shells, manual PATH configuration is required.

## Fish Path Setup (automatic)

The installer created this line in your fish config:
```fish
set -gx RAILWAY_HOME '/home/aldo/.railway'
if not contains "$RAILWAY_HOME/bin" $PATH
  set -gx PATH "$RAILWAY_HOME/bin" $PATH
end
```

## Bash Path Setup (manual)

For bash/zsh, add this to `~/.bashrc`:
```bash
export RAILWAY_HOME="$HOME/.railway"
export PATH="$RAILWAY_HOME/bin:$PATH"
```

## Verification Commands

```bash
# Check RAILWAY_HOME is set
echo $RAILWAY_HOME

# Check railway is in PATH
which railway

# Check version
railway --version
```

## Session-Specific Notes

During the Railway setup session on 2026-08-05:
- Initial `railway` command failed with "command not found"
- Fix: Set PATH explicitly via `export RAILWAY_HOME=/home/aldo/.railway && export PATH="$RAILWAY_HOME/bin:$PATH"`
- Alternative: Source fish environment with `source "$HOME/.railway/env.fish"` (fish syntax only)
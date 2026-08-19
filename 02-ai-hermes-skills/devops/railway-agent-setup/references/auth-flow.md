# Railway Authentication Flow

## Context

During the setup session on 2026-08-05, the `railway login` command required browser authentication and blocked until completion.

## Standard Flow

```bash
railway login
# Outputs:
# → Sign in with one click:
#     https://railway.com/activate?user_code=MXJM-ZZWF
# → Or go to https://railway.com/activate and enter this code:
#     MXJM-ZZWF
```

## Headless/Automation Workaround

The `railway login` command blocks waiting for browser authentication. For headless environments:

1. Run `railway login` in background:
   ```bash
   railway login &
   # Get the activation URL and code from output
   ```

2. Open the URL in any browser and enter the code.

3. Bring the job back or wait for it to complete.

## Common Issues

### Login Timeout (Exit Code 124)

The command times out after 60s if you don't complete browser authentication:
```
[Command timed out after 60s]
Exit 124: the command hit its timeout.
```

### Session Already Authenticated

After successful login, `railway setup agent -y` reports:
```
Already logged in.
```

### Manual Activation

If you get the activation code but can't open the URL in your current environment:
1. Copy the URL: `https://railway.com/activate?user_code=XXXX-XXXX`
2. Open in any browser on any machine
3. Enter the 8-character code when prompted

## Verification After Login

```bash
# List projects - works only after auth
railway projects list

# Check linked project status
railway status
```

## Session-Specific Notes

During 2026-08-05 session:
- First login attempt timed out after 60s
- Second attempt also timed out (browser not available in headless)
- Third attempt: ran `railway setup agent -y` which confirmed "Already logged in."
- This suggests the authentication state was persisted after the first successful browser auth
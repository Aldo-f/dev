# Opencode Installation via NPM

## Overview
This document describes how to install and configure opencode (the open-source AI coding agent) via npm when it's not available in standard distribution repositories.

## Installation Steps

1. Install opencode-ai globally via npm:
   ```bash
   npm install -g opencode-ai
   ```

2. Verify installation:
   ```bash
   opencode --version
   # Should output: 1.18.9 (or similar)
   ```

## Configuration for Custom Providers

To configure opencode to use a custom OpenAI-compatible endpoint (like a local freellmapi service):

1. Create the config directory:
   ```bash
   mkdir -p ~/.config/opencode
   ```

2. Create or edit the config file:
   ```yaml
   # ~/.config/opencode/config.yaml
   providers:
     - name: freellm
       type: openai
       base_url: http://192.168.0.5:3001/v1
       api_key: ""
       model: auto
   ```

## Usage

Once configured, you can use opencode with your custom provider:

```bash
# Run a simple query
opencode run "Hello, can you help me with this code?" --model freellm/auto

# Or start interactive mode
opencode --model freellm/auto
```

## Notes
- The `api_key` can be left empty for local services that don't require authentication
- The `model: auto` setting allows the service to choose the best available model
- Adjust the `base_url` to match your service's actual endpoint
- Some services may require specific authentication headers or different endpoints

## Troubleshooting

If you encounter connection issues:
1. Verify the service is running and accessible
2. Check that the endpoint is correct (often `/v1` or `/v1/chat/completions`)
3. Verify authentication requirements
4. Check service logs for detailed error messages

## Related Patterns
- See `references/omo-installation.md` for installing omo via npm
- See `references/npm-global-install.md` for general npm global installation patterns
- See `references/installer-fix.md` for robust installer patterns
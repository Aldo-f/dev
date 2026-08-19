# Fix for Ansible hermes-skills role git_config parameter error

## Issue
When running the 01-core-infra install.sh script, the Ansible playbook failed in the hermes-skills role with the error:
```
ERROR! Scope is local but all of the following are missing: repo
```
This occurred in the tasks for setting git user name and email.

## Root Cause
The hermes-skills role was using the incorrect parameter name `repo_path` in the git_config module instead of the correct parameter `repo`.

In Ansible's git_config module, the parameter to specify the repository path is `repo`, not `repo_path`.

## Fix
Changed the hermes-skills/tasks/main.yml tasks:
- From: `repo_path: "{{ dev_home }}/02-ai-hermes-skills"`
- To: `repo: "{{ dev_home }}/02-ai-hermes-skills"`

This was applied to both the "Set git user name for repo" and "Set git user email for repo" tasks.

## Verification
After the fix, the install.sh script runs successfully without the git_config error, and the hermes-skills repository is properly configured with the correct git user details.
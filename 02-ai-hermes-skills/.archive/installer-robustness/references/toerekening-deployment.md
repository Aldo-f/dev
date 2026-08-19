# Deploying Applications from Infrastructure-Only Repositories

## Problem
Some repositories contain only infrastructure files (Dockerfile, docker-compose.yml, etc.) without the actual application source code. When deploying such repositories:
1. Direct cloning and building fails because there's no source to build
2. The application cannot run without its source code
3. Simply copying the infrastructure files doesn't provide the needed application code

## Solution
When dealing with infrastructure-only repositories:
1. Clone the repository to get the infrastructure files
2. Copy the necessary application source/template files from your template directory
3. Build and deploy using Docker Compose

## Implementation in Ansible
```yaml
# Clone the infrastructure repository
- name: Clone Toerekening repo
  git:
    repo: https://github.com/aldo-f/toerekening.git
    dest: /home/aldo/dev/06-apps-toerekening
    version: main
    force: yes

# Copy template application files (when repo is infrastructure-only)
- name: Copy Toerekening template files
  copy:
    src: "{{ item.src }}"
    dest: "{{ item.dest }}"
  loop:
    - { src: "{{ template_dir }}/apps/toerekening/docker-compose.yml", dest: "/home/aldo/dev/06-apps-toerekening/docker-compose.yml" }
    - { src: "{{ template_dir }}/apps/toerekening/Dockerfile", dest: "/home/aldo/dev/06-apps-toerekening/Dockerfile" }
    - { src: "{{ template_dir }}/apps/toerekening/package.json", dest: "/home/aldo/dev/06-apps-toerekening/package.json" }
    - { src: "{{ template_dir }}/apps/toerekening/package-lock.json", dest: "/home/aldo/dev/06-apps-toerekening/package-lock.json" }

# Build and start the application
- name: Build and start Toerekening via Docker Compose
  command: docker-compose up -d --build
  args:
    chdir: /home/aldo/dev/06-apps-toerekening
```

## Why This Approach
- Preserves the infrastructure definitions from the repository
- Ensures the application has the necessary source code to build and run
- Works reliably even when the source repository is infrastructure-only
- Maintains separation between infrastructure (from repo) and application (from templates)

## Verification
```bash
# Check that both infrastructure and application files exist
ls -la /home/aldo/dev/06-apps-toerekening/
# Should show both infrastructure files (from repo) and application files (from templates)

# Check that the service is running
docker ps | grep toerekening
```
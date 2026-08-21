import os
import sys
import json
import re
import time
import subprocess
import logging
from datetime import datetime

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler('/var/log/pino-orchestrator.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def parse_jsonc(filepath):
    """Parse JSON with comments (JSONC)"""
    with open(filepath, 'r') as f:
        content = f.read()
    # Remove single line comments
    content = re.sub(r'(//|#).*?$', '', content, flags=re.M)
    # Remove multi-line comments
    content = re.sub(r'/\\*.*?\\*/', '', content, flags=re.S)
    return json.loads(content)

def load_providers_config():
    """Load provider configuration from provider.json"""
    config_path = './providers/provider.json'
    if not os.path.exists(config_path):
        return {}
    
    with open(config_path, 'r') as f:
        return json.load(f)

def get_provider_credentials(provider_name, credentials):
    """Get credentials for a specific provider"""
    if provider_name == 'honeygain':
        return credentials.get('honeygain', {})
    elif provider_name == 'earnapp':
        return credentials.get('earnapp', {})
    elif provider_name == 'iproyalpawns':
        return credentials.get('iproyalpawns', {})
    elif provider_name == 'packetstream':
        return credentials.get('packetstream', {})
    elif provider_name == 'peer2profit':
        return credentials.get('peer2profit', {})
    return {}

def is_provider_enabled(provider_config, provider_name):
    """Check if a provider is enabled"""
    if provider_name in ['honeygain', 'earnapp', 'iproyalpawns', 'packetstream', 'peer2profit']:
        provider_data = provider_config.get('providers', {}).get(provider_name, {})
        return provider_data.get('enabled', False)
    return False

def manage_container(container_name, image, command=None, environment=None, volumes=None):
    """Manage a Docker container"""
    # Check if container exists and is running
    check_cmd = ["docker", "ps", "-a", "-f", f"name={container_name}", "--format", "{{.Status}}"]
    result = subprocess.run(check_cmd, capture_output=True, text=True)
    
    if "Up" in result.stdout:
        return True  # Already running
    
    # Remove existing container if it exists
    subprocess.run(["docker", "rm", "-f", container_name], capture_output=True)
    
    # Build docker run command
    cmd = ["docker", "run", "-d", "--name", container_name, "--restart", "always"]
    
    # Add volumes
    if volumes:
        for vol in volumes:
            cmd.extend(["-v", vol])
    
    # Add environment variables
    if environment:
        for key, value in environment.items():
            cmd.extend(["-e", f"{key}={value}"])
    
    # Add image
    cmd.append(image)
    
    # Add command if specified
    if command:
        if isinstance(command, list):
            cmd.extend(command)
        else:
            cmd.append(command)
    
    # Run the container
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"Failed to start {container_name}: {result.stderr}")
        return False
    
    logging.info(f"Started container: {container_name}")
    return True

def manage_honeygain(node_name, credentials, logger):
    """Manage Honeygain container"""
    honeygain_creds = get_provider_credentials('honeygain', credentials)
    email = honeygain_creds.get('email')
    password = honeygain_creds.get('password')
    
    if not email or not password or email == "CHANGE_ME@example.com":
        logger.info("Honeygain credentials not configured")
        return
    
    container_name = "honeygain_node"
    image = "honeygain/honeygain:latest"
    command = ["-tou-accept", "-email", email, "-pass", password, "-device", node_name]
    
    manage_container(container_name, image, command)

def manage_traffmonetizer(node_name, credentials, logger):
    """Manage Traffmonetizer container"""
    traffmonetizer_creds = get_provider_credentials('traffmonetizer', credentials)
    token = traffmonetizer_creds.get('token')
    
    if not token or token == "CHANGE_ME":
        logger.info("Traffmonetizer token not configured")
        return
    
    container_name = "traffmonetizer_node"
    image = "traffmonetizer/cli_v2:latest"
    command = ["start", "accept", "--token", token]
    
    manage_container(container_name, image, command)

def manage_earnapp(credentials, logger):
    """Manage Earnapp container"""
    earnapp_creds = get_provider_credentials('earnapp', credentials)
    device_id = earnapp_creds.get('device_id')
    
    if not device_id or device_id == "YOUR_DEVICE_ID":
        logger.info("Earnapp device ID not configured")
        return
    
    container_name = "earnapp"
    image = "earnapp/earnapp:latest"
    environment = {
        "EMAIL": earnapp_creds.get('email', ''),
        "PASSWORD": earnapp_creds.get('password', '')
    }
    volumes = ["./providers/earnapp/data:/app/data"]
    
    manage_container(container_name, image, environment=environment, volumes=volumes)

def main():
    logger = setup_logging()
    logger.info("Starting Pino Node Orchestrator")
    
    credentials_path = "./credentials.jsonc"
    if not os.path.exists(credentials_path):
        logger.error(f"Credentials file not found: {credentials_path}")
        sys.exit(1)
    
    # Load credentials (JSONC format)
    with open(credentials_path, 'r') as f:
        content = f.read()
    content = re.sub(r'(//|#).*?$', '', content, flags=re.M)
    content = re.sub(r'/\\*.*?\\*/', '', content, flags=re.S)
    credentials = json.loads(content)
    
    # Load provider configuration
    provider_config = load_providers_config()
    
    node_name = credentials.get('system', {}).get('nodeName', 'unknown-node')
    logger.info(f"Node name: {node_name}")
    
    while True:
        try:
            # Reload configurations each loop
            with open(credentials_path, 'r') as f:
                content = f.read()
            content = re.sub(r'(//|#).*?$', '', content, flags=re.M)
            content = re.sub(r'/\\*.*?\\*/', '', content, flags=re.S)
            credentials = json.loads(content)
            
            provider_config = load_providers_config()
            
            # Manage all enabled providers
            if is_provider_enabled(provider_config, 'honeygain'):
                manage_honeygain(node_name, credentials, logger)
            
            if is_provider_enabled(provider_config, 'traffmonetizer'):
                manage_traffmonetizer(node_name, credentials, logger)
                
            if is_provider_enabled(provider_config, 'earnapp'):
                manage_earnapp(credentials, logger)
                
            # Add other providers as needed
            # manage_iproyalpawns(credentials, logger)
            # manage_packetstream(credentials, logger)
            # manage_peer2profit(credentials, logger)
            
            time.sleep(60)  # Check every minute
            
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
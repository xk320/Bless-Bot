# Copyright (C) 2024 FakerPK
# Licensed under the AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.html
# This software is provided "as-is" without any warranties.

import asyncio
import aiohttp
import random
import platform
import psutil
import hashlib
import uuid
import os
import itertools
from aiohttp_socks import ProxyConnector
from colorama import Fore, Style, init

init(autoreset=True)

# Configuration
API_BASE_URL = "https://gateway-run.bls.dev/api/v1"
RETIRE_API_URL = "https://gateway-run-indexer.bls.dev/api/v1/nodes"
MAX_PING_ERRORS = 3
PING_INTERVAL = 60
RESTART_DELAY = 240
MAX_REGISTRATION_RETRIES = 3
RETRY_DELAYS = [5, 15, 30]
NODE_ID_CHARS = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

class Node:
    def __init__(self, original_id):
        self.original_id = original_id.strip()
        self.current_id = original_id.strip()
        self.hardware_id = self._generate_hardware_id()
        self.registered = False
        self.ping_errors = 0
        self.proxy = None

    def _generate_hardware_id(self):
        system_info = f"{platform.node()}-{platform.machine()}-{platform.processor()}-{uuid.getnode()}"
        return hashlib.sha256(system_info.encode()).hexdigest()

    def regenerate_id(self):
        if len(self.original_id) >= 4:
            base = self.original_id[:-4]
            new_id = base + ''.join(random.choices(NODE_ID_CHARS, k=4))
            self._update_data_file(self.current_id, new_id)
            self.current_id = new_id
        self.registered = False

    def _update_data_file(self, old_id, new_id):
        try:
            with open('data.py', 'r') as f:
                content = f.read()
            
            new_content = content.replace(
                f'"nodeId": "{old_id}"',
                f'"nodeId": "{new_id}"'
            )
            
            with open('data.py', 'w') as f:
                f.write(new_content)
                
            print(f"{Fore.CYAN}[ℹ] Updated data.py: {old_id} → {new_id}")
        except Exception as e:
            print(f"{Fore.RED}[❌] Failed to update data.py: {e}")

async def retire_node(session, node, auth_token):
    for attempt in range(3):
        try:
            response = await session.post(
                f"{RETIRE_API_URL}/{node.current_id}/retire",
                headers={
                    "Authorization": f"Bearer {auth_token}",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                },
                json={}
            )
            if response.status == 200:
                print(f"{Fore.GREEN}[✅] Retired {node.current_id}")
                return True
            print(f"{Fore.RED}[❌] Failed to retire {node.current_id}: HTTP {response.status}")
        except Exception as e:
            print(f"{Fore.RED}[❌] Retirement error: {str(e)}")
        
        await asyncio.sleep(2 ** attempt)
    return False

async def register_node(session, node, auth_token):
    for attempt in range(MAX_REGISTRATION_RETRIES):
        try:
            response = await session.post(
                f"{API_BASE_URL}/nodes/{node.current_id}",
                headers={
                    "Authorization": f"Bearer {auth_token}",
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                },
                json={
                    "hardwareId": node.hardware_id,
                    "hardwareInfo": {
                        "cpuArchitecture": platform.machine(),
                        "cpuModel": platform.processor(),
                        "cpuFeatures": ["avx", "sse4_2"],
                        "numOfProcessors": psutil.cpu_count(),
                        "totalMemory": psutil.virtual_memory().total
                    },
                    "extensionVersion": "0.1.7"
                }
            )
            
            if response.status == 200:
                print(f"{Fore.GREEN}[✅] Registered {node.current_id}")
                node.registered = True
                return True
                
            print(f"{Fore.RED}[❌] Registration failed: HTTP {response.status}")
            
        except Exception as e:
            print(f"{Fore.RED}[❌] Registration error: {str(e)}")
        
        await asyncio.sleep(RETRY_DELAYS[attempt])
    
    print(f"{Fore.YELLOW}[⚠] Regenerating ID for {node.current_id}")
    return False

async def manage_session(session, node, auth_token):
    try:
        response = await session.post(
            f"{API_BASE_URL}/nodes/{node.current_id}/start-session",
            headers={
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            },
            json={}
        )
        
        if response.status == 200:
            print(f"{Fore.BLUE}[📡] Session started for {node.current_id}")
            return True
            
        print(f"{Fore.RED}[❌] Session start failed: HTTP {response.status}")
        
    except Exception as e:
        print(f"{Fore.RED}[❌] Session error: {str(e)}")
    
    return False

async def monitor_node(session, node, auth_token):
    while node.registered:
        try:
            response = await session.post(
                f"{API_BASE_URL}/nodes/{node.current_id}/ping",
                headers={
                    "Authorization": f"Bearer {auth_token}",
                    "Content-Type": "application/json"
                },
                json={}
            )
            
            if response.status == 200:
                node.ping_errors = 0
                print(f"{Fore.CYAN}[📶] Ping OK: {node.current_id}")
            else:
                await handle_ping_failure(node, f"HTTP {response.status}", auth_token)
                
            await asyncio.sleep(PING_INTERVAL)
            
        except Exception as e:
            await handle_ping_failure(node, str(e), auth_token)

async def handle_ping_failure(node, error, auth_token):
    node.ping_errors += 1
    print(f"{Fore.YELLOW}[⚠] Ping error ({node.ping_errors}/{MAX_PING_ERRORS}): {error}")
    
    if node.ping_errors >= MAX_PING_ERRORS:
        print(f"{Fore.RED}[🔴] Max ping errors for {node.current_id}")
        if node.proxy:
            connector = ProxyConnector.from_url(node.proxy)
        else:
            connector = None
        
        async with aiohttp.ClientSession(connector=connector) as session:
            if await retire_node(session, node, auth_token):
                node.regenerate_id()

async def node_lifecycle(node, auth_token):
    while True:
        try:
            if node.proxy:
                connector = ProxyConnector.from_url(node.proxy)
            else:
                connector = None
            
            async with aiohttp.ClientSession(connector=connector) as session:
                # Registration Phase
                if not await register_node(session, node, auth_token):
                    continue
                
                # Session Management
                if not await manage_session(session, node, auth_token):
                    if node.registered:
                        await retire_node(session, node, auth_token)
                    node.regenerate_id()
                    continue
                
                # Monitoring Phase
                await monitor_node(session, node, auth_token)
                
        except Exception as e:
            print(f"{Fore.RED}[❌] Critical error: {str(e)}")
            if node.registered:
                if node.proxy:
                    connector = ProxyConnector.from_url(node.proxy)
                else:
                    connector = None
                async with aiohttp.ClientSession(connector=connector) as session:
                    await retire_node(session, node, auth_token)
            node.regenerate_id()
        
        await asyncio.sleep(RESTART_DELAY)

async def main():
    print(f"""{Fore.YELLOW}
    ███████╗ █████╗ ██╗  ██╗███████╗██████╗  ██████╗ ██╗  ██╗ 
    ██╔════╝██╔══██╗██║ ██╔╝██╔════╝██╔══██╗ ██╔══██╗██║ ██╔╝ 
    █████╗  ███████║█████╔╝ █████╗  ██████╔╝ ██████╔╝█████╔╝  
    ██╔══╝  ██╔══██║██╔═██╗ ██╔══╝  ██╔══██╗ ██╔═══╝ ██╔═██╗  
    ██║     ██║  ██║██║  ██╗███████╗██║  ██║ ██║     ██║  ██╗     
    ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═╝     ╚═╝  ╚═╝     
    {Style.RESET_ALL}""")

    print(f"{Fore.MAGENTA}Bless Network Bot! AUTOMATE AND DOMINATE{Style.RESET_ALL}")
    print(f"{Fore.RED}========================================{Style.RESET_ALL}")

    # Load proxies from proxy.txt
    proxies = []
    if os.path.exists('proxy.txt'):
        with open('proxy.txt', 'r') as f:
            proxies = [line.strip() for line in f if line.strip()]
        print(f"{Fore.CYAN}[ℹ] Loaded {len(proxies)} proxies from proxy.txt")

    choice = input(f"{Fore.CYAN}Select option:\n{Fore.GREEN}1. Use existing config\n{Fore.GREEN}2. Interactive setup\n{Fore.YELLOW}Enter choice (1/2): ")

    config = []
    if choice == '1':
        try:
            from data import config
        except ImportError:
            print(f"{Fore.RED}[❌] Missing data.py file")
            return
    elif choice == '2':
        while True:
            user_token = input(f"{Fore.YELLOW}Enter user token: ")
            nodes = []
            while True:
                node_id = input(f"{Fore.YELLOW}Enter node ID (blank to finish): ")
                if not node_id: 
                    break
                nodes.append({"nodeId": node_id})
            config.append({"usertoken": user_token, "nodes": nodes})
            if input(f"{Fore.YELLOW}Add another user? (y/n): ").lower() != 'y':
                break
    else:
        print(f"{Fore.RED}Invalid choice")
        return

    tasks = []
    for user in config:
        auth_token = user["usertoken"]
        proxy_cycle = itertools.cycle(proxies) if proxies else None
        
        for node_data in user["nodes"]:
            node = Node(node_data["nodeId"])
            if proxies:
                node.proxy = next(proxy_cycle)
                print(f"{Fore.CYAN}[ℹ] Assigned proxy {node.proxy} to {node.current_id}")
            tasks.append(node_lifecycle(node, auth_token))

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())

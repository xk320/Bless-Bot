import asyncio
import aiohttp
from aiohttp_socks import ProxyConnector
import json
import random
import os
from datetime import datetime
from colorama import Fore, Back, Style, init

init(autoreset=True)  # Initialize colorama

API_BASE_URL = "https://gateway-run.bls.dev/api/v1"
MAX_PING_ERRORS = 3
PING_INTERVAL = 60  # seconds
RESTART_DELAY = 240  # seconds
PROCESS_RESTART_DELAY = 150  # seconds

class Node:
    def __init__(self, node_id, hardware_id, proxy=None):
        self.node_id = node_id
        self.hardware_id = hardware_id
        self.proxy = proxy
        self.ping_error_count = 0

async def fetch_ip_address(session, proxy=None):
    try:
        async with session.get("https://api.ipify.org?format=json") as response:
            data = await response.json()
            return data["ip"]
    except Exception as e:
        print(f"{Fore.RED}[❌ ERROR] Failed to fetch IP address: {e}{Style.RESET_ALL}")
        return None

async def register_node(session, node, ip_address, auth_token):
    url = f"{API_BASE_URL}/nodes/{node.node_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}"
    }
    body = {
        "ipAddress": ip_address,
        "hardwareId": node.hardware_id,
        "hardwareInfo": {
            "cpuArchitecture": "x86_64",
            "cpuModel": "AMD Ryzen 7 3700X",
            "cpuFeatures": ["mmx", "sse", "sse2", "sse3", "ssse3", "sse4_1", "sse4_2", "avx"],
            "numOfProcessors": 8,
            "totalMemory": 32 * 1024 * 1024 * 1024
        },
        "extensionVersion": "0.1.7"
    }
    
    try:
        async with session.post(url, headers=headers, json=body) as response:
            data = await response.json()
            if response.status == 200:
                print(f"{Fore.GREEN}[ℹ️ INFO]  ✅ Registered node {node.node_id}{Style.RESET_ALL}")
                return data
            else:
                print(f"{Fore.RED}[❌ ERROR] Failed to register node {node.node_id}: {data}{Style.RESET_ALL}")
                return None
    except Exception as e:
        print(f"{Fore.RED}[❌ ERROR] Failed to register node {node.node_id}: {e}{Style.RESET_ALL}")
        return None

async def start_session(session, node, auth_token):
    url = f"{API_BASE_URL}/nodes/{node.node_id}/start-session"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}"
    }
    body = {}  # Empty JSON body
    
    try:
        async with session.post(url, headers=headers, json=body) as response:
            data = await response.json()
            if response.status == 200:
                print(f"{Fore.GREEN}[ℹ️ INFO]  ✅ Started session for node {node.node_id}{Style.RESET_ALL}")
                return data
            else:
                print(f"{Fore.RED}[❌ ERROR] Failed to start session for node {node.node_id}: {data}{Style.RESET_ALL}")
                return None
    except Exception as e:
        print(f"{Fore.RED}[❌ ERROR] Failed to start session for node {node.node_id}: {e}{Style.RESET_ALL}")
        return None

async def ping_node(session, node, auth_token):
    url = f"{API_BASE_URL}/nodes/{node.node_id}/ping"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}"
    }
    body = {}  # Empty JSON body
    
    try:
        async with session.post(url, headers=headers, json=body) as response:
            data = await response.json()
            if response.status == 200 and data.get("status", "").lower() == "ok":
                print(f"{Fore.CYAN}[ℹ️ INFO]  📡 Successful ping for node {node.node_id}{Style.RESET_ALL}")
                node.ping_error_count = 0
                return True
            else:
                raise Exception(f"Unexpected response: {data}")
    except Exception as e:
        node.ping_error_count += 1
        print(f"{Fore.YELLOW}[❌ ERROR]  ⚠️ Node {node.node_id} is offline. Error count: {node.ping_error_count}{Style.RESET_ALL}")
        if node.ping_error_count >= MAX_PING_ERRORS:
            print(f"{Fore.RED}[❌ ERROR]  ⚠️ Max ping errors reached for node {node.node_id}. Restarting process...{Style.RESET_ALL}")
            return False
    return True

async def process_node(session, node, ip_address, auth_token):
    while True:
        try:
            registration_data = await register_node(session, node, ip_address, auth_token)
            if not registration_data:
                raise Exception("Failed to register node")

            session_data = await start_session(session, node, auth_token)
            if not session_data:
                raise Exception("Failed to start session")

            while True:
                if not await ping_node(session, node, auth_token):
                    break
                await asyncio.sleep(PING_INTERVAL)
            
        except Exception as e:
            print(f"{Fore.RED}[❌ ERROR] Error processing node {node.node_id}: {e}{Style.RESET_ALL}")
        
        print(f"{Fore.YELLOW}[ℹ️ INFO]  🔄 Restarting process for node {node.node_id} in {PROCESS_RESTART_DELAY} seconds...{Style.RESET_ALL}")
        await asyncio.sleep(PROCESS_RESTART_DELAY)

async def main():
    print(f"""{Fore.YELLOW}
 ______    _             _____  _  __
|  ____|  | |           |  __ \| |/ /
| |__ __ _| | _____ _ __| |__) | ' / 
|  __/ _` | |/ / _ \ '__|  ___/|  <  
| | | (_| |   <  __/ |  | |    | . \ 
|_|  \__,_|_|\_\___|_|  |_|    |_|\_\ {Style.RESET_ALL}
    """)

    print(f"{Fore.MAGENTA}Bless Network Bot! AUTOMATE AND DOMINATE{Style.RESET_ALL}")
    print(f"{Fore.RED}========================================{Style.RESET_ALL}")

    choice = input(f"{Fore.CYAN}Please select an option:\n{Fore.GREEN}1. Start mining (using data from data.py)\n{Fore.GREEN}2. Add new information interactively\n{Fore.YELLOW}Enter your choice (1 or 2): {Style.RESET_ALL}")

    if choice == '1':
        from data import config
    elif choice == '2':
        config = []
        while True:
            user_token = input(f"{Fore.YELLOW}Enter user token: {Style.RESET_ALL}")
            nodes = []
            while True:
                node_id = input(f"{Fore.YELLOW}Enter node ID (or press Enter to finish): {Style.RESET_ALL}")
                if not node_id:
                    break
                hardware_id = input(f"{Fore.YELLOW}Enter hardware ID for {node_id}: {Style.RESET_ALL}")
                proxy = input(f"{Fore.YELLOW}Enter proxy for {node_id} (leave blank if not using a proxy): {Style.RESET_ALL}")
                nodes.append({"nodeId": node_id, "hardwareId": hardware_id, "proxy": proxy})
            config.append({"usertoken": user_token, "nodes": nodes})
            
            another = input(f"{Fore.YELLOW}Add another user? (y/n): {Style.RESET_ALL}").lower()
            if another != 'y':
                break
    else:
        print(f"{Fore.RED}Invalid choice. Exiting.{Style.RESET_ALL}")
        return

    async with aiohttp.ClientSession() as session:
        tasks = []
        for user in config:
            auth_token = user["usertoken"]
            for node_data in user["nodes"]:
                node = Node(node_data["nodeId"], node_data["hardwareId"], node_data.get("proxy"))
                ip_address = await fetch_ip_address(session, node.proxy)
                if not ip_address:
                    print(f"{Fore.RED}[❌ ERROR] Failed to fetch IP address for node {node.node_id}. Skipping.{Style.RESET_ALL}")
                    continue
                tasks.append(process_node(session, node, ip_address, auth_token))
        
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())


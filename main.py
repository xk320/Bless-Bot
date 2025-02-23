# Copyright (C) 2025 FakerPK
# Licensed under the AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.html
# This software is provided "as-is" without any warranties.

import asyncio
import aiohttp
from aiohttp_socks import ProxyConnector
import json
import random
import os
from datetime import datetime
from colorama import Fore, Back, Style, init
import platform
import psutil
import hashlib
import uuid

init(autoreset=True)

API_BASE_URL = "https://gateway-run.bls.dev/api/v1"
RETIRE_API_URL = "https://gateway-run-indexer.bls.dev/api/v1/nodes"
PROXY_FILE = "proxy.txt"
MAX_PING_ERRORS = 3
PING_INTERVAL = 60
RESTART_DELAY = 240
PROCESS_RESTART_DELAY = 150
MAX_REGISTRATION_RETRIES = 5
REGISTRATION_RETRY_DELAY = 30
NODE_ID_CHARS = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

proxies = []

def load_proxies():
    global proxies
    try:
        with open(PROXY_FILE, 'r') as f:
            proxies = [line.strip() for line in f if line.strip()]
        print(f"{Fore.CYAN}[ℹ️ INFO] Loaded {len(proxies)} proxies from {PROXY_FILE}{Style.RESET_ALL}")
    except FileNotFoundError:
        proxies = []
    except Exception as e:
        print(f"{Fore.RED}[❌ ERROR] Error loading proxies: {e}{Style.RESET_ALL}")
        proxies = []

def save_proxies():
    try:
        with open(PROXY_FILE, 'w') as f:
            f.write('\n'.join(proxies))
    except Exception as e:
        print(f"{Fore.RED}[❌ ERROR] Error saving proxies: {e}{Style.RESET_ALL}")

def remove_bad_proxy(proxy):
    if proxy in proxies:
        proxies.remove(proxy)
        save_proxies()
        print(f"{Fore.YELLOW}[⚠️ WARNING] Removed bad proxy: {proxy}{Style.RESET_ALL}")

def generate_hardware_id():
    system_info = f"{platform.node()}-{platform.machine()}-{platform.processor()}-{str(uuid.getnode())}"
    return hashlib.sha256(system_info.encode()).hexdigest()

def regenerate_node_id(original_id):
    if len(original_id) < 4:
        return original_id
    prefix = original_id[:-4]
    return prefix + ''.join(random.choices(NODE_ID_CHARS, k=4))

class Node:
    def __init__(self, node_id):
        self.original_id = node_id.strip()
        self.node_id = self.original_id
        self.hardware_id = generate_hardware_id()
        self.proxy = None
        self.ping_error_count = 0
        self.rotate_proxy()

    def rotate_proxy(self):
        if proxies:
            self.proxy = random.choice(proxies)
        else:
            self.proxy = None

async def retire_node(session, node, auth_token):
    url = f"{RETIRE_API_URL}/{node.node_id}/retire"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }
    try:
        async with session.post(url, headers=headers, json={}) as response:
            if response.status == 200:
                print(f"{Fore.GREEN}[ℹ️ INFO] ✅ Successfully retired node {node.node_id}{Style.RESET_ALL}")
                return True
            print(f"{Fore.RED}[❌ ERROR] Failed to retire node {node.node_id}: HTTP {response.status}{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}[❌ ERROR] Retirement error for {node.node_id}: {e}{Style.RESET_ALL}")
        return False

async def fetch_ip_address(session):
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
        "Authorization": f"Bearer {auth_token}",
        "X-Extension-Version": "0.1.7",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }
    body = {
        "ipAddress": ip_address,
        "hardwareId": node.hardware_id,
        "hardwareInfo": get_hardware_info(),
        "extensionVersion": "0.1.7"
    }
    
    for attempt in range(MAX_REGISTRATION_RETRIES):
        try:
            async with session.post(url, headers=headers, json=body) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"{Fore.GREEN}[ℹ️ INFO] ✅ Registered node {node.node_id}{Style.RESET_ALL}")
                    return data
                elif response.status == 403:
                    print(f"{Fore.YELLOW}[⚠️ WARNING] Authorization failed for node {node.node_id}. Retrying in {REGISTRATION_RETRY_DELAY}s ({attempt+1}/{MAX_REGISTRATION_RETRIES}){Style.RESET_ALL}")
                    await asyncio.sleep(REGISTRATION_RETRY_DELAY)
                else:
                    print(f"{Fore.RED}[❌ ERROR] Failed to register node {node.node_id}: Status {response.status}{Style.RESET_ALL}")
                    return None
        except Exception as e:
            print(f"{Fore.RED}[❌ ERROR] Failed to register node {node.node_id}: {e}{Style.RESET_ALL}")
            if attempt < MAX_REGISTRATION_RETRIES - 1:
                await asyncio.sleep(REGISTRATION_RETRY_DELAY)
            else:
                return None
    return None

async def start_session(session, node, auth_token):
    url = f"{API_BASE_URL}/nodes/{node.node_id}/start-session"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}",
        "X-Extension-Version": "0.1.7",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }
    
    try:
        async with session.post(url, headers=headers, json={}) as response:
            if response.status == 200:
                data = await response.json()
                print(f"{Fore.GREEN}[ℹ️ INFO] ✅ Started session for node {node.node_id}{Style.RESET_ALL}")
                return data
            print(f"{Fore.RED}[❌ ERROR] Failed to start session for node {node.node_id}: Status {response.status}{Style.RESET_ALL}")
            return None
    except Exception as e:
        print(f"{Fore.RED}[❌ ERROR] Failed to start session for node {node.node_id}: {e}{Style.RESET_ALL}")
        return None

async def ping_node(session, node, auth_token):
    url = f"{API_BASE_URL}/nodes/{node.node_id}/ping"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}",
        "X-Extension-Version": "0.1.7",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }
    
    try:
        async with session.post(url, headers=headers, json={}) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("status", "").lower() == "ok":
                    print(f"{Fore.CYAN}[ℹ️ INFO] 📡 Successful ping for node {node.node_id}{Style.RESET_ALL}")
                    node.ping_error_count = 0
                    return True
                raise Exception(f"Unexpected response: {data}")
            raise Exception(f"Ping failed with status {response.status}")
    except Exception as e:
        node.ping_error_count += 1
        print(f"{Fore.YELLOW}[⚠️ WARNING] Node {node.node_id} offline. Errors: {node.ping_error_count}. Error: {e}{Style.RESET_ALL}")
        if node.ping_error_count >= MAX_PING_ERRORS:
            print(f"{Fore.RED}[❌ ERROR] ⚠️ Max errors for node {node.node_id}. Restarting...{Style.RESET_ALL}")
            return False
        return True

async def process_node(node, auth_token):
    while True:
        try:
            connector = ProxyConnector.from_url(node.proxy) if node.proxy else None
            async with aiohttp.ClientSession(connector=connector) as session:
                ip_address = await fetch_ip_address(session)
                if not ip_address:
                    raise Exception("Failed to get IP address")

                reg_data = await register_node(session, node, ip_address, auth_token)
                if not reg_data:
                    node.node_id = regenerate_node_id(node.original_id)
                    print(f"{Fore.YELLOW}[⚠️ WARNING] 🔄 Regenerated node ID: {node.node_id}{Style.RESET_ALL}")
                    continue

                session_data = await start_session(session, node, auth_token)
                if not session_data:
                    await retire_node(session, node, auth_token)
                    node.node_id = regenerate_node_id(node.original_id)
                    print(f"{Fore.YELLOW}[⚠️ WARNING] 🔄 Regenerated node ID: {node.node_id}{Style.RESET_ALL}")
                    continue

                while True:
                    success = await ping_node(session, node, auth_token)
                    if not success:
                        await retire_node(session, node, auth_token)
                        node.node_id = regenerate_node_id(node.original_id)
                        print(f"{Fore.YELLOW}[⚠️ WARNING] 🔄 Regenerated node ID: {node.node_id}{Style.RESET_ALL}")
                        break
                    await asyncio.sleep(PING_INTERVAL)

        except Exception as e:
            print(f"{Fore.RED}[❌ ERROR] Node {node.node_id} error: {e}{Style.RESET_ALL}")
            if node.proxy:
                remove_bad_proxy(node.proxy)
                node.rotate_proxy()
            node.node_id = regenerate_node_id(node.original_id)
            print(f"{Fore.YELLOW}[⚠️ WARNING] 🔄 Regenerated node ID: {node.node_id}{Style.RESET_ALL}")

        await asyncio.sleep(PROCESS_RESTART_DELAY)

async def main():
    load_proxies()
    
    print(f"""{Fore.YELLOW + Style.BRIGHT}
    ███████╗ █████╗ ██╗  ██╗███████╗██████╗  ██████╗ ██╗  ██╗ 
    ██╔════╝██╔══██╗██║ ██╔╝██╔════╝██╔══██╗ ██╔══██╗██║ ██╔╝ 
    █████╗  ███████║█████╔╝ █████╗  ██████╔╝ ██████╔╝█████╔╝  
    ██╔══╝  ██╔══██║██╔═██╗ ██╔══╝  ██╔══██╗ ██╔═══╝ ██╔═██╗  
    ██║     ██║  ██║██║  ██╗███████╗██║  ██║ ██║     ██║  ██╗     
    ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═╝     ╚═╝  ╚═╝     
    {Style.RESET_ALL}""")

    print(f"{Fore.MAGENTA + Style.BRIGHT}Bless Network Bot! AUTOMATE AND DOMINATE{Style.RESET_ALL}")
    print(f"{Fore.RED}========================================{Style.RESET_ALL}")

    choice = input(f"{Fore.CYAN}Select option:\n{Fore.GREEN}1. Use existing config\n{Fore.GREEN}2. Interactive setup\n{Fore.YELLOW}Enter choice (1/2): {Style.RESET_ALL}")

    config = []
    if choice == '1':
        from data import config
    elif choice == '2':
        while True:
            user_token = input(f"{Fore.YELLOW}Enter user token: {Style.RESET_ALL}")
            nodes = []
            while True:
                node_id = input(f"{Fore.YELLOW}Enter node ID (blank to finish): {Style.RESET_ALL}")
                if not node_id: break
                nodes.append({"nodeId": node_id})
            config.append({"usertoken": user_token, "nodes": nodes})
            if input(f"{Fore.YELLOW}Add another user? (y/n): {Style.RESET_ALL}").lower() != 'y':
                break
    else:
        print(f"{Fore.RED}Invalid choice{Style.RESET_ALL}")
        return

    tasks = []
    for user in config:
        auth_token = user["usertoken"]
        for node_data in user["nodes"]:
            node = Node(node_data["nodeId"])
            tasks.append(process_node(node, auth_token))

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())

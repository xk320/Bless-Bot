import requests
import time
import threading

# Constants
BASE_API_URL = "https://gateway-run.bls.dev"
AUTH_TOKEN = "your_auth_token_here"  # Replace with your Bearer token
HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json",
}

# Node IDs
NODE_IDS = [
    "12D3..............................................YP",  # Node 1
    "12D3..............................................VU",  # Node 2
]

# Functions
def check_global_health():
    """Check the global health of the Bless API."""
    url = f"{BASE_API_URL}/health"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        health_status = response.text.strip()
        print(f"Global Health Check: {health_status}")
    except requests.exceptions.HTTPError as e:
        print(f"Global Health Check Failed: {e.response.status_code} {e.response.reason}")
        print(f"Response content: {e.response.text}")

def ping_session(node_id):
    """Ping a session for a given node to keep it alive."""
    url = f"{BASE_API_URL}/api/v1/nodes/{node_id}/ping"
    try:
        response = requests.post(url, headers=HEADERS)
        response.raise_for_status()
        print(f"Ping successful for Node {node_id}")
    except requests.exceptions.HTTPError as e:
        print(f"Ping failed for Node {node_id}: {e.response.status_code} {e.response.reason}")
        print(f"Response content: {e.response.text}")

def manage_node(node_id):
    """Perform periodic pings for a single node."""
    try:
        while True:
            print(f"Pinging Node {node_id}...")
            ping_session(node_id)
            time.sleep(60)  # Wait 60 seconds between pings
    except KeyboardInterrupt:
        print(f"Stopping management for Node {node_id}")
    except Exception as e:
        print(f"An error occurred for Node {node_id}: {e}")

def global_health_monitor():
    """Monitor the global health of the Bless API."""
    try:
        while True:
            check_global_health()
            time.sleep(300)  # Check global health every 5 minutes
    except KeyboardInterrupt:
        print("Stopping global health monitor.")
    except Exception as e:
        print(f"An error occurred in global health monitoring: {e}")

# Main Script
if __name__ == "__main__":
    try:
        # Create threads for global health check and each node
        threads = []

        # Global health monitor thread
        health_thread = threading.Thread(target=global_health_monitor)
        health_thread.start()
        threads.append(health_thread)

        # Node management threads
        for node_id in NODE_IDS:
            thread = threading.Thread(target=manage_node, args=(node_id,))
            thread.start()
            threads.append(thread)

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

    except KeyboardInterrupt:
        print("Exiting script...")

    except Exception as e:
        print(f"An error occurred: {e}")

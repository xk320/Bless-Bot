# Bless Network Bot v1.0 - Automate Node Management and Mining
Automate your Bless Network node management with this Python-based script. Manage multiple devices, handle WebSocket connections, and maximize your node earnings 24/7! Perfect for VPS setups.

![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## **Features**
* Automates Bless Network Node Management and Pings.
* Supports Multiple Nodes  for simultaneous operations.
* Keeps nodes alive and boosts network uptime for maximum earnings.
* Works seamlessly for better reliability.

---

## **Get Your authToken**
To connect to the Bless Network, you’ll need your **authToken**:
1. Create an account on the Bless Network Website [hhttps://bless.network/dashboard](https://bless.network/dashboard?ref=WBY5T8)
2. Log in to your chrome extension.
3. Press `F12` to open Developer Tools in your extension or right click on the opened extension.
![image](https://github.com/user-attachments/assets/227cbdef-f607-4be5-af33-752c6dcbd657)
4. Go to the **Console** tab and enter:
   ```javascript
   chrome.storage.local.get("authToken", function(data) {
    console.log("Auth Token:", data.authToken);
    });
   ```
5. Copy the ```authToken``` shown in the console and save it for later.
![image](https://github.com/user-attachments/assets/e1aa44f8-81df-4bf9-9193-fe36dab70fde)


## **Get Your peerPubKey**
6. Extract ```peerPubKey``` 
  ```javascript
  chrome.storage.local.get("nodeData", function(data) {
    console.log("Node Data:", data.nodeData);
});
```
This will print something like:
```javascript
{
  "peerEncryptedPrivKey": "m9+YyMXk7N1daxSR...",
  "peerPubKey": "12D................................2bk"
}
```
7. Save the ```authToken``` and ```peerPubKey``` these are essential for the Python script.

## **Multiple Nodes**
1. You can remove the extension after obtaining its ```peerPubKey``` and download it again to get a new one.
2. Repeat this process as many times as you like.
3. There is a cap of 5 devices so no need to go all out.

## **Requirements**
- **Python**: Install it from [python.org](https://www.python.org/downloads/) or use the command below for Ubuntu:
  ```bash
  sudo apt install python3
  ```
- **VPS Server**: Use AWS, Google Cloud, or any cheap VPS (~$2-5/month).

---

## **Setup Instructions**
### Step 1: Clone the Repository
```bash
git clone https://github.com/FakerPK/BlessNetworkBot.git
cd BlessNetworkBot
```

### Step 2: Install Requirements
```bash
pip install -r requirements.txt
```

### Step 3: Update the Script
1. Open `main.py` in a text editor.
2. Replace the placeholder `your_auth_token_here` (Line 7) with your actual **authToken**.
3. Replace the Node IDs (Line 15).


### Step 4: Run the Script
```bash
python3 main.py
```


## **Note**
The script is working at the moment but it can stop any day so take advantage of it.
---

## **Contact for Support**
If you have questions or run into issues, hit me up on Discord or Telegram:

---

## **Social Links**
- **Discord Community**: [Join Now](https://discord.gg/Z58YmYwr)
- **Telegram**: [Subscribe Here](https://t.me/FakerPK)

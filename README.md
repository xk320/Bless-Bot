# Bless Network Bot v1.1 - Automate Node Management and Mining
Automate your Bless Network node management with this Python-based script. Manage multiple devices, handle WebSocket connections, and maximize your node earnings 24/7! Perfect for VPS setups.

![AGPL License](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)

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
  "peerPubKey": "12D..................................k"
}
```

## **Get Your Hardware ID**
7. As you have extracted the previous ```authToken``` and ```peerPubKey``` from the Console Tab, move to the Network Tab on the top and wait for a ping request to be sent.
8. Once the request is seen on the Network Tab, click on it and move to the `Response` section and copy the *Hardware ID*.
9. The *Hardware ID* stays the same for all Nodes on one account.
![image](https://github.com/user-attachments/assets/7a01b848-3a36-4db2-b315-38e048ea773a)
 
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
## **If You Want To Buy Proxies From My Recommended Provider Follow These Steps**
1. Go to [https://app.proxies.fo](https://app.proxies.fo/ref/f1353b58-10c4-98a5-d94d-6164e2efcfaf) and Sign Up.
2. *Please use my refferal link before signing up, it helps me and the cause*: [My refferal link](https://app.proxies.fo/ref/f1353b58-10c4-98a5-d94d-6164e2efcfaf)
3. Go to the ISP section, DONOT BUY THE RESIDENTIAL PLAN OR ELSE THIS WON'T WORK:
![image](https://github.com/user-attachments/assets/1337a21b-7a3c-4e18-9335-45a541c29d99)

4. Buy one of these plans, remember DONOT BUY THE RESIDENTIAL PLAN ONLY BUY THE ISP PLAN:
 ![image](https://github.com/user-attachments/assets/a4d94623-025a-459f-85d8-771975e7a503)
5. Please use my refferal link before signing up, it helps me and the cause: [My refferal link](https://app.proxies.fo/ref/f1353b58-10c4-98a5-d94d-6164e2efcfaf)


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

### Step 3: Update the data.py file
Add proxies and all the extracted info into the `data.py` file.

### Step 4: Run the Script
```bash
python3 main.py
```


## **Note**
The script is working at the moment but it can stop any day so take advantage of it.
**You can check out my Medium article for a more detailed and comprehensive guide.**

[https://medium.com/@FakerPK/bless-network-bot-v1-0-automate-node-management-and-mining-6f017d47bb44](https://medium.com/@FakerPK/bless-network-bot-v1-0-automate-node-management-and-mining-6f017d47bb44)
---

## **Contact for Support**
If you have questions or run into issues, hit me up on Discord or Telegram:

---
##  **💸Donations**
If you would like to support me or the development of this projects, you can make a donation using the following addresses:
- **Solana :** ```9SqcZjiUAz9SYBBLwuA9uJG4UzwqC5HNWV2cvXPk3Kro```
- **EVM :** ```0x2d550c8A47c60A43F8F4908C5d462184A40922Ef```
- **BTC :** `bc1qhx7waktcttam9q9nt0ftdguguwg5lzq5hnasmm`
---

## **Social Links**
- **Discord Community**: [Join Now](https://discord.gg/Z58YmYwr)
- **Telegram**: [Subscribe Here](https://t.me/FakerPK)

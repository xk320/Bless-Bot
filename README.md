
使用此基于Python的脚本自动化您的祝福网络节点管理。管理多个设备，处理Websocket连接，非常适合VPS设置。

![AGPL License](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)

---

## **功能**
* 自动化Bless Network节点管理和ping
* 支持同时操作的多个节点.
* 保持节点的活力并增加网络正常运行时间以获得最大收益.

---
### 清使用我的推荐链接给予支持:
- [Bless推荐链接](https://bless.network/dashboard?ref=2CGEP7)
## **获取token**
1. 在Bless Network网站上创建一个帐户 [hhttps://bless.network/dashboard](https://bless.network/dashboard?ref=WBY5T8)
2. 登录到您的帐户.
3. 在`Windows`上按`CTRL + SHIFT + C`或`F12`打开开发人员工具 .
4. 转到“应用程序”选项卡并输入:
5. 复制屏幕截图中显示的B7S_AUTH_TOKEN ，并保存以备后用.
![image](https://github.com/user-attachments/assets/5808a866-b647-4afc-8d61-1a000ce301c1)


## **获取 PEER PUBKEY**
6.`Inspect Element` 到您的扩展程序中，然后转到 `Console` 选项卡.

7. 提取 ```peerPubKey``` ，也就是后续脚本中要配置的`nodeId`
  ```javascript
  chrome.storage.local.get("nodeData", function(data) {
    console.log("Node Data:", data.nodeData);
});
```
这将打印出类似的内容:
```javascript
{
  "peerEncryptedPrivKey": "m9+YyMXk7N1daxSR...",
  "peerPubKey": "12D..................................k"
}
```

## **运行多个节点**
1. 更改`peer PubKey`的最后一个数字，然后将其复制到其他`nodeId`的位置.
2. 一个账户最多5个设备
```javascript
config = [
    {
        "usertoken": "AUTH_TOKEN_1",
        "nodes": [
            {
                "nodeId": "12D..................................k",
                "proxy": ""  #format: socks5://username:pass@ip:port
            },
            {
                "nodeId": "12D..................................2",
                "proxy": ""  #format: socks5://username:pass@ip:port
            },
            {
                "nodeId": "12D..................................3",
                "proxy": ""  #format: socks5://username:pass@ip:port
            },
            {
                "nodeId": "12D..................................4",
                "proxy": ""  #format: socks5://username:pass@ip:port
            },
            {
                "nodeId": "12D..................................5",
                "hardwareId": "HARDWARE_ID", #stays same for all nodes
                "proxy": ""  #format: socks5://username:pass@ip:port
            },
        ]
    },
    {
        "usertoken": "AUTH_TOKEN_2",
        "nodes": [
            {
                "nodeId": "12D..................................6",
                "proxy": ""  #format: socks5://username:pass@ip:port
            },
            {
                "nodeId": "12D..................................7",
                "proxy": ""  #format: socks5://username:pass@ip:port
            },
            {
                "nodeId": "12D..................................8",
                "proxy": ""  #format: socks5://username:pass@ip:port
            },
            {
                "nodeId": "12D..................................9",
                "proxy": ""  #format: socks5://username:pass@ip:port
            },
            {
                "nodeId": "12D..................................j",
                "proxy": ""  #format: socks5://username:pass@ip:port
            }
        ]
    } #add a comma and copy paste if you want to add more auth tokens
]
```
> **SECRET INFO**:
> The 5 `PubKeys` you extract from one account, can be used with other accounts.
> 
> Remove your extension then create a new account with your refferal code and extract the `B7S_AUTH_TOKEN`.
> 
> Add the `B7S_AUTH_TOKEN` to the `usertoken` field in the ``data.py`` and copy paste the ``PubKeys`` from before and run the script.

## **依赖**
- **Python**: Install it from [python.org](https://www.python.org/downloads/) or use the command below for Ubuntu:
  ```bash
  sudo apt install python3
  ```

## **安装文档**
### 第一步: 下载代码
```bash
git clone https://github.com/FakerPK/BlessNetworkBot.git
cd BlessNetworkBot
```

### 第二步: 安装依赖
```bash
pip install -r requirements.txt
```

### S第三步: 更新配置文件
Add proxies and all the extracted info into the `data.py` file.

### 第四步: 运行脚本
```bash
python3 main.py
```

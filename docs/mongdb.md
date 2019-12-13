### 安裝配置
- [官方安裝文檔](https://docs.mongodb.com/v4.0/tutorial/install-mongodb-on-ubuntu/)
    - 导入MongoDB公共GPG密钥
        ```sh
        wget -qO - https://www.mongodb.org/static/pgp/server-4.0.asc | sudo apt-key add -
        ```
    - 为MongoDB创建一个列表文件
        ```sh 
        echo "deb [ arch=amd64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.0.list
        ```
    - 更新apt-get
        ```sh 
        sudo apt-get update
        ```
    - 安装MongoDB软件包
        ```sh 
        sudo apt-get install -y mongodb-org=4.0.13 mongodb-org-server=4.0.13 mongodb-org-shell=4.0.13 mongodb-org-mongos=4.0.13 mongodb-org-tools=4.0.13
        ```
- apt-get install mongodb-clients

### 设为开机启动项目
```sh
sudo systemctl enable mongod.service
```

### 設置用戶、遠程訪問

- 設置用戶認證
    ```
    # 啓動shell
    mongo
    # 設置認證用戶
    use admin
    db.createUser(
      {
        user: "root",
        pwd: "Meanergy168",
        roles: [ { role: "userAdminAnyDatabase", db: "admin" }, "readWriteAnyDatabase" ],
        mechanisms : ["SCRAM-SHA-1"] 
      }
    )
    # vim /etc/mongod.conf
        security:
            authorization: enabled
    # 重啓服務
    ```
- 設置遠程訪問
    ```
    vim /etc/mongod.conf
    bindIp: 0.0.0.0
    ```

### 報錯集錦
1、service mongod start啓動報錯
```sh 
Failed to start mongod.service: Unit mongod.service not found.

# 解決方法
service mongod enable
```

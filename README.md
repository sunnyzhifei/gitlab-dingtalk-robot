# gitlab2dingtalkrobot
由于钉钉自带的gitlab机器人有些事件不支持通知，故自定义机器人
钉钉webhook自定义机器人，实现gitlab 事件通知到钉钉，目前暂时只支持push event 和pipline event

## how to use
（需要Python3，目前我使用的是Python3.6）
1. 要求安装依赖 
    >`pip3 install -r requirements.txt`

2. 启动服务
    >`python3 ./gitlab2dingding.py` 

3. 钉钉配置自定义机器人<br/>
    ![安全设置.png](https://img04.sogoucdn.com/app/a/100520146/6efd129b88f88a51af0d91666cfcd555)

4. gitlab配置webhook<br/>
    -  URL配置： `http://$ip:5000/hook/$access_token`
    ![gitlab.png](https://img04.sogoucdn.com/app/a/100520146/d6d1f080811ed5e4fb74af438bc04207)
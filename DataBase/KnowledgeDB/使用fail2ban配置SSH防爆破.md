# 使用fail2ban配置SSH防爆破

在`/var/log/auth.log`查阅到非常多的SSH爆破日志

也可以结合分析系统日志`/var/log/syslog`

## 安装

apt install fail2ban

## 配置文件

fail2ban 的默认配置文件是 /etc/fail2ban/jail.conf, 但不建议直接修改这个文件, 推荐创建一个本地配置文件 /etc/fail2ban/jail.local 来覆盖默认设置

```shell
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local

vim /etc/fail2ban/jail.local

# 在文件中配置具体的安全策略, 例如 SSH 服务找到 `[sshd]` 部分并进行如下配置: 

    [sshd]
    enabled = true
    port = ssh
    filter = sshd
    logpath = /var/log/auth.log
    maxretry = 3
    bantime = 360000
    findtime = 600

```

* enabled: 启用此监控
* port: 监控的端口, ssh 是默认端口, 也可以指定具体的端口号
* filter: 指定使用的过滤器规则
* logpath: 指定要监控的日志文件
* maxretry: 指定在 findtime 时间内允许的最大失败尝试次数
* bantime: 禁止 IP 的时间（秒）
* findtime: 在此时间窗口内如果失败次数超过 maxretry 则会被禁止

## 配置 systemd, 检查服务状态

启动并启用 fail2ban 服务并设置为开机自启:

```shell
sudo systemctl start fail2ban
sudo systemctl enable fail2ban
```

检查 Fail2ban 状态

`fail2ban-client status`

查看特定 jail 的状态, 例如 SSH:

`fail2ban-client status sshd`

检查 fail2ban 日志文件, 可以查看 /var/log/fail2ban.log 来获取更多关于哪些 IP 被禁止的信息:

`tail -f /var/log/fail2ban.log`

## 添加例外规则

ignoreip 配置选项用于指定一组 IP 地址，这些地址将被排除在禁止策略之外

在 `[DEFAULT]` 部分中找到或添加 ignoreip 行, 格式如下:

`ignoreip = 127.0.0.1/8 ::1 192.168.1.0/24 10.0.0.0/8`

根据需求修改 ignoreip 行, 你可以添加以下类型的项目:

```plaintext
单个 IP 地址: 例如 192.168.1.100
CIDR 表示法的网段: 例如 192.168.1.0/24
IP 范围: 例如 192.168.1.0/255.255.255.0
主机名: 例如 example.com
```

多个项目之间用空格分隔, 一些常见的配置示例:

```plaintext
忽略本地回环地址和整个本地网络
ignoreip = 127.0.0.1/8 ::1 192.168.0.0/16

忽略特定的远程 IP 和一个网段
ignoreip = 123.45.67.89 10.20.30.0/24

忽略一个域名 (注意:这依赖于 DNS 解析)
ignoreip = example.com

组合多种类型
ignoreip = 127.0.0.1/8 ::1 192.168.1.0/24 10.0.0.0/8 trusted-server.com
```

重启 fail2ban 服务以使更改生效:

`systemctl restart fail2ban`

验证配置:

`fail2ban-client get <JAIL_NAME> ignoreip`

替换 <JAIL_NAME> 为检查的具体 jail 名称

## 使用failban配置nginx http登录爆破保护

ToDo

[参考1](https://cloud.tencent.com/developer/article/2137876)
[参考2](https://zhuanlan.zhihu.com/p/71818778)

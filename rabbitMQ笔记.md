###### 默认端口：5672
没有配置文件，读取从环境变量开始，环境变量定义配置文件地址，端口，日志文件地址，等信息；然后再从配置文件中获取；类似于Oracle的配置

###### 架构：
主机：broker，一个主机也可以有多个broker
生产者：产生数据端
消费者：获取数据端
队列：存放数据处


###### ------已命名队列named queue------
生产端发送：
1. 1 从Pika建立连接
1. 2 连接创建通道
1. 3 通道指定需要接收的队列
1. 4 用exchange存放数据指定内容和键值
1. 5 关闭连接

消费端接收：
1. 1 从Pika建立连接
1. 2 连接创建通道
1. 3 通道指定需要接收的队列（如果知道已经存在此队列，可以不指定，但是有风险，不知道是不是已经发送了）
1. 4 定义回调函数，即怎么消耗（处理）拿到的数据
1. 5 定义消耗 方式
1. 6 开始消耗（没有关闭连接，不是到是不是消耗后，连接会关闭）
###### ------已命名队列named queue------


###### ------工作队列work queue------
用作耗时任务处理，也就是消费者端，需要大量时间处理的任务, 承担并行工作，需要消耗方确认是否处理完成消息，如果没有返回应答，就需要从新入队列

消息持久化， channel.queue_declare(queue='hello',durable=True)，实际是存入缓存，没有实际写入，如果需要用更加稳固的方式，可以用到publisher confirms

根据消耗者的忙闲状态分配任务fair dispatch
channel.basic_qos(prefetch_count=1), 有可能会导致队列装满
------工作队列work queue------


###### ------发布订阅队列publish/subscribe queue------
发送消息到多个消耗者。
在生产者，队列，消费者关系中又加入交换器exchanges构成全消息模式。

以前工作方式（named queue, work queue）：
生产者生产消息，发送到队列
队列存储，并缓存
消费者接受队列并处理

目前工作方式(publish/subscribe)：
核心：通过交换器exchanges，生产者不知道产品递送到了那个队列中，他只送到交换器。

交换器工作模式，接受生产者的产品，并推送到队列中；交换器必须要知道，特定消息应该怎么处理，这个是由交换器类型exchange type决定。
exchange type:
direct, topic,header,fanout(直接广播)

前端有交换器的队列，生产者不需要指定队列及其名称，rabbitmq将会产生一个随机名字的队列名，用来存储消息，但是一旦消费者拿到了产品，这个队列将被销毁。
队列和交换器绑定：
channel.queue_bind(exchagne='logs'
    queue=result.method.queue)
------发布订阅队列publish/subscribe queue------


###### ------路由器 routing --------
实际原理：
通过exchange的routing_key，对要发送的消息进行分组，并根据策略进行过滤，达到指定队列转发，而不像以前订阅转发，都是广播，但是通过路由可以定向的广播到一个或者多个队列
------路由器 routing --------


###### ------topics exchange主题交换器 --------
主要区别：
routing,主要解决针对策略，分别多路由到一个或者多个队列
topics,主要解决针对多个策略，进行后续路由到队列的过程

决定参数是routing_key必须要是有个列表，也就是多个策略路由规则，其中多个用点号隔开,最多255个字节

通配符：
*，表示一个单词
#，表示0个或者多个单词

------topics exchange主题交换器 --------

###### ------RPC，远程程序调用remote procedure call --------

没看懂

------RPC，远程程序调用remote procedure call --------

















##### 命令：
**rabbitmqctl list_queues**查看队列及其内容

*rabbitmqctl list_queues name message_ready message_unacknowledged* 查看队列中没有应答的消息

**rabbitmqctl list_exchages** 列出所有的交换器

**rabbitmqctl list_bindings** 列出所有的绑定关系

**rabbitmq-plugins enable rabbitmq_management** 启动管理web插件

[root@centos7 rabbitmq]# rabbitmqctl list_users
Listing users ...
guest   [administrator]

[root@centos7 rabbitmq]# rabbitmqctl add_user kevin kevin 
添加用户名 密码
Creating user "kevin" ...
[root@centos7 rabbitmq]# rabbitmqctl set_permissions -p / kevin ".*" ".*" ".*" 
给用户附权限
Setting permissions for user "kevin" in vhost "/" ...
[root@centos7 rabbitmq]# rabbitmqctl set_user_tags kevin administrator  



# rabbitmq集群配置：

## 第一步：
首先设置rabbitmq主机的hostname，centos7下面设置Hostname方法有变化：hostnamectl set-hostname real_hostname

hostnamectl set-hostname centos7 #centos7作为磁盘节点

hostnamectl set-hostname centos72 #centos72作为内存节点

## 第二步：
然后设置本地DNS,也就是配置hosts文件，让这两个机器可以通过足迹主机名互通
分别在两个服务器hosts里添加

192.168.56.101   centos72

192.168.56.102   centos7
## 第三步：
设置同步用的秘钥，也就是rabbitmq的erlang cookie

文件在/var/lib/rabbitmq/.erlang.cookie

文件默认权限是400不可以更改，需要先设置权限:

在主机centos7 192.192.168.56.102上打开.erlang.cookie文件

拷贝centos72 192.168.56.101上.erlang.cookie文件内容到centos7上

把文件权限改回400

## 第四步：
停止所有的rabbitmq服务器：rabbitmqctl stop

## 第五步：
以detached模式启动rabbitmq

rabbitmqctl -detached

并查看两个服务器的状态

rabbitmqctl status

rabbitmqctl cluster_status

## 第六步：
停止rabbitmq应用

rabbitmqctl stop_app

## 第七步：
把rabbitmq加入集群

在主机centos72上执行以下命令

rabbitmqctl join_cluster --ram rabbit@centos7

注意：如果是两个内存节点是可以相互作为集群添加的，但是我这里是只有两个虚拟机，一个作为磁盘节点，一个作为内存节点，所以当rabbit@centos7作为主节点的时候，就只需要在centos72上执行以上语句就可以加入到主节点上了。
启动rabbitmq应用  

rabbitmqctl start_app

在两个服务器上都查案状态：

rabbitmqctl cluster_status:
on centos72

```
[root@centos72 rabbitmq]# rabbitmqctl stop_app
    Stopping node rabbit@centos72 ...
    [root@centos72 rabbitmq]# rabbitmqctl join_cluster --ram rabbit@centos7
    Clustering node rabbit@centos72 with rabbit@centos7 ...
    [root@centos7 rabbitmq]# rabbitmqctl cluster_status
    Cluster status of node rabbit@centos72 ...
    [{nodes,[{disc,[rabbit@centos7]},{ram,[rabbit@centos72]}]},
     {running_nodes,[rabbit@centos7,rabbit@centos72]},
     {cluster_name,<<"rabbit@centos7">>},
     {partitions,[]},
     {alarms,[{rabbit@centos7,[]},{rabbit@centos72,[]}]}]
```


on centos7

```
[root@centos7 rabbitmq]# rabbitmqctl cluster_status
    Cluster status of node rabbit@centos7 ...
    [{nodes,[{disc,[rabbit@centos7]},{ram,[rabbit@centos72]}]},
     {running_nodes,[rabbit@centos72,rabbit@centos7]},
     {cluster_name,<<"rabbit@centos7">>},
     {partitions,[]},
     {alarms,[{rabbit@centos72,[]},{rabbit@centos7,[]}]}]
```










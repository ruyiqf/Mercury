# 数据分析系统

Mercury 数据分析系统 

数据库: Redis+Mongodb, Mysql集群

后端: 基于RQ框架的数据引擎，开发语言Python

数据源：Tushare

# 期货回测系统

* 支持多合约回测，多合约组合成为一个Portfolio进行独立回测
* 支持多策略回测，在一个Account下面可以组合多个Portfolio同时回测
* 支持Ticker级别的回测

## 开发环境
MacOS Python3.6 Python3.5也可以运行

## 启动回测服务

```python
python start.py run help

Usage: start.py run [OPTIONS]

Start to run a strategy

Options:
-h, help                   Show this message and exit.
-d, data-bundle-path PATH
                             指定数据包所在文件夹
progress / no-progress   show progress bar
                             显示策略回测进度
-f, strategy-dir PATH
                             策略文件夹，改文件夹下面可以实现自己的策略，支持多个策略，比如对冲策略，默认是该文件夹下面所有策略是一个账号
                    
-s, start-date TEXT
                             回测策略开始时间
-e, end-date TEXT
                             回测策略结束时间
-ic, initial-cash FLOAT
                             回测初始资金
-fq, frequency TEXT
                             回测频率，默认是分钟级别
-o, results-path PATH
                             回测结果文件，默认是pickle格式
```

## 获取最新期货数据（已经更新到最新数据）

```python
python start update_bundle help

Usage: start.py update_bundle [OPTIONS]

Sync Data Bundle of commodity future data specially

Options:
-d, data-bundle-path DIRECTORY
```
* 下载数据实例

python start update_bundle

## 测试策略
```python
python start.py run -f ./strategy -s 2016-09-01 -e 2017-03-07 -ic 1000000 -fq 1t -d ./vob/data -o ./result/
```

## 技术支持和技术讨论
QQ群：611039134



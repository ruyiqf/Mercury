# 启动回测服务

```python
python start.py run help
```
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
 

# 获取最新期货数据（已经更新到最新数据）

```python
python start update_bundle help
```

Usage: start.py update_bundle [OPTIONS]

Sync Data Bundle of commodity future data specially

Options:
-d, data-bundle-path DIRECTORY

**下载数据实例**

```python
python start update_bundle
```

## 测试策略
```python
python start.py run -f ./strategy -s 2016-09-01 -e 2017-03-07 -ic 1000000 -fq 1t -d ./vob/data -o ./result/
```
## 交易
```python
python start.py firm_bargain -f ./unit_test -s 2017-03-07 -e 2017-04-07 -ic 1000000 -fq 1t -d /Users/ruyiqf/winddata/data/
```

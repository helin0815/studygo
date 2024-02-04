#!/bin/env python

import os

if os.getenv("LI_ENV") == "prod":
    sentinels = "172.21.40.56:26384,172.21.40.104:6390,172.21.40.105:6390"
    cluster_name = "sentinel-op-sg-service-prod-6389"
    passwd = "op-sg-service-prod1q2w3e"
else:
    sentinels = "192.168.9.72:6382,192.168.9.73:6382,192.168.46.150:6379"
    cluster_name = "sentinel-dsd-public-redis-sentinel-dev-6381"
    passwd = "dsd-public-redis-sentinel-dev1q2w3e"


class RedisManage(object):

    def __init__(self, sentinels, clusterName, passwd, S="lichatRobot"): # 哨兵地址 集群名称 密码 唯一前置字符:预防测试redis重复数据
        from redis.sentinel import Sentinel

        self.sentinel = Sentinel(sentinels, socket_timeout=1)
        self.master = self.sentinel.master_for(clusterName, password=passwd)
        # self.slave = self.sentinel.slave_for(clusterName, password=passwd)
        self.s = S

    def get(self, key):
        key = "{s}-{key}".format(s=self.s, key=key)
        return self.master.get(key)

    def set(self, key, value, ex=None):
        if ex:
            ex = int(ex)
        return self.master.set("{s}-{key}".format(s=self.s, key=key), value, ex=ex)

    def delete(self, key):
        return self.master.delete("{s}-{key}".format(s=self.s, key=key))


# 实例化redis对象
REDIS = RedisManage([i.split(":")
                     for i in sentinels.split(",")], cluster_name, passwd)

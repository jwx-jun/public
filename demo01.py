#!/usr/local/bin/python
#-*- coding: UTF-8 -*-

# K线周期5min

import time
import pandas as pd
import numpy as np
import talib
import math

BBW_SET = 0.3   # BOLL极限宽度指标
angle_MA_60_SET = 1  # 角度初始值
# PERIOD = PERIOD_M5   # 获取不同周期的K线,参数值:PERIOD_M1指1分钟,PERIOD_M5指5分钟,PERIOD_M15指15分钟,PERIOD_M30指30分钟,PERIOD_H1指1小时,PERIOD_D1指一天
Position_state = 0    # 0表示没有持仓，1表示持仓
Bool_out_count = 0    # 开仓时K线在boll内部，计数2，超出布林上轨后减1，又进入布林上轨后再减1，此时Bool_out_count为0


def mian():               # 主程序
    Log(exchange.SetContractType("swap"))     # 设置为永续合约
    Log(exchange.GetAccount())
    while True:
        # def K_line():              # 获取K线数据
        # records = _C(exchange.GetRecords(PERIOD_M5))
        records = exchange.GetRecords(PERIOD_M5)
        if len(records) >= 100:
            # return records[:-2]
            doTicker(records[:-2])         # 调用策略函数
            Sleep(300)


def doTicker(r):                               # 策略
    global Position_state
    global Bool_out_count
    MA_10 = TA.MA(r, 10)                                     # 一维数组
    MA_30 = TA.MA(r, 30)
    MA_60 = TA.MA(r, 60)
    angle_MA_60 = math.atan((MA_60[-1] - MA_60[-2])/100)*180/3.1415926    # 计算MA60的斜率
    Log(angle_MA_60)
    boll = TA.BOLL(r, 60, 2)                                              # 返回值boll二位数组
    upLine = boll[0]
    midLine = boll[1]
    downLine = boll[2]
    BBW = (upLine[-1] - downLine[-1])/midLine[-1]                          # BOLL极限宽度指标
    if BBW <= BBW_SET and angle_MA_60 >= angle_MA_60_SET and Position_state == 0:
        buy()                   # 买入开仓
        if check_account(1):   # 判断买入
            Position_state = 1
            Bool_out_count = 2

    if Position_state == 1 and Bool_out_count == 2:
        if r[-1]["Close"] > upLine[-1]:
            Bool_out_count = Bool_out_count-1
    if Bool_out_count == 1:
        if r[-1]["Close"] < upLine[-1]:
            sell()               # 卖出平仓
            if check_account(2) == 0:    # 判断卖出
                # pass
                Position_state = 0
                Bool_out_count = 0



# 执行买入动作，打印买入信息
def buy():

    exchange.SetDirection("buy")    # 买入开多仓
    exchange.SetMarginLevel(5)
    id = exchange.Buy(-1, 10)     # 数字货币期货市价单方式下单，下单量参数的单位为合约张数
    Log("id:", id)
    return id



# 执行卖出动作，打印卖出信息
def sell():

    exchange.SetDirection("closebuy")   # 卖出平多仓
    id1 = exchange.Sell(-1, 10)
    Log("id:", id1)
    return id1


def check_account(mark):

    position = exchange.GetPosition()   # 获取当前持仓信息，可以传入一个参数，指定要获取的合约类型
    if len(position) > 0:
        Log("Amount:", position[0]["Amount"], "FrozenAmount:", position[0]["FrozenAmount"], "Price:",
            position[0]["Price"], "Profit:", position[0]["Profit"], "Type:", position[0]["Type"],
            "ContractType:", position[0]["ContractType"])
        # if mark == 3:
        #     return position[0]["Amount"]
        if position[0]["Amount"] and position[0]["FrozenAmount"] == 0 and mark == 1:   # mark 为表示买
            return position[0]["Amount"]
        if position[0]["Amount"] == 0 and position[0]["FrozenAmount"] == 0 and mark == 2:  # mark 为表示卖
            return position[0]["Amount"]


if __name__ == '__main__':
    mian()

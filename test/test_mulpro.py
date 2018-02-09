#!/usr/bin/env python
# -*- coding: utf-8 -*-
import multiprocessing


def printAdd(i, j):
    print("comming...")
    print(i + j)


if __name__ == "__main__":

    pool = multiprocessing.Pool()
    idx = 0

    def demo1():
        for i in range(5):
            if idx == 3:
                return
            pool.apply_async(printAdd, args=(1, i))



    demo1()
    pool.close()
    pool.join()
    print("多进程执行结束")
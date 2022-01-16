---
layout: post
comments: true
title: "Database System: Multi-Version Concurrency Control"
date: 2022-1-13 02:00:00
tags: Database 15-445
---

> 之前把解决并发控制的协议介绍了，这篇笔记主要记录Multi-Version Concurrency Control，它不是一个协议，而是更为具体的并发控制实现。（这篇有坑待填）

<!--more-->



## 1. Overview of MVCC

![image-20220115175023145]({{'//assets/images/2022-1-13-multi-version-concurrency-control/image-20220115175023145.png' | relative_url}})

MVCC的Main Idea是：Writers don’t block the readers. Readers don’t block the writers. 具体来说，当一个txn在对一个object进行写操作时，DBMS会对这个object创建一个新的版本；当txn读一个object时，读的是它最新的版本。它的好处在于，第一，它使得read-only的txn可以在不使用任何lock的情况下，读取consistent snapshot（Use timestamps to determine visibility）；第二，它支持time-travel queries，使得能检索不同时间点的数据库状态。

> With MVCC, the DBMS maintains multiple physical versions of a single logical object in the database. When a transaction writes to an object, the DBMS creates a new version of that object. When a transaction reads an object, it reads the newest version that existed when the transaction started

MVCC的设计由四个方面组成：

1. Concurrency Control Protocol （2PL, T/O, OCC...）
2. Version Storage 
3. Garbage Collection 
4. Index Management

先来举个例子直观理解一下：

![image-20220115180217516]({{'//assets/images/2022-1-13-multi-version-concurrency-control/image-20220115180217516.png' | relative_url}})

我们根据开始时间给txn分好timestamp后，开始执行。

1. T1读取数据库中原本有的最初版本的A0，Status Table中T1标记为Active用以区分是否已经Committed；

2. T1对A进行写操作，创建新版本，Begin timestamp设置为1，旧版本End timestamp设置为1；

![image-20220115180241759]({{'//assets/images/2022-1-13-multi-version-concurrency-control/image-20220115180241759.png' | relative_url}})

3. T2要读A，查Status Table可知，T1写操作产生的A1没有被commit，所以T2只能读取版本A0，Status Table中T2标记为Active；

4. T2要写A，但必须等会儿再写，因为T1还没有Commit，

![image-20220115180356385]({{'//assets/images/2022-1-13-multi-version-concurrency-control/image-20220115180356385.png' | relative_url}})

5. T1 要读A，这次读的是从它开始之后的最新版本，所以是读A1；
6. T1 Commit，更新Status Table中T1为Committed；
7. T2 此时可以创建新版本A3进行写操作，之后Commit；



## 2. Version Storage 

Version Storage 要去解决的问题是，第一，对于一个logical object，如何去储存它的多种physical version；第二，当我要去读这个logical object时，如何找到它的最新可读physical version。那么解决问题的方法是：The DBMS uses the tuples' pointer field to create a **version chain** per logical tuple. 下面介绍version chain的三种实现方式。



### 2.1 Append-Only Storage

### 2.2 Time-Travel Storage

### 2.3 Delta Storage

要考试了





## 3. Garbage Collection 

### 3.1 Tuple-level GC

### 3.2 Transaction-level GC

来不及了





## 4. Index Management

### 4.1 Logical Pointers

### 4.2 Physical Pointers

后面再补

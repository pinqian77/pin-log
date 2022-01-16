---
layout: post
comments: true
title: "Database System: Timestamp Ordering Concurrency Control"
date: 2022-1-12 02:00:00
tags: Database 15-445
---

> 上节课介绍了Two-Phase Locking Concurrency Control，这是一种用lock机制来实现的并发控制方法。这篇笔记主要记录Timestamp Ordering Concurrency Control，它完全基于timestamp实现，不用lock. 通过这节课可以明白：
>
> - Timestamp是在何时分发，分发给谁，如何分发
> - Timestamp Ordering Concurrency Control 是什么
> - strict T/O 不同在哪里
> - Isolation Level

<!--more-->



![image-20220115155901834]({{'//assets/images/2022-1-12-timestamp-ordering-concurrency-control/image-20220115155901834.png' | relative_url}})

## 1. Rules of Timestamp Ordering

### 1.1 Basic T/O

首先我们来区分一下两种方法。要实现并发控制，我们的essential motivation其实就是想要保证来自不同txn中的conflicting operations能够被serial地执行。之前讲的Two-Phase Locking是一种pessimistic的方法，它边运行边决定serializability order，用到是工具是各种**lock**；而Timestamp Ordering（T/O）是一种optimistic的方法，serializability order在txn被执行之前决定，用到的工具是**timestamp**。注意，T/O是在execute前决定serializability order的。



T/O其实思想很简单：按txn进场顺序分配timestamp，然后保证txn按照timestamp由小到大执行，这样就保证了serial schedule.

> **T/O Concurrency Control**
>
> Use timestamps to determine the serializability order of txns. If $TS(t_i) < TS(t_j)$, then the DBMS must ensure that the execution schedule is equivalent to a serial schedule where $T_i$ appears before $T_j$.

![image-20211228132151727]({{'//assets/images/2022-1-12-timestamp-ordering-concurrency-control/image-20211228132151727.png' | relative_url}})

每个txn开始时，会被分配一个timestamp，记作$TS(t_i)$. 这个txn的timestamp干嘛用的呢？它和要读写的resource有关联。

数据库中的resource X会记录上一个成功读或者写它的txn的timestamp。那么这样，在每个operation执行之前我们就可以进行check：

对于读操作来说，如果一个resource已经被一个未来的txn写过了，那读的肯定就有问题，所以要abort；

对于写来说，如果一个resource正在被未来的txn读，或者已经被未来的txn写了，那写的肯定就有问题，所以要abort.

下面来举两个例子：

![image-20220115163935694]({{'//assets/images/2022-1-12-timestamp-ordering-concurrency-control/image-20220115163935694.png' | relative_url}})

先看左图，T1先开始，T2后开始，所以分别分到timestamp 1和2。按照时间顺序，T1读B，未违反规则，B的R-TS更新为1；T2读B，未违反规则，B的R-TS的更新为2；T2写B，未违反规则，B的W-TS的更新为2；T1读A，未违反规则，A的R-TS的更新为1；T2读A，未违反规则，B的W-TS的更新为2；T1再读A，未违反规则，A的R-TS的保持为2；T2写A，未违反规则，A的W-TS的更新为2.

再看右图，T1先开始，T2后开始，所以分别分到timestamp 1和2。按照时间顺序，T1读A，未违反规则，A的R-TS更新为1；T2写A，未违反规则，A的W-TS的更新为2；T1想写A，但此时$TS(t_1)=1$, $W-TS(A)=2$, 违反了规则，所以T1将被abort.

这样的T/O协议保证schedule一定是conflict serializable的，且不会发生死锁，因为没txn在等，有错直接abort了。但是呢，要是一个txn非常长，它很有可能会面临starvation，因为慢慢长路，它被abort的可能性就很大。



### 1.2 Thomas Write Rule

![image-20220115165543602]({{'//assets/images/2022-1-12-timestamp-ordering-concurrency-control/image-20220115165543602.png' | relative_url}})

还有另一种写规则叫做**Thomas Write Rule**，这里简单介绍一下。简单来说，在普通写规则的基础上，Thomas Write Rule对于要去写一个未来写过的资源这种情况，直接skip（本来是要abort的）。通过上图右边的例子就能直观地理解这个规则了。



### 1.3 **strict T/O**

同样的，普通的T/O也会面临cascading rollback问题，我们可以通过给普通T/O加一些条件成**strict T/O**来解决。

> **strict T/O**
>
> Delay read or write requests until the youngest txn who wrote X before has committed or aborted.



## 2. Optimistic  Concurrency Control

先略后补



## 3.  Recoverable Schedule

接下来介绍**recoverable schedule**. 什么是recoverable的呢？每一个txn都commit了才叫recoverable的，否则DBMS不能保证可以恢复数据。

> **What is recoverable schedule?**
>
> A schedule is recoverable if txns commit only after <u>all txns</u> whose changes they read, <u>commit</u>.

![image-20220115170136786]({{'//assets/images/2022-1-12-timestamp-ordering-concurrency-control/image-20220115170136786.png' | relative_url}})



## 4. Isolation Level

Serializability可以允许我们解决并发问题，但强制执行它可能会parallelism降低而并限制性能。所以我们引入Isolation Level，使用weaker level of consistency 去 improve scalability.

> ![image-20220115173019814]({{'//assets/images/2022-1-12-timestamp-ordering-concurrency-control/image-20220115173019814.png' | relative_url}})

大部分数据库默认的隔离等级事read committed. MySQL默认repeatable read.




























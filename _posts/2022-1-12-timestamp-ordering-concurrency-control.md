---
layout: post
title: "Database System: Timestamp Ordering Concurrency Control"
date: 2022-1-12 02:00:00
tags: 15-445
---

> The previous lesson introduced Two-Phase Locking Concurrency Control, a method of concurrency control implemented using the lock mechanism. This note focuses on Timestamp Ordering Concurrency Control, which is based entirely on timestamps and does not use locks. In this lesson, you can understand:
> - When Timestamp is distributed, to whom and how it is distributed
> - What Timestamp Ordering Concurrency Control is
> - What is the difference between strict T/O
> - Isolation Level
<!--more-->



![image-20220115155901834]({{'//assets/images/2022-1-12-timestamp-ordering-concurrency-control/image-20220115155901834.png' | relative_url}})

## 1. Rules of Timestamp Ordering

### 1.1 Basic T/O

First let's distinguish between the two approaches. To achieve concurrency control, our essential motivation is actually to ensure that conflicting operations from different txn can be executed serially. Two-Phase Locking is a pessimistic approach, which determines the serializability order while running, using various tools **lock**, while Timestamp Ordering (T/O) is an optimistic approach, in which the serializability order is determined when the txn is executed. The serializability order is decided before txn is executed, and the tool used is **timestamp**. Note that T/O determines the serializability order before executing.

The idea of T/O is actually very simple: assign timestamps in the order of txn entry, and then ensure that txn is executed from smallest to largest according to the timestamp, so that the serial schedule is guaranteed.

> **T/O Concurrency Control**
>
> Use timestamps to determine the serializability order of txns. If $TS(t_i) < TS(t_j)$, then the DBMS must ensure that the execution schedule is equivalent to a serial schedule where $T_i$ appears before $T_j$.

![image-20211228132151727]({{'//assets/images/2022-1-12-timestamp-ordering-concurrency-control/image-20211228132151727.png' | relative_url}})

At the beginning of each txn, a timestamp is assigned as $TS(t_i)$. What is the purpose of this txn timestamp? It is associated with the resource to be read or written.

Resource X in the database will record the last txn timestamp that successfully read or wrote it, so that before each operation is executed we can check:

For a read operation, if a resource has already been written by a future txn, the read must be faulty, so abort;

For writes, if a resource is being read by a future txn, or has already been written by a future txn, then the write must be faulty, so abort.

Here are two examples:

![image-20220115163935694]({{'//assets/images/2022-1-12-timestamp-ordering-concurrency-control/image-20220115163935694.png' | relative_url}})

Let's first look at the figure on the left. T1 starts first, followed by T2, so they receive timestamps 1 and 2 respectively. In chronological order, T1 reads B, which doesn't violate any rules, and B's R-TS is updated to 1; T2 reads B, which also doesn't violate any rules, and B's R-TS is updated to 2; T2 writes to B, which again doesn't violate any rules, and B's W-TS is updated to 2; T1 reads A, which doesn't violate any rules, and A's R-TS is updated to 1; T2 reads A, which doesn't violate any rules, and A's W-TS is updated to 2; T1 reads A again, which doesn't violate any rules, and A's R-TS remains at 2; T2 writes to A, which doesn't violate any rules, and A's W-TS is updated to 2.

Now, let's look at the figure on the right. T1 starts first, followed by T2, so they receive timestamps 1 and 2 respectively. In chronological order, T1 reads A, which doesn't violate any rules, and A's R-TS is updated to 1; T2 writes to A, which doesn't violate any rules, and A's W-TS is updated to 2; T1 wants to write to A, but at this time, $TS(t_1)=1$, and $W-TS(A)=2$, which violates the rules, so T1 will be aborted.

This type of Timestamp Ordering (T/O) protocol ensures that the schedule is always conflict serializable and no deadlock will occur because no transaction is waiting, any errors will lead to immediate abortion. However, there's a downside - if a transaction is very long, it may face starvation. As the transaction's length increases, the likelihood of it being aborted also increases.



### 1.2 Thomas Write Rule

![image-20220115165543602]({{'//assets/images/2022-1-12-timestamp-ordering-concurrency-control/image-20220115165543602.png' | relative_url}})

There is another kind of write rule called **Thomas Write Rule**, which is briefly described here. Simply put, on top of the normal write rule, the Thomas Write Rule directly skips a resource that was written in the future (and was meant to be aborted). This rule can be understood intuitively by the example on the right side of the figure above.

### 1.3 **strict T/O**

Similarly, ordinary T/O will also face cascading rollback problem, which we can solve by adding some conditions to ordinary T/O into **strict T/O**.

> **strict T/O**
> Delay read or write requests until the youngest txn who wrote X before has committed or aborted.

## 2. Optimistic Concurrency Control

Optimistic Concurrency Control (OCC) is a type of concurrency control for relational databases. OCC assumes that multiple transactions can complete without affecting each other, and therefore transactions can proceed without locking any resources. When a transaction is ready to commit, it validates that no other transactions have modified the data it has read. If this validation fails, the transaction is rolled back and can be restarted.

## 3.  Recoverable Schedule

Next, let's discuss the concept of a recoverable schedule. So, what is a recoverable schedule? It refers to a state where every transaction has committed, which allows the DBMS to ensure data recovery.

> **What is recoverable schedule?**
> A schedule is recoverable if txns commit only after <u>all txns</u> whose changes they read, <u>commit</u>.

![image-20220115170136786]({{'//assets/images/2022-1-12-timestamp-ordering-concurrency-control/image-20220115170136786.png' | relative_url}})

This concept is crucial to maintain the integrity and consistency of data in the event of failures. The ability to recover to a consistent state after a failure is a key aspect of any reliable database system.


## 4. Isolation Level

> ![image-20220115173019814]({{'//assets/images/2022-1-12-timestamp-ordering-concurrency-control/image-20220115173019814.png' | relative_url}})

The isolation level of a transaction refers to the degree to which the changes made by one transaction are visible to other concurrent transactions. There are four isolation levels defined by the SQL standard, each providing a different balance between performance and the likelihood of concurrency phenomena. The four levels, in increasing order of isolation, are Read Uncommitted, Read Committed, Repeatable Read, and Serializable.

Understanding the trade-offs between the different isolation levels helps in selecting the most appropriate level for a particular transaction or application, considering factors such as the nature of the data, the requirements of the application, and the acceptable level of risk for concurrency phenomena like dirty reads, non-repeatable reads, and phantom reads.



























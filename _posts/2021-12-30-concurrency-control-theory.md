---
layout: post
title: "Database System: Concurrency Control Theory"
date: 2021-12-30 02:00:00
tags: 15-445
---



> This lesson introduces the Concurrency Control and Recovery section from a high level perspective, and the specific implementation will be introduced in the next lesson. Through this lesson we can understand:
> - What is Transaction, Schedule
> - Why we need Concurrency Control and Recovery
> - ACID corresponding to the case
> - Serial Schedule, Serializable Schedule, Conflict Serializable Schedule
> - How to determine Conflict Serializable Schedule

<!--more-->

First, let's talk about motivation. How do we avoid a race condition when we operate on a record at the same time, and how do we ensure correctness when we encounter an external force majeure power failure while operating on the database? These are the questions that this section of Concurrency Control and Recovery will address.

> **Motivation**
> 
> Race condition may cause updates lost, thus we need <u>Concurrency Control</u>.
> Database durability may be broken, thus we need  <u>Recovery</u>.

Second, we need to know what **Transaction** is.

> A transaction(txn) is the execution of <u>a sequence of one or more operations</u> on a database to perform some higher-level function. It is the <u>basic unit of change</u> in a DBMS.
> In SQL, txn
> - starts with <u>BEGIN</u> command.
>- stops with either <u>COMMIT</u> or <u>ABORT</u>:
>   - if commit, the DBMS either saves all the changes or aborts it.
>   - if abort, all changes are undone.


In the simplest scenario, each transaction is executed fully one after another. While this method minimizes errors, it is highly inefficient. If our system is multi-core, it would be wasteful to only use one core at a time while the others remain idle. Therefore, we aim to enable different transactions to be executed concurrently.

> **Problem Statement**
> 
> To achieve better utilization and increase response time to users, we aim to allow <u>concurrent execution of independent transactions</u>, while assuring correctness.

Concurrency means that operations in different transactions will be executed interleaved, which means that errors may occur, so we need to specify a reasonable criterion to determine the legality of concurrency, and this criterion is **ACID**.

> **Atomicity**: all actions in the txn happen, or none happen.
> **Consistency**: if each txn is consistent and the DB starts consistent, then it ends up consistent.
> **Isolation**: execution of one txn is isolated from that of other txns.
> **Durability**: if a txn commits, its effects persist.

The methods we talk about later are all designed to achieve atomicity, isolation, durability, because consistency is actually a desired criterion and is outside the control of the DBMS. Here we give a high level overview, we mainly achieve atomicity and durability through logging and shadow paging, and isolation through concurrency control protocol.

The concurrency of each transaction, looking inward, means that the operations from different transactions are executed in a certain order, which we call **Schedule**. Now to see if the concurrency is legal, it is the same as to see if the schedule is legal. So let's see how to determine whether it is legal or not. Here "legal", that is, whether "correct", actually refers to whether it can **Serializable**.

We know that it must be legal to execute transactions in order, so if the schedule is equivalent to this order of execution, it must also be legal.

> If the schedule is equivalent to some serial execution, then it is correct.

If a schedule is itself serial, i.e. the operation of each transaction is not interleaving, then we call it **Serial Schedule**. If the operation itself is interleaving, but the result is equivalent to a Serial Schedule, we call it a **Serializable Schedule**.

> **Definition of Serial Schedule**
>
> A schedule that dose not interleave the actions of different transactions.
> 
> **Definition of Serializable Schedule**
>
> A schedule that is equivalent to some serial execution of the transactions.


What does a serializable schedule mean? It means more flexible, provides flexibility, and some operations can be swapped in order to achieve more efficient concurrency. So the question arises, how do we determine whether equivalence it, how do we know which operations can swap positions without affecting the result? Then it's time to introduce **conflicting operations**.

> **Definition of Conflicting Operation**
>
> 1. They are by different transactions,
> 2. They are on the same object,
> 3. At least one of them is a write().

According to the definition, we know that there are only three cases of conflicting operation, which correspond to three insecure cases:

- read-write conflict corresponds to unrepeatable reads.

![image-20211226222332279]({{ '/assets/images/2021-12-30-concurrency-control-theory/image-20211226222332279.png' | relative_url }})



- write-read conflict corresponds to reading uncommitted data ("dirty read").

![image-20211226222455660]({{ '/assets/images/2021-12-30-concurrency-control-theory/image-20211226222455660.png' | relative_url }})



- write-write corresponds to overwriting uncommitted data.

![image-20211226222542349]({{ '/assets/images/2021-12-30-concurrency-control-theory/image-20211226222542349.png' | relative_url}})

Now, we can check (not generate) whether a schedule is correct or not, just to determine whether it is serializable or not. The former is the standard for most database implementations, and the latter only exists in the rational world, so I will only focus on the former in the notes that follow.

Just now, we talked about equivalent schedule, which does not require the same intermediate process, but only the same database operation, and the final result is the same. Now let's talk about **conflict equivalent**, which requires that the operations of two transactions should be the same and the order of conflicting operations should be the same.

> **Definition of conflict equivalent**
>
> Two schedules are conflict equivalent iff:
>
> 1. They involve the same actions of the same transactions, and
> 2. Every pair of conflicting actions is ordered the same way.

Taking this a step further, we can obtain a schedule that is stricter than serializable, conflict serializable schedule:

> **Definition of Conflict Serializable Schedule**
>
> Schedule is conflict serializable if it is conflict equivalent to some serial schedule.

In layman's terms, that is, if you can swap the order of non-conflicting operations in a schedule, and end up with a serial schedule, then the schedule that you move around is a conflict serializable schedule.

We usually use the Precedence Graph (Dependency Graph) to determine whether a schedule is a conflicting serializable schedule, there is a circle of the chemical is not.

Finally then, some of the most important concepts in this section can be summarized by this diagram.

![image-20211226224957811]({{ '/assets/images/2021-12-30-concurrency-control-theory/image-20211226224957811.png' | relative_url}})

---
layout: post
title: "Database System: Two-Phase Locking Concurrency Control"
date: 2022-1-08 02:00:00
tags: 15-445
---

> This lesson mainly introduces the Two-Phase Locking mechanism. After learning, you can master:
> - What is Two-Phase Locking
> - What is Rigorous Two-Phase Locking, why rigorous is needed
> - How to handle deadlock
> - Why and how to use Intention lock

<!--more-->



## 1. Overview of Lock Schema

In our last lesson, we discussed that we could check the legality of a schedule by seeing whether the non-conflict operations can be swapped to achieve a serial schedule. However, this only applies under ideal conditions. In reality, we cannot know all operations in advance, hence, cannot check for legality. Therefore, we need other methods to support reasonable concurrency. This note mainly records the use of the **locks** mechanism to solve this problem.



> **Motivation**
> We need a way to guarantee that all execution schedules are correct (i.e., serializable) without knowing the entire schedule ahead of time.

The DBMS includes a **Lock Manager**, which decides whether a transaction (txn) can be locked. The relationship between the main entities is as follows: A **Schedule** is composed of operations from different **Transaction**. During the execution process, the Transaction applies for a Lock from the Lock Manager. The Lock applies to resources in the database, which can be a piece of data or a table. To implement on-the-fly concurrency control, let's first understand two basic types of Locks. This means that reads can occur simultaneously, but writes must be unique.

> **Basic Lock Types**
>
> S-LOCK: Shared locks for reads
>
> X-LOCK: Exclusive locks for writes

The execution process using the Lock mechanism is as follows:

1. The txn requests (or upgrades) a Lock from the Lock Manager
2. The Lock Manager decides whether to approve the request based on the Lock status of other txns (check the lock table)
3. The txn releases the Lock when it is no longer needed
4. The Lock Manager updates the lock table and assigns the Lock to other waiting txns



## 2. 2PL Ensures Conflict Serializable

Next, we aim to solve the problem left from the last lesson: how to control concurrency during database runtime. The solution is the **Two-phase locking** (2PL) protocol.

> **What is Two-Phase Locking**
>
> It determines whether a txn can access an object in the database on the fly, which does not need to know all the queries that a txn will execute ahead of time.
>
> Phase 1: Growing
>
> <u>Each</u> txn requires the locks that it needs from the lock manager, while the lock manager grants/denies lock requires.
>
> Phase 2: Shrinking
>
> The txn is allowed to only release locks that it previously acquired. No permission to acquire new locks.
>
> 要注意的是，Growing，Shrinking是针对每一个txn来说的，并非整一个schedule.

2PL is a **pessimistic** concurrency control protocol, used to determine whether a txn is allowed to access resources in the database. This protocol does not require knowledge of the operations that the transaction will execute in advance.

So how does it work? As the name implies, it is divided into two phases: Phase 1 is the phase to apply the lock and Phase 2 is the phase to release the lock.

So why does this ensure that the schedule is conflict serializable? This is how I understand it. It's like the sliding window problem you encounter when doing algorithmic problems, where there is a process of expansion to certain conditions and then contraction. If we use locks wisely, the execution is legal and the direction is monotonic, there is no possibility of a loop in the dependency graph, and no loop means conflict serializable.



## 3. Strict 2PL Avoids Cascading Abort

Although this is enough to ensure the correctness of the schedule, this common 2PL also needs to face the problem of **cascading aborts**. The cascading aborts problem refers to the case where one txn aborts in a schedule and the other unnecessary txn aborts as well. The solution is **Strict 2PL**. The difference between the grow phase of this upgraded 2PL and the shrink phase is that all locks are released at once after all operations are completed.

> **What is Strict Two-Phase Locking**
>
> The txn is only allowed to release locks after is has ended, i.e., committed or aborted.

![image-20211227195935984]({{'/assets/images/2022-1-08-two-phase-locking-concurrency-control/image-20211227195935984.png' | relative_url}})



## 4. Deadlock Handling

But the above is still not perfect, deadlock is always an unavoidable problem, we either detect it when it happens and solve it, or prevent it before it happens. 

For **deadlock detection**, we **periodically use a waits-for graph** to detect that a deadlock has occurred if a loop is formed. If the lock is on, a victim txn is selected to abort, allowing the deadlock to be relieved and the DBMS to decide how far to roll back.

![image-20220115151556221]({{'/assets/images/2022-1-08-two-phase-locking-concurrency-control/image-20220115151556221.png' | relative_url}})

For **deadlock prevention**, we have two prevention methods wait-die and wound-wait. In both methods, each txn is given a priority based on the start time, and a high priority means that the txn starts earlier. How to understand these two methods? First of all, we have to make it clear that the subjects of these two statements are actually for the txn to apply for Lock; then, the first word indicates what to do when the subject's priority is high, and the second word indicates what to do when the subject's priority is low:

![image-20220115152351331]({{'/assets/images/2022-1-08-two-phase-locking-concurrency-control/image-20220115152351331.png' | relative_url}})

In the above case, T1 is applying for a lock, so the subject is T1, and we know that T1 starts first, so T1 has high priority. This is the case of "high subject priority", so let's look at the first word. Then if it is Wait-Die, then T1 waits T2, T1 has to wait for T2 to release A to use A. If it is Wound-Wait, then T1 wounds T2, T1 hurts T2, T2 is directly abort, A is grabbed by T1 from T2.

In the following one, T2 applies for lock, so the subject is T2, but still T1 starts first, so T1 has high priority. This is a case of "low subject priority", so we have to look at the second word. So if it's Wait-Die, T2 Die, meaning it's suicide, let A be T1; if it's Wound-Wait, then T2 wait, have to wait for T1 to release it.



## 5. Intention Locks

Finally, the introduction of **Intention locks** to achieve **Hierarchical Locking.** The reason is that we are far from talking about the lock object is actually a record, but in practice, if you go by this lock, the efficiency will be very low, we may need to lock a table at once so lock to increase efficiency. But locking objects of different sizes makes the design of lock very cumbersome, so we introduce the concept of **lock granularity**, with intention locks are used to achieve such needs.

> **Definition of Intention Locks**
>
> An intention lock allows a <u>higher-level node</u> to be locked in <u>shared or exclusive</u> <u>mdoe</u> without having to check all descendent nodes. If a node is locked in an intention mode, then some txn <u>is doing explicit locking</u> at a lower level in the tree.
>
> **Intention-Shared(IS)**
>
> Indicates explicit locking at lower level with shared locks.
>
> **Intention-exclusive(IX)**
>
> Indicates explicit locking at lower level with exclusive locks.
>
> **Shared+Intention-exclusive(SIX)**
>
> The subtree is locked explicitylt in shared mode and explicit locking is being done at a lower level with exclusive-mode locks.

To summarize, if we want to set S or IS on a node, then the node's parent node must be set to at least IS; if we want to set X, IX, or SIX on a node, then the node's parent node must be set to at least IX.

![image-20211227211109853]({{'//assets/images/2022-1-08-two-phase-locking-concurrency-control/image-20211227211109853.png' | relative_url}})

So far, our schedule classification has been further expanded. In fact, you can look at this category of No cascading aborts separately, after all, strong strict 2PL is designed to avoid cascading aborts, which is stricter than conflict serializable and weaker than serial, so it is better to remember.

![image-20211227200617795]({{'/assets/images/2022-1-08-two-phase-locking-concurrency-control/image-20211227200617795.png' | relative_url}})


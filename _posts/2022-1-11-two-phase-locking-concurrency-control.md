---
layout: post
comments: true
title: "Database System: Two-Phase Locking Concurrency Control"
date: 2022-1-11 02:00:00
tags: Database 15-445
---

> 这节课主要介绍了Two-Phase Locking机制，学完可以掌握：
>
> - Two-Phase Locking是什么
> - Rigorous Two-Phase Locking是什么，为什么需要rigorous
> - 如何handle deadlock
> - 为什么要有， 怎么用Intention lock

<!--more-->



## 1. Overview of Lock Schema

上节课我们虽然讲了可以通过schedule能否被swap non-conflict operation得到一个serial schedule来check它是不是合法的，但这只是理想状况下，现实中，我们并不能事先知道全部的operation，也就不能check合法性，所以需要另外的方法来支持合理的并发。这篇笔记主要记录用**locks**机制来解决这个问题。

> **Motivation**
>
> We need a way to guarantee that all execution schedules are correct (i.e., serializable) without knowing the entire schedule ahead of time.



DBMS包含一个**Lock Manager**，用于决定txn是否可以锁定。 主体间的关系是这样的：**Schedule**由不同**Transaction**的operation组成，执行过程中，Transaction向Lock Manager申请**Lock**，Lock的作用对象为数据库中的resource，可以是一条数据，也可以是一张表。为了实现on the fly的concurrency control，我们先来了解两种最基本的Lock。这意味着，读可以一起读，要写只能唯一写。

> **Basic Lock Types**
>
> S-LOCK: Shared locks for reads
>
> X-LOCK: Exclusive locks for writes

使用Lock机制的执行流程是这样的：

```markdown
1. txn向Lock Manager请求（或者升级）Lock
2. Lock Manager根据当前其他txn持有的Lock状态（查看锁表），来决定是否批准请求
3. 当txn不再需要Lock时，释放Lock
4. Lock Manager更新锁表，把Lock给其他等待中的txn
```



## 2. 2PL Ensures Conflict Serializable

接下来，就是为了解决上节课的遗留问题：如何在数据库运行的时候进行并发控制。解决方法为**Two-phase locking**（2PL）protocol.

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

2PL 是一种**悲观的**并发控制协议，用于确定是否允许txn访问数据库中的resource，这种协议不需要提前知道事务将执行的操作。

那么它是怎么做的呢？顾名思义，它分为两个阶段：Phase 1为申请锁的阶段，Phase 2为释放锁的阶段。

![image-20211227191643014]({{'/assets/images/2022-1-11-two-phase-locking-concurrency-control/image-20211227191643014.png' | relative_url}})

那么为什么这样可以确保schedule是conflict serializable的呢？我是这么理解的，这就像是做算法题时遇到的滑动窗口问题，有一个扩张到一定条件再收缩的过程。而这个过程的方向性是唯一的，就像从左往右去遍历一个数组，在这里便是遍历所有的operations。那么如果我们合理地用锁，执行是合法的，方向是单调的，就不可能在dependency graph中成环，不成环也就意味着conflict serializable.



## 3. Strict 2PL Avoids Cascading Abort

虽然这已经足以确保schedule的正确性，但这个普通的2PL还需要面对**cascading aborts**的问题。以上其实我们只关注了txn每次都commit的情况，而没有考虑abort的情况。cascading aborts problem指的就是在一个schedule中，一个txn abort了，连带把另外的不必要abort的txn也abort的情况。解决方法是**Strict 2PL**. 这种升级过的2PL的grow阶段没什么不同，shrink阶段的不同在于只在全部操作完成后一次性release所有locks.

> **What is Strict Two-Phase Locking**
>
> The txn is only allowed to release locks after is has ended, i.e., committed or aborted.

![image-20211227195935984]({{'/assets/images/2022-1-11-two-phase-locking-concurrency-control/image-20211227195935984.png' | relative_url}})



## 4. Deadlock Handling

但上述仍不完美，deadlock总是无法避免的问题，我们要么它在发生时detect出来再解决，要么在发生了之前prevent. 

对于**deadlock detection**，我们**periodical地用waits-for graph**去检测，如果成环则发生了死锁。如果锁上了，一个victim txn会被选中abort掉，使得僵局缓解，DBMS来决定roll back多远。

![image-20220115151556221]({{'/assets/images/2022-1-11-two-phase-locking-concurrency-control/image-20220115151556221.png' | relative_url}})

对于**deadlock prevention**，我们有wait-die和wound-wait两个预防方法。这两种方法里，各个txn都会根据启动的时间被赋予priority，priority高，就代表这个txn启动得早。那怎么来理解这两种方法呢？首先，我们要明确，这两个语句的主语其实都是针对要申请Lock的txn；然后，前一个单词表示的是主语priority高的时候要做的事情，后一个单词表示主语priority低的时候要做的事情，下面来举个例子：

![image-20220115152351331]({{'/assets/images/2022-1-11-two-phase-locking-concurrency-control/image-20220115152351331.png' | relative_url}})

上面这个，T1要申请锁，所以主语是T1，且我们知道T1先开始，所以T1优先级高。这时候满足“主语优先级高”的情况，所以我们看第一个单词。那么如果是Wait-Die，那么T1 waits T2，T1得等T2释放A了才能用A；如果是Wound-Wait，那么T1 wounds T2，T1伤害了T2，T2直接被abort，A被T1从T2那里抢了过来。

下面这个，T2申请锁，所以主语是T2，但仍然是T1先开始，所以T1优先级高。这时候满足“主语优先级低”的情况，所以我们得看第二个单词。那么如果是Wait-Die，T2 Die了，意思说就自杀了，把A让个T1了；如果是Wound-Wait，那么T2 wait，得等T1释放才行。



## 5. Intention Locks

最后，介绍了用**Intention locks**去实现**Hierarchical Locking.** 原因是，我们之前距离讲到的lock作用对象其实都是一条一条record，但实际中如果按这样去锁，效率会很低，我们可能会需要一次性锁一张table这样的lock去增加效率。但锁不同大小的对象就让lock的设计很繁琐，所以我们引入**锁粒度**的概念，用intention locks被使用去实现这样的需求。

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

总结一下，如果我们要在一个node上设置S或者IS，那么这个node的parent node至少必须被设置了IS；如果要在一个node上设置X，IX，或者SIX，那么这个node的parent node至少必须被设置了IX.

![image-20211227211109853]({{'//assets/images/2022-1-11-two-phase-locking-concurrency-control/image-20211227211109853.png' | relative_url}})

那么至此，我们的schedule分类进一步拓展。其实可以把No cascading aborts这一类单独看，毕竟strong strict 2PL设计出来就是为了避免cascading aborts，它比conflict serializable严格，比serial弱，这样就比较好记忆了。

![image-20211227200617795]({{'/assets/images/2022-1-11-two-phase-locking-concurrency-control/image-20211227200617795.png' | relative_url}})


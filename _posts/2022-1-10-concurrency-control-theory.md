---
layout: post
comments: true
title: "Database System: Concurrency Control Theory"
date: 2022-1-10 02:00:00
tags: Database 15-445
---



> 这节课从一个high level的角度介绍了Concurrency Control 和 Recovery部分，具体实现方法会在下一节课中介绍。通过这节课我们可以了解：
>
> - Transaction，Schedule是什么
> - 为什么需要Concurrency Control and Recovery
> - ACID分别对应的情况
> - Serial Schedule，Serializable Schedule，Conflict Serializable Schedule的关系是什么
> - 如何判断Conflict Serializable Schedule
>

<!--more-->



首先我们来说动机。当我们同时对一条记录进行操作时，如何避免race condition？当在操作数据库时遭遇外界不可抗力的power failure，要如何确保它的正确性？诸如此类问题，就是这节Concurrency Control and Recovery要去解决的。

> **Motivation**
>
> Race condition may cause updates lost, thus we need <u>Concurrency Control</u>.
>
> Database durability may be broken, thus we need  <u>Recovery</u>.



其次，我们需要知道 **Transaction** 是什么。

> A transaction(txn) is the execution of <u>a sequence of one or more operations</u> on a database to perform some higher-level function. It is the <u>basic unit of change</u> in a DBMS.
>
> In SQL, txn
>
> - starts with <u>BEGIN</u> command.
>- stops with either <u>COMMIT</u> or <u>ABORT</u>:
>   - if commit, the DBMS either saves all the changes or aborts it.
>   - if abort, all changes are undone.
> 



最简单的情况，transaction来一个完整地执行一个，这样难出错，但效率太低。如果我们的设备是multi-core的，总不能每次只用一个核让其他的都闲着吧。所以呢，我们想让不同的transaction能够并发地被执行。

> **Problem Statement**
>
> To achieve better utilization and increase response time to users, we aim to allow <u>concurrent execution of independent transactions</u>, while assuring correctness.



并发意味着不同的transaction中的operation会交错地被执行，这意味着可能会出错，所以我们需要规定合理的criteria去判断并发的合法性，这个criteria便是**ACID**.

> **Atomicity**: all actions in the txn happen, or none happen.
>
> **Consistency**: if each txn is consistent and the DB starts consistent, then it ends up consistent.
>
> **Isolation**: execution of one txn is isolated from that of other txns.
>
> **Durability**: if a txn commits, its effects persist.

我们后面讲到的方法，都是为了去实现 atomicity, isolation, durability，因为consistency其实算是一个desired criterion，在DBMS的掌控范围之外。 这里给一个high level的概述，我们主要通过logging和shadow paging实现atomicity和durability，通过concurrency control protocol实现isolation.



各个transaction的并发，往内看就是来自不同transaction的operations按一定的顺序被执行，我们把这叫做**Schedule**。现在要去看这个并发合不合法，就等同于去看这个schedule合不合法。那么接下里就来看如何判断合不合法。这里“合法”，即是否“correct”，其实指的就是是否能**Serializable**.

我们知道，按序执行transaction一定是合法的，所以如果schedule等同于这样顺序执行的化，也一定时合法的。

> If the schedule is equivalent to some serial execution, then it is correct.

如果一个schedule本身就是serial的，即各个transaction的operation是不interleaving的，那我们称它为**Serial Schedule**. 那有些本身operation是interleaving的，但是运行结果等同于Serial Schedule的，我们称它为**Serializable Schedule**.

> **Definition of Serial Schedule**
>
> A schedule that dose not interleave the actions of different transactions.
>
> **Definition of Serializable Schedule**
>
> A schedule that is equivalent to some serial execution of the transactions.



一个serializable的schedule意味着什么呢？意味着更灵活，提供了flexibility，一些operation可以互换顺序以实现更高效的并发。那么问题来了，我们要怎么去判断是否equivalence呢，怎么知道哪些operation可以互换位置而不影响结果呢？那么介绍**conflicting operation**的时候到了。

> **Definition of Conflicting Operation**
>
> 1. They are by different transactions,
> 2. They are on the same object,
> 3. At least one of them is a write().

根据定义，我们可以知道conflicting operation一共就三种情况，分别对应了三种不安全的情况：

- read-write conflict 对应 unrepeatable reads.

![image-20211226222332279](/../../../../../media/2022-1-10-concurrency-control-theory/image-20211226222332279.png)



- write-read conflict 对应 reading uncommitted data ("dirty read").

![image-20211226222455660](/../../../../../media/2022-1-10-concurrency-control-theory/image-20211226222455660.png)



- write-write 对应 overwriting uncommitted data.

![image-20211226222542349](/../../../../../media/2022-1-10-concurrency-control-theory/image-20211226222542349.png)



那么现在，我们可以去check（注意不是generate）一个schedule是不是correct的了，只需要去判断是不是serializable的就行。这里15455对serializability分了两个等级，conflict serializability和view serializability。前者是目前大多数数据库实现的标准，后者只存在于理形世界中，后面的笔记我只关注前者。



刚才在前面我们讲到了equivalent schedule，它不需要中间过程的一样，只需要对同一个数据库进行操作，最后的结果是一样的就行。现在我们来讲**conflict equivalent**，它要求两个transaction的operation要一样，且conflicting operation顺序得一样。

> **Definition of conflict equivalent**
>
> Two schedules are conflict equivalent iff:
>
> 1. They involve the same actions of the same transactions, and
> 2. Every pair of conflicting actions is ordered the same way.

更进一步，我们可以得到一个比serializable更严格的schedule，conflict serializable schedule：

> **Definition of Conflict Serializable Schedule**
>
> Schedule is conflict serializable if it is conflict equivalent to some serial schedule.

通俗一点,就是说如果你能把一个schedule中non-conflicting的operation交换顺序, 最终得到一个serial schedule,那么被你移来移去的那个schedule就是个conflict serializable schedule.

我们通常会用Precedence Graph(Dependency Graph)来判断一个schedule是不是conflict serializable schedule，有圈的化就不是。



那么最后，这一节最重要的几个概念可以由这张图来概括。

![image-20211226224957811](/../../../../../media/2022-1-10-concurrency-control-theory/image-20211226224957811.png)

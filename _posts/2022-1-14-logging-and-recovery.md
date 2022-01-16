---
layout: post
comments: true
title: "Database System: Logging and Recovery"
date: 2022-1-14 02:00:00
tags: Database 15-445
---



> 这篇笔记主要记录 Logging 和 recovery 机制。
>
> 1. Logging: txn正常进行时，进行一些记录，使得万一要是crash了能够通过这些记录复原
> 2. Recovery: txn crash/failure了，系统重启后对数据库进行恢复操作。

<!--more-->



首先，我们要清楚，是什么导致数据库需要去recovery，换言之，我们之前一直在说的failure到底指什么。我们能去恢复的只有前两个：

1. Transaction Failure
   - Logical error （txn冲突了）
   - Internal state error （如deadlock了必须abort某个txn）
2. System Failure
   - Software Failure （像除0运算）
   - Hardware Failure（power failure要注意的是，当我们在讨论这个时，我们是假设disk中的数据是不会被损坏的）
3. Storage Media Failure



那么接下来，我们就来说说logging，分别从why和how两个方面去介绍（跳过了15445中有些内容）。



## 1. Why there are multiple logging mechanisms

我们必须先知道一点Schedule，Buffer Pool，Disk间运行的机制。下面通过一个例子来说明一下流程：

![image-20220114184213317]({{'//assets/images/2022-1-14-logging-and-recovery/image-20220114184213317.png' | relative_url}})

我们从左图读数据开始。**Schedule**受**Execution Engine**控制，我们现在要读A，那么Execution Engine会向**Buffer Pool**发出请求A，Buffer Pool查看A所在的**Page**是否在Pool中，如果已经在了，就给Execution Engine一个**Pointer**，并在之后确保这个含A的Page会一直在Pool中；如果不在，就从**Disk**中找到A所在的Page，将整个Page移到Pool中，然后做上述操作。

然后看右图写数据。Execution Engine被分发的Pointer指向A所在Page的内存地址，可以对A进行写操作。写操作是发生在内存中的Buffer Pool中，在txn未commit前，改动的数据都不会写入Disk中（这句话可能不严谨，因为在Steal Policy的情况下，未发起commit的txn改动的数据可能会躺枪，被另一个发起commit的txn连带着把数据写回Disk）。我们把有过数据改动，但还没写回Disk的Page叫做**Dirty Page**.

![image-20220114185700126]({{'//assets/images/2022-1-14-logging-and-recovery/image-20220114185700126.png' | relative_url}})

之后看COMMIT操作，在这里，我会把这个COMMIT和Log机制的联系说一下。

当一个txn发起COMMIT时，到底发生了什么？我觉得我们得把COMMIT分解，分解成一个是**txn**发起COMMIT的动作，另一个是**Log Manager**把COMMIT这则log写入Disk的动作。但COMMIT的目的是什么呢？是要把数据写回Disk。我们在这里讲三种log方式，其实讲的是，我应该在txn发起COMMIT请求后的**什么时候**，把Log Manager的COMMIT写入Disk，因为只有Disk中的数据才是稳定安全的，而Log也在Disk中。而这个“什么时候”，指的就是把数据写回Disk这个时间点，如果COMMIT Log写在数据写回Disk之后，我们采用的就是undo log；如果COMMIT Log写在数据写回Disk之前，我们采用的就是redo log. 具体的不同会在之后说到。

![image-20220114192416468]({{'//assets/images/2022-1-14-logging-and-recovery/image-20220114192416468.png' | relative_url}})

还有两个比较重要的概念也需要讲一下：**Force** 和 **Steal** policy.

如果我们采用Force Policy，那意味着，该txn的数据必须在此时被写回Disk中（force to be written to disk）。但我们知道，Buffer Pool移动的是Page，那对于上图被改动过的A怎么办呢，它所在的txn还未发起COMMIT. 这就涉及到是否允许Steal Page. 如果我们允许还未COMMIT的A也连带着被写回Disk，那么这就是Steal Policy；如果我们不允许A被写回Disk，那就是Non-Steal Policy. 

上图展现的是NO-STEAL + FORCE策略。这个策略有什么好处呢？第一，对于所有aborted txn，我们没有必要去做undo操作，因为no-steal policy保证了它不会被其他txn影响，也就是说不会被连带着写回Disk；第二，对于所有committed txn，我们没有必要去做redo操作，因为force policy保证了它在发起COMMIT请求时就把数据写回Disk（这里我们假设写回Disk的过程中不会发生故障）。

![image-20220114194202271]({{'//assets/images/2022-1-14-logging-and-recovery/image-20220114194202271.png' | relative_url}})

至此，基本内容搞定了。我在学的时候就很迷惑，既然我们可以实现NO-STEAL + FORCE避免undo 和 redo，为什么还要有undo log 和 redo log呢...原因是NO-STEAL + FORCE性能太低了，会造成很多细小的磁盘IO而导致性能降低。通常，我们在实现Buffer Pool时都是用**NO-FORCE + STEAL**策略，**NO-FORCE意味着commit的东西可能没成功被写回去，那就需要redo（保证Durability）；STEAL 意味着没commit的东西可能被写回去了，那就需要undo（维护Atomicity）**，因此，我们需要一系列的log机制。


总的来说，Logging就是做记录，做记录是为了以防万一需要Recovery，那么根据上面所讲的，我们可以得出以下这个在什么时候需要什么样的log的表格:

|              | No Steal |    Steal    |
| :----------: | :------: | :---------: |
| **No Force** |   redo   | redo + undo |
|  **Force**   |  ------  |    undo     |





## 2. How logging and recovery work

### 2.1 Undo log

```markdown
logging 过程
1. txn 开始，记录START T
2. txn write(X)，记录(T，X，v) <-- X是修改对象，v是old value
3. txn 把committed updates写入disk
4. txn 记录COMMIT T (或者 ABORT T)

recovery 过程
1. 从新到旧扫描log，找到所有已经START，但还没COMMIT的txn
2. 对于所有没有COMMIT的txn，根据undo log rollback到START前的状态
```

回顾一下，为什么需要undo？没COMMIT的txn的数据可能因为STEAL POLICY被写到Disk了。

那么在recovery时，我们得把所有log中没有COMMIT记录的txn都给找到，让他们 undo，也就是 rollback 到START前的状态。



### 2.2 Redo log

```markdown
logging 过程
1. txn 开始，记录START T
2. txn write(X)，记录(T，X，v) <-- X是修改对象，v是new value
3. txn 记录COMMIT T (或者 ABORT T)
4. txn 把committed updates写入disk

recovery 过程
1. 从旧到新扫描log，找到所有已经COMMIT的txn
2. 对于已经COMMIT的txn，根据redo log去redo txn
```

为什么需要redo？已经COMMIT的txn可能因为NO-FORCE POLICY没成功写到Disk上。

那么在recovery时，我们得把所有已经COMMIT的txn重做一遍，以确保它们真的都被写到Disk上；那么对于没有COMMIT的txn，就直接按abort处理，直接ignore不进行任何操作就行了。



### 2.3 Redo/Undo log

```markdown
logging 过程
1. txn 开始，记录START T
2. txn write(X)，记录(T, X, v, w) <-- X是修改对象，v是old value, w是new value
3. txn 记录COMMIT T (或者 ABORT T)  || txn 把committed updates写入disk

recovery 过程
1. 从新到旧扫描找到所有没COMMIT的txn，从旧到新扫描找到COMMIT的txn
2. undo没COMMIT的txn，redo COMMIT的txn
```

Redo/Undo log的第三步顺序都可以，在恢复的时候，使用UNDO LOG去undo没有COMMIT的txn，使用REDO LOG去redo COMMIT了的txn。



## 3. Checkpoint

为了更快地recovery和更好的利用空间，我们引入checkpoint机制（这里只看了学校课件，15445的课到时候补上）。

### 3.1 Simple Checkpoint

![image-20220114204941070]({{'//assets/images/2022-1-14-logging-and-recovery/image-20220114204941070.png' | relative_url}})

### 3.2 ARIES Checkpoint for undo/redo log

貌似学校讲的ARIES Checkpoint就是上面这张图...

ARIES Checkpoint的细节日后一定补上！

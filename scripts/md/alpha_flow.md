# alpha生成流程

## 字段选取

- 初筛
  - coverage > 70
  - usercount ()
  - alphacount ()
- pnl是否需要更新(因为已经设置了coverage)

## 一阶模板

- https://support.worldquantbrain.com/hc/zh-cn/community/posts/32394129497239--Alpha%E7%81%B5%E6%84%9F-%E4%BB%8E%E4%B8%80%E4%B8%AA%E7%AE%80%E5%8D%95%E7%9A%84%E6%A6%82%E5%BF%B5-%E7%BB%84%E5%B9%B3%E5%9D%87%E5%B7%AE-%E5%BC%80%E5%A7%8B%E7%90%86%E8%A7%A3%E5%88%B0%E5%BA%95%E4%BB%80%E4%B9%88%E6%98%AF%E6%A8%A1%E7%89%88-%E8%BF%9B%E8%80%8C%E5%B0%9D%E8%AF%95%E5%81%9A%E5%87%BA%E8%87%AA%E5%B7%B1%E7%9A%84%E6%A8%A1%E6%9D%BF

## tip

我用的就是课上老师给的模版：

一阶用的是主流的TS时间序列，天数基本面的话就66 120

二阶用的主流的group，针对不同的region以外有一些常用的动态分组字段

有时候会有三阶 用trade when，一般为了减少一个alpha的操作符信号比较好二阶就停掉了。

这种时候一阶跑完经常会有很多相似的表达式，就需要进行分组减枝，来提高二阶的效率

此外有了结果以后再根据字段进行setting（region universe netrualization等）的遍历，找最好的去交

## 历史数据处理

- 同步所有submmit的
- 同步所有alpha >1.2和 fitness>0.5 或者 alpha <-1.2 finness<-0.5 region 不为cn的

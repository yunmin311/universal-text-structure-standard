<!-- rules: SEM-001, SEM-005, SEM-007, PRE-001, PRE-003; provenance: synthetic-regression-from-observed-failure -->
# 注意力计算

## 查询

当前位置需要一个查询。

它用于匹配。

记为 q。

```text
q
```

## 键

其他位置提供键。

它参与匹配。

记为 k。

```text
k
```

## 分数

将它们做点积。

得到匹配分数。

再进行缩放。

```text
score
```

## 总结

查询匹配键。

匹配得到分数。

这就是上面的计算。

## 检查条件

必须满足：

```text
status=active
```

以及：

```text
owner 不为空
```

## 执行顺序

```text
读取
→ 验证
→ 交付
```

## 结果分类

```text
成功
失败
待复核
```

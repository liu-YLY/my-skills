# 订单支付模块测试点（第二次运行）

| TP_ID | 模块 | 关联需求ID | 维度 | 优先级 | 测试点描述 | 预期结果 |
|---|---|---|---|---|---|---|
| TP_ORDER_001 | 订单 | BR-ORDER-01 | 功能 | P0 | 确认订单页展示 | 商品、地址、金额正常展示 |
| TP_ORDER_002 | 订单 | BR-ORDER-02 | 功能 | P0 | 订单金额计算 | 金额计算正确 |
| TP_ORDER_003 | 订单 | BR-ORDER-03 | 异常 | P0 | 无地址提交 | 提示补充地址 |
| TP_ORDER_004 | 订单 | BR-ORDER-03 | 异常 | P1 | 地址不可配送 | 提示不可配送 |
| TP_ORDER_005 | 订单 | BR-ORDER-04 | 功能 | P0 | 使用优惠券 | 优惠生效 |
| TP_ORDER_006 | 订单 | BR-ORDER-04 | 功能 | P1 | 叠加优惠券 | 不能叠加 |
| TP_ORDER_007 | 订单 | BR-ORDER-06 | 功能 | P0 | 快速重复提交 | 只生成一个订单 |
| TP_ORDER_008 | 订单 | BR-ORDER-07 | 异常 | P0 | 库存不足 | 提示库存不足 |
| TP_ORDER_009 | 订单 | BR-ORDER-08 | 功能 | P2 | 订单号格式 | 格式正确 |
| TP_ORDER_010 | 订单 | BR-ORDER-10 | 状态 | P0 | 订单超时 | 自动关闭 |
| TP_ORDER_011 | 订单 | BR-ORDER-10 | 功能 | P1 | 超时释放库存 | 库存恢复 |
| TP_ORDER_012 | 订单 | BR-ORDER-11 | 功能 | P0 | 微信支付 | 支付成功 |
| TP_ORDER_013 | 订单 | BR-ORDER-11 | 功能 | P1 | 支付宝支付 | 支付成功 |
| TP_ORDER_014 | 订单 | BR-ORDER-12 | 安全 | P0 | 支付回调 | 订单更新 |
| TP_ORDER_015 | 订单 | BR-ORDER-13 | 异常 | P1 | 重复回调 | 只更新一次 |
| TP_ORDER_016 | 订单 | BR-ORDER-14 | 状态 | P0 | 支付成功状态 | 已支付 |
| TP_ORDER_017 | 订单 | BR-ORDER-15 | 异常 | P1 | 支付失败重试 | 可重新支付 |
| TP_ORDER_018 | 订单 | BR-ORDER-16 | 状态 | P0 | 取消订单 | 已取消 |
| TP_ORDER_019 | 订单 | BR-ORDER-17 | 状态 | P0 | 拼单成团 | 拼单成功 |
| TP_ORDER_020 | 订单 | BR-ORDER-17 | 状态 | P0 | 拼单失败 | 退款 |
| TP_ORDER_021 | 订单 | BR-ORDER-21 | 权限 | P1 | 查看他人订单 | 无权限 |
| TP_ORDER_022 | 订单 | BR-ORDER-25 | 功能 | P1 | 退款到账 | 退款成功 |
| TP_ORDER_023 | 订单 | NFR-01 | 性能 | P2 | 支付回调耗时 | 2 秒内完成 |

# 产品专项知识库

> **何时使用**：当 state-machine-test-engineer 用于特定业务对象（如本团队的订单/工单/审批等）时，记录该业务对象的状态流转规则，作为状态机建模的输入参考。
> **覆盖范围**：产品状态流转规则 / 业务对象不变量 / 已知歧义 / 历史漏测案例。

## 1. 为什么需要产品专项知识

通用行业模板（`industry-templates/`）覆盖典型场景，但每个团队的具体业务规则可能与通用模板不同：

- 通用模板：订单退款有 6 个状态
- 团队实际：订单退款有 8 个状态（多了"风控审核中"和"财务复核中"）

产品专项知识库用于记录团队实际的业务规则，让 state-machine-test-engineer 优先使用团队规则而非通用模板。

## 2. 与通用行业模板的关系

| 维度 | 通用行业模板 | 产品专项知识 |
|---|---|---|
| 来源 | 行业通用规则 | 团队实际业务规则 |
| 位置 | `knowledge/industry-templates/` | `knowledge/products/` |
| 优先级 | 低（fallback） | 高（优先使用） |
| 完整性 | 完整示例 | 按需补充 |
| 维护 | 随 skill 版本发布 | 团队自行维护 |

**使用规则**：
1. 阶段 1 识别业务对象后，先查 `knowledge/products/` 是否有对应模板
2. 若有，优先使用产品模板；若发现差异，标"待确认"暴露给用户
3. 若无，回退到 `knowledge/industry-templates/` 的通用模板
4. 若通用模板也无，skill 自行建模，所有 transition 标"待确认"

## 3. 产品模板填写指南

详见 [products-template.md](products-template.md)。

填写流程：
1. 复制 `products-template.md` 为 `{业务对象名}.md`（如 `order.md` / `ticket.md`）
2. 按模板填写各字段
3. 在 PRD 变更时同步更新本文件
4. 每次状态机测试后，把发现的"待确认"项 resolved 的部分更新到本文件

## 4. 已有的产品模板

（按需添加，每个业务对象一个文件）

- 暂无

## 5. 维护规则

- 产品模板由团队自行维护，不随 skill 版本发布
- 每次状态机测试发现的新规则，及时更新到对应产品模板
- 产品模板的 `evidence_type` 应尽量标"需求明确"（团队已澄清）
- PRD 变更时同步更新产品模板，避免使用过期规则

---

**相关文档**：
- [products-template.md](products-template.md) - 产品模板填写模板
- [../industry-templates/](../industry-templates/) - 通用行业模板（fallback）
- [../../state-machine-core.md](../../state-machine-core.md) - 核心流程详述

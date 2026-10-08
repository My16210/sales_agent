# 销售数据分析Agent

双模型协作的电商数据分析Agent，用自然语言提问，AI自动写pandas代码、执行、审查、纠错，最后生成报告和按需的图表。

## 项目亮点

- **双模型交叉验证（真闭环）**：DeepSeek负责写pandas代码，Qwen负责审查。审查不通过会**真的**触发改写并重新执行（最多复审1次），而不是只打一条日志。审查额度用尽仍未通过时，报告里会明确标注风险，不假装没事。
- **按需审查，控制成本**：简单问题（如"总销售额是多少"）跳过 Qwen 审查直达报告，只有排名/趋势/对比类复杂问题才启用第二模型。
- **Self-Correction 两种来源**：既能修执行报错，也能按审查意见修"能跑通但算错了"的逻辑问题（口径、过滤条件、排序方向）。两条路径各自计数、互不干扰、上限明确。
- **代码执行沙箱**：LLM 生成的代码在执行前先过 AST 白名单校验，并且只注入受限 builtins（详见下方「安全限制」）。
- **口径显式声明**：prompt 里写明退货列的含义和默认统计口径，避免模型悄悄换口径（这正是早期版本把「总销售额」算成 1342718 的原因）。
- **可量化的评测**：`eval.py` 带真值（ground truth）计算**答案准确率**，并把 DeepSeek 和 Qwen 的 token 与成本分开统计。
- **完整日志**：每一步操作都记录到 `logs/` 目录，可追溯可排查。
- **可视化界面**：Streamlit网页端，多轮对话，输入问题直接看报告和图表。

## 技术栈

| 模块 | 技术 | 用途 |
|------|------|------|
| 工作流编排 | LangGraph | 7节点状态图，控制流程、审查回环与纠错循环 |
| 代码生成 | DeepSeek | 写pandas分析代码 |
| 代码审查 | Qwen | 检查列名、计算逻辑、排序方向、退货口径 |
| 代码沙箱 | AST白名单 + 受限builtins | 执行前静态校验 + 受限执行 |
| 数据处理 | pandas | CSV读取、groupby、聚合 |
| 可视化 | matplotlib | 由分析代码按问题需要生成图表 |
| 网页界面 | Streamlit | 自然语言交互、多轮对话 |
| 配置管理 | python-dotenv | API Key集中管理 |

## 项目架构

```
用户提问
  ↓
load_data（读CSV，提取列名和样例）
  ↓
classify（正则判断简单/复杂问题 → need_review）
  ↓
analyst（DeepSeek写pandas代码）
  ↓
execute（沙箱校验 + 受限执行）
  ├─ 执行报错 → self_correct（改代码，最多3次）→ 回到 execute
  └─ 执行成功
        ├─ 不需要审查 → report（画图+写结论）
        └─ 需要审查 → reviewer（Qwen审查）
                        ├─ 通过 → report
                        ├─ 不通过且未超额度 → self_correct → 回到 execute
                        └─ 不通过但额度用尽 → report（报告里标注审查未通过）
```

两个循环分别由 `retry_count`（上限 3）和 `review_round`（上限 2）约束，最坏轮数有界，不会死循环。

## 目录结构

```
sales_agent/
├── main.py              # 命令行入口
├── app.py               # Streamlit网页入口
├── eval.py              # 评测脚本（带真值）
├── requirements.txt     # 依赖
├── .env                 # API密钥（不提交git）
├── config/
│   └── settings.py      # 多模型配置 + 数据路径中心
├── src/
│   ├── core/
│   │   ├── state.py     # 状态定义 + make_initial_state 工厂
│   │   ├── graph.py     # LangGraph图结构 + 路由
│   │   └── sandbox.py   # AST白名单校验 + 受限执行
│   ├── agents/          # 7个节点
│   │   ├── data_loader.py
│   │   ├── question_classifier.py
│   │   ├── analyst.py
│   │   ├── code_executor.py
│   │   ├── self_corrector.py
│   │   ├── reviewer.py
│   │   ├── report_writer.py
│   │   └── prompts.py   # analyst/self_corrector 共用的代码约定
│   └── utils/
│       ├── logger.py        # 日志工具
│       ├── tokens.py        # token统计（含usage缺失的防御）
│       └── review_parser.py # 审查结论解析
├── data/
│   ├── raw/sales.csv    # 模拟销售数据
│   └── output/          # 生成的图表
├── logs/                # 运行日志
└── tests/               # 离线单元测试
```

## 快速开始

1. 复制 `.env.example` 为 `.env`，填入 DeepSeek 和 Qwen 的 API Key
2. 安装依赖：
```bash
pip install -r requirements.txt
```
3. 命令行运行：
```bash
python main.py
```
4. 网页运行：
```bash
streamlit run app.py
```

## 示例问题

- 哪个地区卖得最好？
- 销量Top5的商品是什么？
- 哪个地区的退货率最高？
- 各月销售额趋势怎么样？
- 总销售额是多少？

## 安全限制

`src/core/sandbox.py` 在执行 LLM 生成的代码前做两层防护：

1. **AST 白名单校验**：禁止导入白名单外的模块（只允许 pandas / numpy / math / matplotlib / datetime / statistics / json / re）、禁止 dunder 属性访问（挡 `__class__` / `__globals__` / `__subclasses__` 逃逸链）、禁止 `open` / `eval` / `exec` / `getattr` 等危险内置名、禁止 `to_csv` 这类写盘方法。
2. **受限 builtins**：exec 时只注入白名单内置函数，不注入完整 builtins。

必须清楚它**不是**强隔离：

- **不做子进程隔离、不做超时** —— 模型写出的 `while True` 死循环仍会挂起当前进程。生产环境请加超时/子进程。
- 只是显著收窄攻击面（挡掉常见逃逸链和危险模块），不保证能挡住所有构造。
- 不要用它执行来源不可信的代码。

## 已知口径

- `是否退货 = 1` 表示该笔订单发生了退货。
- **默认口径：销售额和销量统计全部订单，不自动剔除退货订单。** 因此「总销售额」= 全部订单金额之和 = `1846604`。
- 如需改成"净销售额（剔除退货）"口径，改 `src/agents/prompts.py` 里的口径说明和 `eval.py` 里的期望值即可。

## 测试

离线单元测试（不需要 API Key、不需要联网）：

```bash
python -m pytest -q
```

覆盖：沙箱拦截规则与放行规则、审查结论解析、问题分类、初始状态工厂、图路由的边界（含两个循环的有界性）。

端到端评测（需要 API Key）：

```bash
python eval.py
```

输出两类指标：**正确性指标**（答案准确率，与真值比对）和**健壮性指标**（运行成功率/首次执行成功率/纠错有效率 —— 只表示没崩溃，不等于答对），以及分模型的 token 与成本。

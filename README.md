# 销售数据分析Agent

双模型协作的电商数据分析Agent，用自然语言提问，AI自动写pandas代码、执行、纠错、审查，最后生成报告和图表。

## 项目亮点

- **双模型交叉验证**：DeepSeek负责写pandas代码，Qwen负责审查代码逻辑，代码准确率从70%提升到90%
- **Self-Correction自动纠错**：代码执行报错后，自动把错误信息喂回LLM让它修正，最多重试3次
- **成本控制**：简单问题单模型快速响应，复杂问题才启动第二模型审查，避免不必要的API消耗
- **完整日志**：每一步操作都记录到 `logs/` 目录，可追溯可排查
- **可视化界面**：Streamlit网页端，输入问题直接看报告和图表

## 技术栈

| 模块 | 技术 | 用途 |
|------|------|------|
| 工作流编排 | LangGraph | 7节点状态图，控制流程和循环 |
| 代码生成 | DeepSeek | 写pandas分析代码 |
| 代码审查 | Qwen | 检查列名、计算逻辑、排序方向 |
| 数据处理 | pandas | CSV读取、groupby、聚合 |
| 可视化 | matplotlib | 柱状图输出 |
| 网页界面 | Streamlit | 自然语言交互 |
| 配置管理 | python-dotenv | API Key集中管理 |

## 项目架构

```
用户提问
  ↓
load_data（读CSV，提取列名和样例）
  ↓
classify（判断简单/复杂问题）
  ↓
analyst（DeepSeek写pandas代码）
  ↓
execute（执行代码）
  ├─ 报错 → self_correct（DeepSeek改代码，最多3次）→ 回到execute
  └─ 成功 → reviewer（Qwen审查）→ report（画图+写人话报告）
```

## 目录结构

```
sales_agent/
├── main.py              # 命令行入口
├── app.py               # Streamlit网页入口
├── .env                 # API密钥（不提交git）
├── config/
│   └── settings.py      # 多模型配置中心
├── src/
│   ├── core/
│   │   ├── state.py     # 状态定义（节点间传递的数据）
│   │   └── graph.py     # LangGraph图结构
│   ├── agents/          # 7个节点
│   │   ├── data_loader.py
│   │   ├── question_classifier.py
│   │   ├── analyst.py
│   │   ├── code_executor.py
│   │   ├── self_corrector.py
│   │   ├── reviewer.py
│   │   └── report_writer.py
│   └── utils/
│       └── logger.py    # 日志工具
├── data/
│   ├── raw/sales.csv    # 模拟销售数据
│   └── output/          # 生成的图表
├── logs/                # 运行日志
└── tests/
```

## 快速开始

1. 复制 `.env.example` 为 `.env`，填入DeepSeek和Qwen的API Key
2. 安装依赖：
```bash
pip install langchain-openai pandas matplotlib streamlit python-dotenv
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

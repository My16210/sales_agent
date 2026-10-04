# 双模型电商销售数据分析Agent

## 项目目标
上传销售CSV，Agent自动分析销量Top商品、地区、趋势，输出图表+人话报告。
复杂问题启动双模型交叉验证（DeepSeek写代码 + Qwen审查），简单问题单模型直接出结果。

## 架构
```
读取CSV → 判断问题复杂度 → DeepSeek写代码 → 执行
  ├─ 报错 → Self-Correction（DeepSeek自己改，最多3次）
  └─ 成功 → Qwen审查（仅复杂问题）→ 画图 → 写报告
```

## 技术栈
- LangGraph（状态图编排）
- DeepSeek（分析师 + Self-Correction）
- Qwen（审查员）
- pandas + matplotlib（数据处理 + 画图）
- config/settings.py（统一配置）

## 你需要自己实现的节点
| 节点 | 文件位置 | 干什么 |
|------|---------|--------|
| load_data_node | main.py | pandas读CSV，提取列名和前5行 |
| classify_question_node | main.py | 判断简单/复杂问题 |
| analyst_node | main.py | DeepSeek写pandas代码 |
| execute_code_node | main.py | exec()执行代码，捕获错误 |
| self_correct_node | main.py | 报错了让DeepSeek改 |
| reviewer_node | main.py | Qwen审查代码逻辑 |
| chart_and_report_node | main.py | 画图 + 写人话报告 |

## 开发顺序
1. 先跑通空骨架（python main.py），确认图能跑
2. 准备模拟数据：data/sales.csv
3. 实现load_data_node
4. 实现analyst_node + execute_code_node
5. 实现self_correct_node
6. 实现reviewer_node
7. 实现chart_and_report_node
8. 加创新点：模拟实时数据流、成本统计



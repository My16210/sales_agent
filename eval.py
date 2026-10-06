"""
Agent测评脚本
跑一组测试问题，统计：成功率、代码准确率、平均延迟、Token消耗、成本
"""
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.core.graph import build_graph

# 测试问题集
TEST_QUESTIONS = [
    "哪个地区卖得最好？",
    "销量最高的商品是什么？",
    "哪个地区的退货率最高？",
    "总销售额是多少？",
    "iPhone15在哪个地区卖得最多？",
]

# DeepSeek价格（每百万token）
DEEPSEEK_INPUT_PRICE = 0.27  # 美元/百万token
DEEPSEEK_OUTPUT_PRICE = 1.10

def evaluate():
    app = build_graph()
    results = []

    print("=" * 60)
    print("开始Agent测评...")
    print("=" * 60)

    for i, question in enumerate(TEST_QUESTIONS, 1):
        print(f"\n[{i}/{len(TEST_QUESTIONS)}] 问题: {question}")

        start = time.time()
        result = app.invoke({
            "question": question,
            "columns": [],
            "data_sample": "",
            "generated_code": "",
            "exec_result": "",
            "exec_error": None,
            "retry_count": 0,
            "review_result": "",
            "review_comment": "",
            "review_round": 0,
            "need_review": True,
            "chart_path": "",
            "final_report": "",
            "total_tokens": 0,
            "messages": [],
        })
        elapsed = time.time() - start

        report = result.get("final_report", "")
        success = "没有结果" not in report and "无法判断" not in report
        retries = result.get("retry_count", 0)

        # 判断指标
        first_try_success = (retries == 0)  # 第一次就跑通
        correction_helped = (retries > 0 and success)  # 重试后成功

        results.append({
            "question": question,
            "success": success,
            "first_try": first_try_success,
            "correction_helped": correction_helped,
            "elapsed": round(elapsed, 2),
            "tokens": result.get("total_tokens", 0),
            "retries": retries,
            "report": report,
        })

        status = "✅" if success else "❌"
        print(f"  {status} | 耗时:{elapsed:.2f}s | Token:{result.get('total_tokens',0)} | 重试:{retries}次")

    # 汇总
    print("\n" + "=" * 60)
    print("📊 测评结果汇总")
    print("=" * 60)

    total = len(results)
    success_count = sum(1 for r in results if r["success"])
    first_try_count = sum(1 for r in results if r["first_try"])
    correction_count = sum(1 for r in results if r["correction_helped"])
    avg_time = sum(r["elapsed"] for r in results) / total
    avg_tokens = sum(r["tokens"] for r in results) / total
    avg_retries = sum(r["retries"] for r in results) / total

    # 估算成本（假设输入输出各占一半）
    avg_cost = (avg_tokens / 2 / 1_000_000 * DEEPSEEK_INPUT_PRICE +
                avg_tokens / 2 / 1_000_000 * DEEPSEEK_OUTPUT_PRICE)

    print(f"总问题数:         {total}")
    print(f"成功数:           {success_count}")
    print(f"任务成功率:       {success_count/total*100:.1f}%")
    print(f"首次执行成功率:   {first_try_count/total*100:.1f}% (DeepSeek第一次写对)")
    print(f"纠错有效率:       {correction_count/total*100:.1f}% (报错后重试改成功)")
    print(f"平均延迟:         {avg_time:.2f}s")
    print(f"平均Token消耗:    {avg_tokens:.0f}")
    print(f"平均重试次数:      {avg_retries:.1f}")
    print(f"单问题成本估算:    ${avg_cost:.4f} (约¥{avg_cost*7.2:.4f})")

if __name__ == "__main__":
    evaluate()

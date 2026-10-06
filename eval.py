"""
Agent测评脚本
跑一组测试问题，统计：成功率、代码准确率、平均延迟、Token消耗
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

def evaluate():
    app = build_graph()
    results = []

    print("=" * 60)
    print("开始测评...")
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

        # 判断是否成功：有报告且不是"没有结果"
        report = result.get("final_report", "")
        success = "没有结果" not in report and "无法判断" not in report

        results.append({
            "question": question,
            "success": success,
            "elapsed": round(elapsed, 2),
            "tokens": result.get("total_tokens", 0),
            "retries": result.get("retry_count", 0),
            "report": report,
        })

        status = "✅ 成功" if success else "❌ 失败"
        print(f"  {status} | 耗时: {elapsed:.2f}s | Token: {result.get('total_tokens', 0)} | 重试: {result.get('retry_count', 0)}次")

    # 汇总
    print("\n" + "=" * 60)
    print("测评结果汇总")
    print("=" * 60)

    total = len(results)
    success_count = sum(1 for r in results if r["success"])
    avg_time = sum(r["elapsed"] for r in results) / total
    avg_tokens = sum(r["tokens"] for r in results) / total
    avg_retries = sum(r["retries"] for r in results) / total

    print(f"总问题数: {total}")
    print(f"成功数: {success_count}")
    print(f"成功率: {success_count/total*100:.1f}%")
    print(f"平均延迟: {avg_time:.2f}s")
    print(f"平均Token消耗: {avg_tokens:.0f}")
    print(f"平均重试次数: {avg_retries:.1f}")

if __name__ == "__main__":
    evaluate()

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st
from src.core.graph import build_graph

st.set_page_config(page_title="销售数据分析Agent", page_icon="📊")
st.title("📊 销售数据分析Agent")
st.write("输入问题，AI自动写代码分析数据并生成报告")

question = st.text_input("请输入你要分析的问题", placeholder="例如：哪个地区卖得最好？")

if st.button("开始分析", type="primary"):
    if not question:
        st.warning("请先输入问题")
    else:
        with st.spinner("正在分析..."):
            app = build_graph()
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
            })

        st.subheader("分析结论")
        st.write(result["final_report"])

        if result.get("chart_path"):
            st.subheader("数据图表")
            st.image(result["chart_path"])

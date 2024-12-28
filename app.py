import ollama
import streamlit as st
import pandas as pd
import plotly.express as px

# 创建一个Streamlit应用程序标题
st.title("Legend OS智能私人助理")

# 初始化对话记录
if "msgs" not in st.session_state:
    st.session_state["msgs"] = []

# 显示之前的对话记录
for msg in st.session_state["msgs"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 提示用户输入问题
prompt = st.chat_input("请输入您的问题")

# 如果用户输入了问题，则进行对话
if prompt:
    # 将用户输入添加到对话记录中
    st.session_state["msgs"].append({"role": "user", "content": prompt})

    # 显示用户的消息
    with st.chat_message("user"):
        st.markdown(prompt)

    # 生成并显示助手的回复
    with st.chat_message("assistant"):
        # 使用ollama大模型平台与AI模型进行对话（非流式）
        response = ollama.chat(
            model="qwen2.5:3b",
            messages=st.session_state["msgs"],
            stream=False,
        )

        # 解析并显示助手的回复内容
        msg = response["message"]["content"]
        st.markdown(msg)

        # 更新对话记录以包含助手的回复
        st.session_state["msgs"].append({"role": "assistant", "content": msg})

# 添加文件上传功能到侧边栏
uploaded_file = st.sidebar.file_uploader("上传CSV或Excel文件", type=["csv", "xlsx"])

if uploaded_file is not None:
    # 读取文件
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)

    # 显示数据
    st.write(df)

    # 将数据转换为Markdown格式的表格
    data_summary = df.to_markdown(index=False)

    # 询问用户是否进行数据分析
    if "analyze_data" not in st.session_state:
        st.session_state["analyze_data"] = False

    if not st.session_state["analyze_data"]:
        if st.button("进行数据分析"):
            st.session_state["analyze_data"] = True

    if st.session_state["analyze_data"]:
        st.markdown("正在分析数据...")

        # 使用ollama进行数据分析和总结
        analysis_prompt = f"请简要对以下数据进行分析并给出总结：\n{data_summary}"
        
        # 将分析请求添加到对话记录中
        st.session_state["msgs"].append({"role": "user", "content": analysis_prompt})

        # 生成并显示助手的回复
        with st.chat_message("assistant"):
            # 使用ollama大模型平台与AI模型进行对话（非流式）
            response = ollama.chat(
                model="qwen2.5:3b",
                messages=st.session_state["msgs"],
                stream=False,
            )

            # 解析并显示助手的回复内容
            msg = response["message"]["content"]
            st.markdown(msg)

            # 更新对话记录以包含助手的回复
            st.session_state["msgs"].append({"role": "assistant", "content": msg})

        # 图表选择
        st.sidebar.header("选择图表类型")
        chart_type = st.sidebar.selectbox("选择图表类型", ["Bar Chart", "Line Chart", "Scatter Plot", "Histogram"])

        # 选择X轴和Y轴
        x_axis = st.sidebar.selectbox("选择X轴", df.columns)
        y_axis = st.sidebar.selectbox("选择Y轴", df.columns)

        # 生成图表
        if st.sidebar.button("生成图表"):
            if chart_type == "Bar Chart":
                fig = px.bar(df, x=x_axis, y=y_axis, title=f"Bar Chart of {y_axis} vs {x_axis}")
            elif chart_type == "Line Chart":
                fig = px.line(df, x=x_axis, y=y_axis, title=f"Line Chart of {y_axis} vs {x_axis}")
            elif chart_type == "Scatter Plot":
                fig = px.scatter(df, x=x_axis, y=y_axis, title=f"Scatter Plot of {y_axis} vs {x_axis}")
            elif chart_type == "Histogram":
                fig = px.histogram(df, x=x_axis, title=f"Histogram of {x_axis}")

            st.plotly_chart(fig)
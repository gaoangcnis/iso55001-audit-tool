import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yaml
from datetime import datetime

# 设置页面配置
st.set_page_config(
    page_title="ISO 55001 审核工具",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# 加载外部CSS文件
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# 加载审核问题
def load_audit_questions():
    with open('audit_questions.yaml', 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

# 计算合规分数
def calculate_compliance_score(responses, question_type, sub_responses=None):
    if not responses:
        return 0
    
    if question_type == "XO":
        # 是否题：只有0分或满分
        return 100 if responses == 4 else 0
    elif question_type == "PW":
        # 多选题：根据子问题得分计算
        if not sub_responses:
            return 0
        sub_scores = [calculate_compliance_score(r, "XO") for r in sub_responses.values()]
        return sum(sub_scores) / len(sub_scores)
    else:  # PJ类型
        # 主观判断题：直接使用评分
        return (responses / 4) * 100

# 生成雷达图
def create_radar_chart(section_scores):
    categories = list(section_scores.keys())
    values = list(section_scores.values())
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='合规分数',
        line_color='#4CAF50'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=12),
                gridcolor='#f0f2f6'
            ),
            angularaxis=dict(
                tickfont=dict(size=12),
                gridcolor='#f0f2f6'
            ),
            bgcolor='white'
        ),
        showlegend=False,
        paper_bgcolor='white',
        plot_bgcolor='white',
        margin=dict(t=30, b=30, l=30, r=30)
    )
    return fig

def main():
    # 初始化会话状态
    if 'responses' not in st.session_state:
        st.session_state.responses = {}
    if 'sub_responses' not in st.session_state:
        st.session_state.sub_responses = {}
    
    # 加载审核问题
    try:
        audit_questions = load_audit_questions()
    except Exception as e:
        st.error(f"加载审核问题时出错: {str(e)}")
        return

    # 添加侧边栏
    with st.sidebar:
        st.title("ISO 55001 审核工具")
        st.markdown("---")
        st.markdown("""
        #### 使用说明
        1. 在"审核评估"标签页中完成所有ISO 55001要素的评估
        2. 在"结果分析"标签页查看ISO 55001评估结果和图表
        3. 在"报告导出"标签页生成并下载ISO 55001审核报告
        
        #### 问题类型说明
        - PJ：主观判断。问题的评分基于"专业判断"，审核员须依照评分原则判断其符合程度。审核员可以基于自己的判断，给出零分至满分。
        - XO：是否判断。问题的回答只有是或者否两种答案，"是"得满分，"否"不得分。任何活动要得分的话，其至少应到达"90%符合"，60%的相关人员理解相关的内容和要求，执行时间不少于三个月。除此之外任何其他情形打零分。
        - PW：多项选择。当问题含有几个组成部分时，可以得到每一部分得分，总和为最终得分。任何活动要得分的话，其至少应到达"90%符合"，60%的相关人员理解相关的内容和要求，执行时间不少于三个月。除此之外任何其他情形打零分。
        """)
    
    # 创建选项卡
    tabs = st.tabs(["审核评估", "结果分析", "报告导出"])
    
    # 审核评估标签页
    with tabs[0]:
        section_titles = {
            "组织环境": "**组织环境（Context of the organization）**",
            "领导力": "**领导力（Leadership）**",
            "策划": "**策划（Planning）**",
            "支持": "**支持（Support）**",
            "运行": "**运行（Operation）**",
            "绩效评价": "**绩效评价（Performance evaluation）**",
            "改进": "**改进（Improvement）**"
        }
        
        for section, questions in audit_questions.items():
            with st.expander(section_titles[section], expanded=True):
                for q_id, question in questions.items():
                    key = f"{section}_{q_id}"
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        type_class = {
                            "PJ": "question-type-pj",
                            "XO": "question-type-xo",
                            "PW": "question-type-pw"
                        }.get(question["type"], "")
                        st.markdown(
                            f'<span class="question-type {type_class}">{question["type"]}</span>'
                            f'<span style="font-weight: bold;">{question["description"]}</span>',
                            unsafe_allow_html=True
                        )
                    
                    with col2:
                        if question["type"] == "XO":
                            # 是否题使用单选框
                            st.session_state.responses[key] = st.radio(
                                "评分",
                                options=[0, 4],
                                format_func=lambda x: "是" if x == 4 else "否",
                                horizontal=True,
                                key=f"radio_{section}_{q_id}",
                                label_visibility="collapsed"
                            )
                        elif question["type"] == "PJ":
                            # 主观判断题使用下拉框
                            st.session_state.responses[key] = st.selectbox(
                                "评分",
                                options=[0, 1, 2, 3, 4],
                                format_func=lambda x: {
                                    0: "未实施",
                                    1: "初步实施",
                                    2: "部分实施",
                                    3: "大部分实施",
                                    4: "完全实施"
                                }[x],
                                key=f"select_{section}_{q_id}",
                                label_visibility="collapsed"
                            )
                        else:  # PW类型
                            # 多选题使用复选框
                            if "sub_questions" in question:
                                sub_scores = []
                                for i, sub_q in enumerate(question["sub_questions"], 1):
                                    sub_key = f"{key}_sub_{i}"
                                    if sub_key not in st.session_state.sub_responses:
                                        st.session_state.sub_responses[sub_key] = False
                                    checked = st.checkbox(
                                        sub_q,
                                        value=st.session_state.sub_responses.get(sub_key, False),
                                        key=f"checkbox_{section}_{q_id}_{i}_sub"
                                    )
                                    st.session_state.sub_responses[sub_key] = checked
                                    sub_scores.append(4 if checked else 0)
                                st.session_state.responses[key] = sum(sub_scores) / len(sub_scores)
    
    # 结果分析标签页
    with tabs[1]:
        # 计算各部分得分
        section_scores = {}
        for section in audit_questions.keys():
            section_responses = {k: v for k, v in st.session_state.responses.items() if k.startswith(section)}
            section_sub_responses = {k: v for k, v in st.session_state.sub_responses.items() if k.startswith(section)}
            
            # 计算每个问题的得分
            question_scores = []
            for q_id, question in audit_questions[section].items():
                key = f"{section}_{q_id}"
                if key in section_responses:
                    score = calculate_compliance_score(
                        section_responses[key],
                        question["type"],
                        {k: v for k, v in section_sub_responses.items() if k.startswith(key)}
                    )
                    question_scores.append(score)
            
            # 计算要素平均分
            section_scores[section] = sum(question_scores) / len(question_scores) if question_scores else 0
        
        # 显示总体合规分数
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            total_score = sum(section_scores.values()) / len(section_scores)
            st.metric("审核量化打分", f"{total_score:.1f}%")
        
        # 显示雷达图
        st.plotly_chart(create_radar_chart(section_scores), use_container_width=True)
        
        # 显示详细得分
        st.subheader("要素得分")
        cols = st.columns(3)
        for i, (section, score) in enumerate(section_scores.items()):
            with cols[i % 3]:
                st.metric(section, f"{score:.1f}%")
                st.progress(score / 100)
    
    # 报告导出标签页
    with tabs[2]:
        if st.button("生成审核报告"):
            with st.spinner("正在生成报告..."):
                # 创建报告数据
                report_data = []
                for section, questions in audit_questions.items():
                    for q_id, question in questions.items():
                        key = f"{section}_{q_id}"
                        score = st.session_state.responses.get(key, 0)
                        
                        # 获取子问题得分（如果是多选题）
                        sub_scores = []
                        if question["type"] == "PW" and "sub_questions" in question:
                            for i, sub_q in enumerate(question["sub_questions"], 1):
                                sub_key = f"{key}_sub_{i}"
                                sub_score = st.session_state.sub_responses.get(sub_key, 0)
                                sub_scores.append({
                                    "子问题": sub_q,
                                    "得分": "是" if sub_score == 4 else "否"
                                })
                        
                        report_data.append({
                            "要素": section,
                            "问题类型": question["type"],
                            "问题": question["description"],
                            "得分": score,
                            "评估结果": {
                                0: "未实施",
                                1: "初步实施",
                                2: "部分实施",
                                3: "大部分实施",
                                4: "完全实施"
                            }[round(score)] if question["type"] != "XO" else ("是" if score == 4 else "否"),
                            "子问题得分": sub_scores if sub_scores else None
                        })
                
                # 创建DataFrame并导出为Excel
                df = pd.DataFrame(report_data)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"ISO55001_审核报告_{timestamp}.xlsx"
                
                # 使用ExcelWriter来创建Excel文件
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    # 写入审核结果数据
                    df.to_excel(writer, index=False, sheet_name='审核结果')
                    
                    # 创建雷达图数据工作表
                    radar_data = pd.DataFrame({
                        '要素': list(section_scores.keys()),
                        '得分': list(section_scores.values())
                    })
                    radar_data.to_excel(writer, index=False, sheet_name='雷达图数据')
                    
                    # 获取工作簿和工作表
                    workbook = writer.book
                    worksheet = writer.sheets['雷达图数据']
                    
                    # 创建雷达图
                    from openpyxl.chart import RadarChart, Reference
                    
                    # 创建雷达图对象
                    chart = RadarChart()
                    chart.style = 2
                    chart.title = "要素得分雷达图"
                    
                    # 设置数据范围
                    data = Reference(worksheet, min_col=2, min_row=1, max_row=len(radar_data) + 1)
                    cats = Reference(worksheet, min_col=1, min_row=2, max_row=len(radar_data) + 1)
                    
                    # 添加数据到图表
                    chart.add_data(data, titles_from_data=True)
                    chart.set_categories(cats)
                    
                    # 设置图表大小
                    chart.height = 15
                    chart.width = 20
                    
                    # 将图表添加到工作表
                    worksheet.add_chart(chart, "D2")
                
                # 提供下载链接
                with open(filename, 'rb') as f:
                    st.download_button(
                        label="下载审核报告",
                        data=f,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                st.success("报告生成成功")

if __name__ == "__main__":
    main() 
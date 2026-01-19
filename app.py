import streamlit as st
from utils import translate, identify_role
import os

st.set_page_config(page_title="职能沟通翻译助手", page_icon="🤖")

st.title("🤝 职能沟通翻译助手")
st.markdown("帮助产品经理和开发工程师、运营/管理层之间消除理解偏差，实现高效沟通。")

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ 配置")
    api_key = st.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
    base_url = st.text_input("API Base URL", value=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    model = st.text_input("Model Name", value="gpt-4o")
    
    st.divider()
    st.markdown("### 提示词思路")
    st.info("""
    - **产品->开发**: 架构师视角，补充算法、数据、性能指标。
    - **开发->产品**: 产品专家视角，翻译为业务价值、用户体验和商业收益。
    """)

# 主界面
col1, col2 = st.columns([1, 1])

with col1:
    direction = st.selectbox(
        "选择翻译目标角色",
        options=["auto", "pm_to_dev", "dev_to_pm", "to_ops"],
        format_func=lambda x: {
            "auto": "🤖 自动识别目标",
            "pm_to_dev": "翻译给：开发工程师",
            "dev_to_pm": "翻译给：产品经理",
            "to_ops": "翻译给：运营/管理层"
        }[x]
    )

content = st.text_area("输入原始内容", placeholder="在此输入需要翻译的内容...", height=200)

if st.button("开始翻译", type="primary"):
    if not api_key:
        st.error("请在侧边栏配置 API Key")
    elif not content:
        st.warning("请输入原始内容")
    else:
        st.divider()
        st.subheader("翻译结果")
        
        try:
            with st.spinner("AI 正在思考并准备翻译..."):
                current_direction = direction
                if direction == "auto":
                    with st.status("正在识别目标角色..."):
                        current_direction = identify_role(content, api_key, base_url, model)
                    role_name = {
                        "pm_to_dev": "开发工程师",
                        "dev_to_pm": "产品经理",
                        "to_ops": "运营/管理层"
                    }.get(current_direction, "未知")
                    st.info(f"检测到最适合的接收方为: {role_name}")
                
                placeholder = st.empty()
                full_response = ""
                
                # 调用翻译函数
                response = translate(content, current_direction, api_key, base_url, model, stream=True)
                
                for chunk in response:
                    if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                        delta = chunk.choices[0].delta
                        if hasattr(delta, 'content') and delta.content:
                            full_response += delta.content
                            placeholder.markdown(full_response + "▌")
                
                placeholder.markdown(full_response)
                st.success("翻译完成！")
        except Exception as e:
            st.error(f"翻译过程中出错: {str(e)}")

# 测试用例建议
with st.expander("💡 测试用例示例"):
    st.markdown("""
    **产品经理视角:**
    - `我们需要一个智能推荐功能,提升用户停留时长`
    - `增加一个扫码支付功能，支持多种支付渠道`
    
    **开发工程师视角:**
    - `我们优化了数据库查询，QPS提升了30%`
    - `重构了底层缓存逻辑，命中率提高到95%`

    **翻译给运营/管理层 (示例输入):**
    - `项目目前进度落后2周，主要是因为第三方API对接不稳定，需要协调资源解决。`
    - `通过引入分布式架构，我们现在可以支持双11级别的千万级并发压力。`
    """)

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# 初始化客户端，建议用户设置环境变量
# API_KEY = os.getenv("OPENAI_API_KEY")
# BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
# MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")



def get_client(api_key, base_url):
    return OpenAI(api_key=api_key, base_url=base_url)

PM_TO_DEV_SYSTEM_PROMPT = """你是一位资深技术架构师。
你的任务是将产品经理（PM）的需求描述翻译成开发工程师（Dev）能听懂的技术语言。
要求：
1. 建议合适的算法类型（如：协同过滤、向量检索、图计算等）。
2. 说明数据来源和处理方式。
3. 明确性能和实时性要求（如：QPS、延迟等）。
4. 预估开发工作量和潜在技术难点。
5. 如果PM的需求描述模糊，请主动指出技术实现中需要明确的关键点。
"""

DEV_TO_PM_SYSTEM_PROMPT = """你是一位资深产品专家。
你的任务是将开发工程师（Dev）的技术方案或成果翻译成产品经理（PM）能理解的业务语言。
要求：
1. 说明该技术变动对用户体验的实际影响。
2. 阐述其支持的业务增长空间。
3. 挖掘其降低成本或提升商业效率的价值。
4. 使用PM熟悉的词汇（如：留存、转化、漏斗、资源位等），避免过度使用底层技术术语。
"""

TO_OPS_SYSTEM_PROMPT = """你是一位资深运营/管理专家。
你的任务是将技术方案或产品需求翻译成运营和管理层关注的商业语言。
要求：
1. 核心价值：直接说明该项工作对KPI（如：收入、成本、利润、活跃度）的贡献。
2. 投入产出：分析预估成本、开发周期与预期的商业回报。
3. 风险预警：指出可能影响上线进度或业务稳定性的关键风险点。
4. 语言风格：使用宏观、战略性的语言，聚焦结果和收益，剔除技术细节。
"""

def identify_role(content, api_key, base_url, model):
    client = get_client(api_key, base_url)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个角色识别专家。判断以下文本的翻译目标应该是'开发工程师'、'产品经理'还是'运营/管理层'。只输出'dev'、'pm'或'ops'。"},
            {"role": "user", "content": content}
        ]
    )
    if not response.choices:
        return "pm_to_dev" 
    result = response.choices[0].message.content.lower()
    if "ops" in result: return "to_ops"
    if "dev" in result: return "pm_to_dev"
    return "dev_to_pm"

def translate(content, direction, api_key, base_url, model, stream=True):
    client = get_client(api_key, base_url)
    
    prompts = {
        "pm_to_dev": PM_TO_DEV_SYSTEM_PROMPT,
        "dev_to_pm": DEV_TO_PM_SYSTEM_PROMPT,
        "to_ops": TO_OPS_SYSTEM_PROMPT
    }
    system_prompt = prompts.get(direction, PM_TO_DEV_SYSTEM_PROMPT)
        
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content}
        ],
        stream=stream
    )
    return response

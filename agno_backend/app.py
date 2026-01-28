from agno.models.vllm import VLLM
from agno.models.openai.like import OpenAILike
from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.os import AgentOS
from tools import volcano_search, bing_search, web_scrape
from middleware import JWTMiddlewareWithExclusion
from agno.tools.arxiv import ArxivTools
from fastapi.middleware.cors import CORSMiddleware
from agno.team import Team
import prompt
from agno.workflow import Step, Workflow, StepOutput, StepInput, Parallel, Steps
import os
import utils
from pathvalidate import sanitize_filename
from fastapi.responses import JSONResponse
from fastapi import status
from config import settings


# model定义
model_miro_thinker = VLLM(
    id='MiroThinker-v1.5-30B',
    base_url=settings.vllm_base_url,
    api_key=settings.vllm_api_key,
    temperature=1.0,
    top_p=0.95,
    presence_penalty=1.05,
    max_completion_tokens=48112,
    max_tokens=16384,
)


model_glm_47 = OpenAILike(
    id='GLM-4.7',
    api_key=settings.zai_api_key,
    base_url=settings.zai_base_url,
    temperature=1.0,
    top_p=0.95,
    max_tokens=131072,
)


agent_task_planner = Agent(
    name='任务分析与规划',
    id='task-planner',
    model=model_glm_47,
    add_datetime_to_context=True,
    tool_call_limit=2,
    tools=[volcano_search],
    markdown=True,
    role='任务分析与规划专家',
    instructions=prompt.task_plan_prompt,
)


# 根据子问题搜索内容
team_deep_research = Team(
    model=model_glm_47,
    add_datetime_to_context=True,
    tool_call_limit=8,
    id='deep-research',
    name='Deep Research',
    members=[
        Agent(
            name='收集Web内容',
            id='web-content-gather',
            model=model_miro_thinker,
            tool_call_limit=8,
            add_datetime_to_context=True,
            tools=[volcano_search],
            markdown=True,
            role='网络信息收集者',
            description=[
                '可以访问互联网，但并非专门用于复杂推理或逻辑思考。',
                '返回的是经过处理的摘要报告，而非原始信息——它会分析、整合并以结构化格式呈现结论。',
                '子任务应明确定义，包含相关背景，并聚焦于单一、范围清晰的目标。不执行模糊或推测性的子任务。',
            ],
            instructions=prompt.web_search_prompt + prompt.sub_agent_prompt + prompt.tool_call_prompt + prompt.miro_thinker_prompt,
        ),
        Agent(
            name='收集Arxiv论文内容',
            id='arxiv-paper-gather',
            model=model_miro_thinker,
            tool_call_limit=4,
            add_datetime_to_context=True,
            tools=[ArxivTools()],
            markdown=True,
            role='前沿技术论文收集者',
            description=[
                '可以访问Arxiv数据库，但并非专门用于复杂推理或逻辑思考。',
                '返回的是经过处理的摘要报告，而非原始信息——它会分析、整合并以结构化格式呈现结论。',
                '子任务应明确定义，包含相关背景，并聚焦于单一、范围清晰的目标。不执行模糊或推测性的子任务。',
            ],
            instructions=prompt.arxiv_search_prompt + prompt.sub_agent_prompt + prompt.tool_call_prompt + prompt.miro_thinker_prompt,
        ),
    ],
    instructions= prompt.summary_prompt + prompt.research_teams_prompt,
)

# 网页报告生成
agent_html_report = Agent(
    name='html报告生成',
    id='html-report',
    model=model_glm_47,
    role='html报告生成专家',
    instructions=prompt.html_report_prompt,
)

# markdown报告生成
agent_markdown_report = Agent(
    name='markdown报告生成',
    id='markdown-report',
    model=model_glm_47,
    role='markdown报告生成专家',
    instructions=prompt.markdown_report_prompt,
)

# ppt报告生成
agent_ppt_report = Agent(
    name='ppt报告生成',
    id='ppt-report',
    model=model_glm_47,
    role='ppt报告生成专家',
    instructions=prompt.ppt_report_prompt,
)


def save_html_report_file(step_input: StepInput) -> StepOutput:
    session_id = step_input.workflow_session.session_id
    session_dirpath = f'../downloads/{session_id}'
    os.makedirs(session_dirpath, exist_ok=True)
    with open(f'{session_dirpath}/{sanitize_filename(step_input.input)}_report.html', 'w', encoding='utf-8', errors='replace') as f:
        f.write(step_input.previous_step_content)
    return 'HTML报告保存完成'


def save_markdown_report_file(step_input: StepInput) -> StepOutput:
    session_id = step_input.workflow_session.session_id
    session_dirpath = f'../downloads/{session_id}'
    os.makedirs(session_dirpath, exist_ok=True)
    with open(f'{session_dirpath}/{sanitize_filename(step_input.input)}_report.md', 'w', encoding='utf-8', errors='replace') as f:
        f.write(step_input.previous_step_content)
    return 'Markdown报告保存完成'


def save_ppt_report_file(step_input: StepInput) -> StepOutput:
    session_id = step_input.workflow_session.session_id
    session_dirpath = f'../downloads/{session_id}'
    os.makedirs(session_dirpath, exist_ok=True)
    with open(f'{session_dirpath}/{sanitize_filename(step_input.input)}_report.ppt.html', 'w', encoding='utf-8', errors='replace') as f:
        f.write(step_input.previous_step_content)
    return 'PPT报告保存完成'


def print_url_for_report(step_input: StepInput) -> StepOutput:
    session_id = step_input.workflow_session.session_id
    return f'[访问报告](/list/{session_id})'


steps_html_report = Steps(
    name='网页报告生成',
    steps=[
        Step(name='网页报告生成', agent=agent_html_report),
        Step(name='保存网页报告', executor=save_html_report_file),
    ],
)

steps_markdown_report = Steps(
    name='Markdown报告生成',
    steps=[
        Step(name='Markdown报告生成', agent=agent_markdown_report),
        Step(name='保存markdown报告', executor=save_markdown_report_file),
    ],
)

steps_ppt_report = Steps(
    name='PPT报告生成',
    steps=[
        Step(name='PPT报告生成', agent=agent_ppt_report),
        Step(name='保存PPT报告', executor=save_ppt_report_file),
    ],
)

workflow = Workflow(
    id='deep-research-pipeline',
    name='深度研究流水线',
    # db=SqliteDb(db_file='agno.db'),
    steps=[
        Step(name='任务分析与规划', agent=agent_task_planner),
        Step(name='深度研究', team=team_deep_research),
        Parallel(
            steps_html_report,
            steps_markdown_report,
            # steps_ppt_report,
        ),
        Step(name='报告链接访问地址', executor=print_url_for_report),
    ],
)

agent_os = AgentOS(
    workflows=[workflow],
)

app = agent_os.get_app()

app.add_middleware(
    JWTMiddlewareWithExclusion,
    exclude_urls=['https://os.agno.com'],
    verification_keys=['Yv7uMsDu6ebYt28U8qRm39s8DKoW8yoaDlKdf2ikDMjkZcts1rHLej7BfqK3sl18'],
    algorithm='HS256',
    validate=True,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'https://os.agno.com',
        'http://127.0.0.1:8101',
        'http://10.4.10.226:8101',
    ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/steps_info')
def get_steps_info():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=utils.extract_step_info(workflow),
    )


if __name__ == '__main__':
    # Default port is 7777; change with port=...
    agent_os.serve(app='app:app', access_log=True, host='0.0.0.0', port=8102)

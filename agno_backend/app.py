from agno.models.siliconflow import Siliconflow
from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.os import AgentOS
from middleware import JWTMiddlewareWithExclusion
from agno.tools.arxiv import ArxivTools
from agno.tools.duckduckgo import DuckDuckGoTools
from fastapi.middleware.cors import CORSMiddleware
from agno.team import Team
import prompt
from agno.workflow import Step, Workflow, StepOutput, StepInput, Parallel, Steps
import os
import utils
from pathvalidate import sanitize_filename
from fastapi.responses import JSONResponse
from fastapi import status

# model定义
model_deepseek_v32 = Siliconflow(
    id='Pro/deepseek-ai/DeepSeek-V3.2',
    api_key='sk-xxxx',
    base_url='https://api.siliconflow.cn/v1',
)

agent_task_planner = Agent(
    name='任务分析与规划',
    id='task_planner',
    model=model_deepseek_v32,
    add_datetime_to_context=True,
    tool_call_limit=2,
    tools=[DuckDuckGoTools()],
    markdown=True,
    role='任务分析与规划专家',
    instructions=prompt.task_plan_prompt + prompt.tool_call_prompt,
)


# 根据子问题搜索内容
team_deep_research = Team(
    model=model_deepseek_v32,
    add_datetime_to_context=True,
    tool_call_limit=10,
    id='deep_research',
    name='Deep Research',
    members=[
        Agent(
            name='收集Web内容',
            id='web_content_gather',
            model=model_deepseek_v32,
            tool_call_limit=5,
            add_datetime_to_context=True,
            tools=[DuckDuckGoTools()],
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
            id='arxiv_paper_gather',
            model=model_deepseek_v32,
            tool_call_limit=2,
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
    instructions=prompt.research_teams_prompt + prompt.summary_prompt + prompt.tool_call_prompt,
)

# 网页报告生成
agent_html_report = Agent(
    name='html报告生成',
    id='html_report',
    model=model_deepseek_v32,
    role='html报告生成专家',
    instructions=prompt.html_report_prompt,
)

# markdown报告生成
agent_markdown_report = Agent(
    name='markdown报告生成',
    id='markdown_report',
    model=model_deepseek_v32,
    role='markdown报告生成专家',
    instructions=prompt.markdown_report_prompt,
)

# ppt报告生成
agent_ppt_report = Agent(
    name='ppt报告生成',
    id='ppt_report',
    model=model_deepseek_v32,
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
    id='deep_research_pipeline',
    name='深度研究流水线',
    db=SqliteDb(db_file='agno.db'),
    steps=[
        Step(name='任务分析与规划', agent=agent_task_planner),
        Step(name='深度研究', team=team_deep_research),
        Parallel(
            steps_html_report,
            steps_markdown_report,
            steps_ppt_report,
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
        'http://127.0.0.1:8000',
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
    agent_os.serve(app='app:app', access_log=True)

import feffery_antd_components as fac
import feffery_utils_components as fuc
from feffery_dash_utils.style_utils import style
from configure import conf


def render_chat_header_content():
    button_parameters = dict(color='default', variant='filled', shape='round')
    return fac.AntdRow(
        [
            fac.AntdCol(fac.AntdText(conf.app_title, style=style(fontSize='1.5em'), strong=True)),
            fac.AntdCol(
                fac.AntdSpace(
                    [
                        fac.AntdButton('基本信息', id='btn-get-agent-team-workflow-info', **button_parameters),
                        fac.AntdButton('历史会话', id='btn-get-history-session', **button_parameters, disabled=True),
                        fac.AntdButton('新建会话', id='btn-new-session', **button_parameters),
                    ],
                    size='middle',
                    wrap=True,
                ),
            ),
        ],
        justify='space-between',
        align='middle',
        className=style(
            padding='10px 20px',
            flex='flex: 0 0 120px',
        ),
        wrap=False,
    )

import feffery_antd_components as fac
import feffery_utils_components as fuc
import feffery_markdown_components as fmc
from feffery_dash_utils.style_utils import style
from utils import dash_util


def render(only_assistant):
    """表示在进行历史消息回放"""
    return dash_util.process_object(
        fac.Fragment(
            [
                *(
                    []
                    if only_assistant
                    else [
                        fac.AntdFlex(
                            [
                                fac.AntdAvatar(
                                    size=32,
                                    mode='icon',
                                    shape='square',
                                    icon='antd-user',
                                ),
                                fac.AntdSpace(
                                    [
                                        fac.AntdText('message_placeholder', style={'display': 'inline-block', 'whiteSpace': 'pre-line'}),
                                        fac.AntdCopyText(text='message_placeholder'),
                                    ]
                                ),
                            ],
                            justify='flex-start',
                            align='center',
                            gap=20,
                        )
                    ]
                ),
                fac.AntdFlex(
                    [
                        fac.AntdAvatar(
                            size=32,
                            mode='icon',
                            shape='square',
                            icon='pi-cpu',
                            style=style(background='#ff4017', flex='0 0 auto', marginTop=10),
                        ),
                        fac.AntdCollapse(
                            id={'type': 'event-collapse-events', 'index': 'server_run_id_placeholder'},
                            children=[],
                            title=fac.AntdSpace(
                                [
                                    fac.AntdIcon(id={'type': 'event-collapse-title-icon', 'index': 'server_run_id_placeholder'}, icon='antd-loading').to_plotly_json(),
                                    fac.AntdText(id={'type': 'event-collapse-title-text', 'index': 'server_run_id_placeholder'}).to_plotly_json(),
                                ],
                            ).to_plotly_json(),
                            collapsible='header',
                            isOpen=False,
                            className='event-collapse',
                            classNames={'header': 'event-collapse-header'},
                            style=style(flex=1),
                        ),
                    ],
                    justify='flex-start',
                    align='flex-start',
                    gap=20,
                ),
                fac.AntdFlex(
                    children=[],
                    id={'type': 'show-tool-result-div', 'index': 'server_run_id_placeholder'},
                    justify='flex-start',
                    align='center',
                    gap=10,
                    style=style(marginLeft='15px'),
                    wrap='wrap',
                ),
                fmc.FefferyMarkdown(
                    id={'type': 'assistant-output', 'index': 'server_run_id_placeholder'},
                    markdownStr='',
                    codeTheme='dracula',
                    codeBlockStyle={
                        'overflowX': 'auto',
                    },
                    style=style(background='transparent', font=12, marginLeft='15px'),
                ),
                fac.AntdFlex(
                    [
                        fac.AntdTooltip(
                            fac.AntdIcon(icon='antd-bar-chart', style={'fontSize': 16}).to_plotly_json(),
                            id={'type': 'statistic-token-output', 'index': 'server_run_id_placeholder'},
                            title='a',
                            styles={
                                'body': {'display': 'inline-block', 'whiteSpace': 'pre-line', 'fontFamily': 'monospace'},
                            },
                        ),
                        fac.AntdCopyText(id={'type': 'copy-output', 'index': 'server_run_id_placeholder'}),
                    ],
                    id={'type': 'statistic-output', 'index': 'server_run_id_placeholder'},
                    style=style(display='none'),  # 运行结束就显示
                    gap='middle',
                    align='center',
                    justify='flex-end',
                ),
            ]
        ),
    )

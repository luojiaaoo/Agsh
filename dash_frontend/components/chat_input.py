import feffery_antd_components as fac
import feffery_utils_components as fuc
from feffery_dash_utils.style_utils import style
from dash import dcc
from utils.enum_domain import BtnSendInputStatus


def render_chat_input_content():
    """渲染用户输入区域"""

    return fuc.FefferyDiv(
        [
            fac.Fragment(
                [
                    # ctrl+enter事件监听
                    fuc.FefferyKeyPress(id='ctrl-enter-keypress', keys='ctrl.enter'),
                    dcc.Store(id='btn-send-input-status'),
                ]
            ),
            fuc.FefferyDiv(
                [  # 对话输入框
                    fac.AntdInput(
                        id='input-text',
                        placeholder='Enter 换行，Ctrl + Enter 发送',
                        mode='text-area',
                        style=style(
                            height='100%',
                            width='100%',
                            resize='none',
                            borderRadius='1.5em',
                        ),
                        autoComplete='off',
                        value='',
                    ),
                    # 对话发送按钮
                    fac.AntdButton(
                        '发送',
                        id='btn-send-input',
                        debounceWait=1000,
                        icon=fac.AntdIcon(icon='antd-export', id='btn-send-input-icon'),
                        variant='solid',
                        style={
                            'position': 'absolute',
                            'right': '20px',
                            'bottom': 10,
                        },
                        disabled=True,
                    ),
                    # 上传文档的按钮
                    fac.AntdUpload(
                        apiUrl='/document/make_file_markdown',
                        multiple=True,
                        buttonContent='文档',
                        id='btn-upload-document',
                        showUploadList=False,
                        style={
                            'position': 'absolute',
                            'right': '20px',
                            'bottom': 60,
                        },
                    ),
                ],
                style={
                    'height': '80%',
                    'maxWidth': '800px',
                    'width': '90%',
                    'position': 'relative',
                    'margin': 'auto',
                },
            ),
        ],
        className={
            'height': '150px',
            '& textarea': style(padding='10px 120px 10px 14px'),
            '& .ant-btn-icon': style(marginRight='2px !important'),
        },
    )

from dash import Input, Output, State
import feffery_antd_components as fac
import feffery_utils_components as fuc
from server import app
from feffery_dash_utils.style_utils import style


def render_chat_area_content():
    """渲染对话区域"""

    return fuc.FefferyDiv(
        [
            fac.AntdSpin(
                fac.AntdFlex(
                    children=[],
                    id='chat-area-list',
                    className=style(
                        maxWidth='900px',
                        width='90%',
                        margin='0 auto',
                    ),
                    vertical=True,
                    gap=5,
                ),
                id='spin-chat-area-list',
                fullscreen=True,
                manual=True,
            )
        ],
        id='chat-area',
        className=style(
            overflowY='auto',
            padding='20px 20px 30px',
            scrollbarWidth='thin',
            scrollbarColor='rgba(144,147,153,.2) #fff',
            flex=1,
        ),
    )

import feffery_antd_components as fac
import feffery_utils_components as fuc
from dash import dcc
from feffery_dash_utils.style_utils import style
from utils import auth_util
from server import app, server  # noqa: F401
import app_c  # noqa: F401
from configure import conf
from dash import html
from components import chat_header, chat_area, chat_input
import uuid


def render_layout(user_id = 'luojiaaoo'):
    session_id = uuid.uuid4().hex
    layout = fac.AntdConfigProvider(
        [
            html.Div(id='backgroud-animation', style=style(position='absolute', width='100vw', height='100vh', zIndex=-1)),
            # 特殊用途
            fac.Fragment(
                [
                    # 通用
                    fuc.FefferySetFavicon(favicon='/assets/logo.ico'),  # 设置favicon
                    fuc.FefferyExecuteJs(id='global-exec-js'),  # 执行JS
                    fuc.FefferyListenUnload(id='global-unload'),  # 资源清理
                    fac.Fragment(id='container-modal'),  # 模态框容器
                    # 运行相关
                    fac.Fragment(id='container-history-session'),  # 历史会话容器
                    dcc.Store(id='store-component-conf'),  # agents/teams/workflows的conf配置
                    dcc.Store(id='store-agno-agentos-url', data=conf.agno_agentos_url),  # agentos地址
                    dcc.Store(id='store-agno-type', data=conf.agno_type),  # 类型
                    dcc.Store(id='store-agno-id', data=conf.agno_id),  # agno id
                    dcc.Store(id='store-user-id', data=user_id),  # 登录用户名
                    dcc.Store(id='store-session-id', data=session_id),  # 当前的会话ID
                    dcc.Store(id='store-run-id'),  # 浏览器回调回传的run_id
                    # 鉴权相关
                    dcc.Interval(id='interval-for-set-bearer-token', interval=1000 * 60 * 5),  # 每5分钟秒生成授权token，用于后端的鉴权
                    dcc.Store(id='store-bearer-token', storage_type='session', data=auth_util.gen_access_token(user_id=user_id,session_id=session_id)),  # 存储最新的Bearer Token
                    # sse缓存取数
                    dcc.Interval(id='dequeue-interval', interval=100, disabled=True),  # 从队列里面取
                ]
            ),
            fac.AntdFlex(
                [
                    chat_header.render_chat_header_content(),
                    chat_area.render_chat_area_content(),
                    chat_input.render_chat_input_content(),
                ],
                vertical=True,
                wrap=False,
                className=style(
                    height='100vh',
                    width='100vw',
                ),
            ),
        ],
    )
    return layout


app.layout = render_layout


if __name__ == '__main__':
    app.run(
        debug=not conf.is_launch_prod,
        host=conf.host,
        port=conf.port,
    )

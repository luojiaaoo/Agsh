from server import app
from dash import ClientsideFunction
from dash.dependencies import Input, Output, State, MATCH
from configure import conf
from urllib.parse import quote
import dash
import feffery_antd_components as fac
import feffery_utils_components as fuc
from feffery_dash_utils.style_utils import style
from dash import dcc
import requests
import uuid
from utils import auth_util


# 获取数据库等基础配置
@app.callback(
    Output('store-component-conf', 'data'),
    Input('store-bearer-token', 'id'),
    State('store-bearer-token', 'data'),
)
def get_config(_, bearer_token):
    headers = {'Authorization': f'Bearer {bearer_token}'}
    response = requests.get(url=f'{conf.agno_agentos_url}/config', headers=headers)
    response.raise_for_status()
    return response.json()


# 查看agent team workflow配置
@app.callback(
    Output('container-modal', 'children'),
    Input('btn-get-agent-team-workflow-conf', 'nClicks'),
    [
        State('store-agno-type', 'data'),  # 类型
        State('store-agno-id', 'data'),  # agno id
        State('store-bearer-token', 'data'),
    ],
    prevent_initial_call=True,
)
def popup_modal(nClick, agno_type, agno_id, bearer_token):
    headers = {'Authorization': f'Bearer {bearer_token}'}
    response = requests.get(url=f'{conf.agno_agentos_url}/{agno_type}', headers=headers)
    response.raise_for_status()
    return fac.AntdModal(
        fuc.FefferyJsonViewer(data=[i for i in response.json() if i['id'] == agno_id][0], collapsed=2, iconStyle='square', indent=6),
        title=f'{agno_type}配置',
        visible=True,
        width='600px',
    )


# 按钮的状态机
app.clientside_callback(
    ClientsideFunction(
        namespace='app_clientside',
        function_name='handleBtnSendStatus',
    ),
    [
        Output('btn-send-input', 'disabled'),
        Output('btn-send-input', 'color'),
        Output('btn-send-input', 'children'),
        Output('btn-send-input-icon', 'icon'),
    ],
    Input('btn-send-input-status', 'data'),
)

# 无内容按钮为禁用状态
app.clientside_callback(
    ClientsideFunction(
        namespace='app_clientside',
        function_name='handleDisableBtnSend',
    ),
    Output('btn-send-input-status', 'data'),
    Input('input-text', 'value'),
    State('btn-send-input-status', 'data'),
)


# jwt认证
@app.callback(
    Output('store-bearer-token', 'data'),
    [
        Input('interval-for-set-bearer-token', 'n_intervals'),  # 周期更新
        Input('store-session-id', 'data'),  # 会话变更也更新
    ],
    State('store-user-id', 'data'),
)
def set_token(_, session_id, user_id):
    return auth_util.gen_access_token(user_id=user_id, session_id=session_id)


# 发送用户消息
app.clientside_callback(
    ClientsideFunction(
        namespace='app_clientside',
        function_name='handleUserNewMessageSend',
    ),
    [
        Output('btn-send-input-status', 'data', allow_duplicate=True),  # 更新发送按钮状态
        Output('dequeue-interval', 'disabled'),  # 开始刷sse数据
        Output('input-text', 'value', allow_duplicate=True),  # 清空input窗口
    ],
    [
        # 发送行为触发
        Input('ctrl-enter-keypress', 'pressedCounts'),  # ctrl.enter发生
        Input('btn-send-input', 'nClicks'),  # 按钮发送
    ],
    [
        # 发送行为触发
        State('input-text', 'value'),  # 有内容
        State('input-text', 'focusing'),  # 选中输入框
        # bearer token
        State('store-bearer-token', 'data'),  # 授权
        # 是否可以发送
        State('btn-send-input-status', 'data'),  # 按钮状态
        # 用户名和会话ID
        State('store-user-id', 'data'),
        State('store-session-id', 'data'),
        # agno属性
        State('store-agno-type', 'data'),
        State('store-agno-id', 'data'),
    ],
    prevent_initial_call=True,
)

# 停止消息
app.clientside_callback(
    ClientsideFunction(
        namespace='app_clientside',
        function_name='handleStopSession',
    ),
    Output('btn-send-input', 'id'),
    Input('btn-send-input', 'nClicks'),
    State('btn-send-input-status', 'data'),
    prevent_initial_call=True,
)

# 每0.1秒从队列取出一个
app.clientside_callback(
    ClientsideFunction(
        namespace='app_clientside',
        function_name='handleSseDequeueMessage',
    ),
    Output('btn-send-input-status', 'id'),
    Input('dequeue-interval', 'n_intervals'),
    State('store-agno-type', 'data'),
    prevent_initial_call=True,
)

# tool按钮查看内容
app.clientside_callback(
    ClientsideFunction(
        namespace='app_clientside',
        function_name='handleShowToolDrawer',
    ),
    Output({'type': 'tool-drawer', 'index': MATCH}, 'visible'),
    Input({'type': 'show-tool-drawer', 'index': MATCH}, 'nClicks'),
    prevent_initial_call=True,
)


# 历史会话
@app.callback(
    Output('container-history-session', 'children'),
    Input('btn-get-history-session', 'nClicks'),
    prevent_initial_call=True,
)
def show_(nClicks):
    table = fac.AntdTable(
        id='table-history-session',
        columns=[
            {
                'title': '会话',
                'dataIndex': 'session_name',
                'width': '100%',
                'renderOptions': {'renderType': 'ellipsis'},
            },
            {
                'title': '载入',
                'dataIndex': 'load',
                'width': '60px',
                'renderOptions': {'renderType': 'button'},
            },
            {
                'title': '删除',
                'dataIndex': 'delete',
                'width': '60px',
                'renderOptions': {'renderType': 'button'},
            },
        ],
        pagination={
            'current': 1,
            'pageSize': 15,
            'pageSizeOptions': [5, 8, 15],
            'position': 'topCenter',
            'showLessItems': True,
        },
        bordered=True,
        mode='server-side',
        # showHeader=False,
    )
    return fac.AntdDrawer(
        [
            fac.AntdSpin(
                table,
                text='数据加载中',
                size='small',
                manual=True,
                id='spin-table-history-session',
            ),
            dcc.Store(id='flush-table-history-session-data', data=uuid.uuid4().hex),
        ],
        title='历史会话',
        visible=True,
        destroyOnClose=True,
        width='500px',
        styles={'body': style(padding='0px')},
        id='drawer-history-session',
    )


# 历史会话加载数据
@app.callback(
    [
        Output('table-history-session', 'data'),
        Output('table-history-session', 'pagination'),
    ],
    [
        Input('flush-table-history-session-data', 'data'),
        Input('table-history-session', 'pagination'),
    ],
    [
        State('store-bearer-token', 'data'),  # 授权
        State('store-user-id', 'data'),  # 用户id
        State('store-component-conf', 'data'),  # 配置信息
    ],
    running=[
        [Output('spin-table-history-session', 'spinning'), True, False],
    ],
)
def table_server_side_mode_pagination_demo_sql(_, pagination, bearer_token, user_id, component_conf):
    if pagination is None:
        return dash.no_update
    pageSize = pagination['pageSize']
    page = pagination['current']
    quote_user_id = quote(user_id)
    quote_component_id = quote(conf.agno_id)
    component_type = conf.agno_type[:-1]  # 要去掉一个s
    db = component_conf['session']['dbs'][0]
    db_id = db['db_id']
    table = db['tables'][0]
    url = (
        f'{conf.agno_agentos_url}/sessions?page={page}&type={component_type}&limit={pageSize}&sort_by=updated_at&sort_order=desc&'
        f'user_id={quote_user_id}&component_id={quote_component_id}&db_id={db_id}&table={table}'
    )
    headers = {'Authorization': f'Bearer {bearer_token}'}
    response = requests.get(url=url, headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()['data']
    page = response.json()['meta']['page']
    limit = response.json()['meta']['limit']
    total_count = response.json()['meta']['total_count']
    return (
        [
            {
                'session_name': session['session_name'],
                'load': {
                    'content': '选中',
                    'color': 'default',
                    'variant': 'filled',
                    'custom': session['session_id'],
                },
                'delete': {
                    'content': '删除',
                    'color': 'danger',
                    'variant': 'filled',
                    'custom': session['session_id'],
                    'popConfirmProps': {
                        'title': '确认删除？',
                        'okText': '确认',
                        'cancelText': '取消',
                    },
                },
            }
            for session in data
        ],
        {
            'total': total_count,
            'current': page,
            'pageSize': limit,
            **pagination,
        },
    )


# 删除历史会话
@app.callback(
    Output('flush-table-history-session-data', 'data'),  # 刷新表格数据
    Input('table-history-session', 'nClicksButton'),
    [
        State('table-history-session', 'clickedCustom'),
        State('table-history-session', 'recentlyButtonClickedDataIndex'),
        State('store-bearer-token', 'data'),
    ],
    prevent_initial_call=True,
)
def delete_history_session(nClicksButton, session_id, ops_type, bearer_token):
    if ops_type == 'delete':
        headers = {'Authorization': f'Bearer {bearer_token}'}
        response = requests.delete(url=f'{conf.agno_agentos_url}/sessions/{session_id}', headers=headers)
        response.raise_for_status()
        return uuid.uuid4().hex
    return dash.no_update


# 进入历史会话
app.clientside_callback(
    ClientsideFunction(
        namespace='app_clientside',
        function_name='handleLoadHistorySession',
    ),
    Output('store-session-id', 'data'),
    Input('table-history-session', 'nClicksButton'),
    [
        State('table-history-session', 'clickedCustom'),
        State('table-history-session', 'recentlyButtonClickedDataIndex'),
        State('store-agno-agentos-url', 'data'),
        State('store-agno-type', 'data'),
    ],
    prevent_initial_call=True,
)

# 新建会话
app.clientside_callback(
    ClientsideFunction(
        namespace='app_clientside',
        function_name='handleNewSession',
    ),
    [
        Output('store-session-id', 'data', allow_duplicate=True),
        Output('chat-area-list', 'children', allow_duplicate=True),
    ],
    Input('btn-new-session', 'nClicks'),
    prevent_initial_call=True,
)

# 资源清理
app.clientside_callback(
    ClientsideFunction(
        namespace='app_clientside',
        function_name='handleUnload',
    ),
    Output('global-unload', 'id'),
    Input('global-unload', 'unloaded'),
    prevent_initial_call=True,
)

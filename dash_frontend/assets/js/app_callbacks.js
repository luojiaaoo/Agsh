window.dash_clientside = Object.assign({}, window.dash_clientside, {
    app_clientside: {
        handleBtnSendStatus: (status) => {
            if (status === 'DISABLED') {
                return [true, 'primary', '发送', 'antd-export']
            } else if (status === 'NO_SEND') {
                return [false, 'primary', '发送', 'antd-export']
            } else if (status === 'SENDING') {
                return [false, 'danger', '停止', 'antd-power-off']
            }
        },
        handleDisableBtnSend: (value, status) => {
            if (status !== 'SENDING' || status === undefined) {
                if (value.trim() === "") {
                    return 'DISABLED'
                } else {
                    return 'NO_SEND'
                }
            }
            return window.dash_clientside.no_update
        },
        handleUserNewMessageSend: async (pressedCounts, nClicks, input_text, focusing, bearer_token, btn_send_input_status, user_id, session_id, agno_type, agno_id) => {
            // 状态不是NO_SEND就不能发送
            if (btn_send_input_status !== 'NO_SEND') {
                console.debug(`状态不满足发送条件${btn_send_input_status}`)
                return window.dash_clientside.no_update;
            }
            // 按按钮，但是是初始化回调触发的，忽略
            if (dash_clientside.callback_context.triggered_id === 'btn-send-input' && nClicks === undefined) {
                return window.dash_clientside.no_update;
            }
            // 不在聚焦状态下，按ctrl+enter也没用
            if (dash_clientside.callback_context.triggered_id === 'ctrl-enter-keypress' && !focusing) {
                return window.dash_clientside.no_update;
            }
            let { server_run_id, component } = get_message_box(input_text)
            dash_clientside.set_props('chat-area-list', { children: [...dash_component_api.getLayout('chat-area-list').props.children, component] })
            window.server_run_id = server_run_id;
            // 发起sse
            const form = new FormData();
            form.append('message', input_text);
            form.append('stream', true);
            form.append('user_id', user_id);
            form.append('session_id', session_id);
            start_sse(`/${agno_type}/${agno_id}/runs`, form, bearer_token)
            scroll_chat_area()
            return ['SENDING', false, '']
        },
        handleStopSession: (nClicks, status) => {
            if (status !== 'SENDING') return window.dash_clientside.no_update
            close_session()
            return window.dash_clientside.no_update
        },
        handleSseDequeueMessage: async (n_intervals, agno_type) => {
            let data = await window.sse_queue.dequeue()
            if (data === null) {
                return window.dash_clientside.no_update
            }
            if (agno_type === 'agents') {  //           ******* agents类型 *******
                handle_agent(data)
            } else if (agno_type === 'teams') {                  // ***** teams类型  *******
                handle_team(data)
            } else if (agno_type === 'workflows') {                  // ***** workflows类型  *******
                await handle_workflow(data)
            }
            return window.dash_clientside.no_update
        },
        handleShowToolDrawer: (nClicks) => {
            return true
        },
        handleStopAssistantMessage: (nClicks) => {
            return ['close', false, true]
        },
        handleNewSession: (nClicks) => {
            close_session();
            return [uuidHex(), []];
        },
        handleUnload: (_) => {
            close_session()
        },
        handleLoadHistorySession: async (nClicksButton, session_id, ops_type, agno_agentos_url, agno_type) => {
            if (ops_type === 'load') {
                dash_clientside.set_props('drawer-history-session', { visible: false }) // 收起历史会话
                dash_clientside.set_props('spin-chat-area-list', { spinning: true })
                close_session() // 停止之前的会话
                dash_clientside.set_props('chat-area-list', { children: [] }) // 清空显示
                let true_interval = dash_component_api.getLayout('dequeue-interval').props.interval
                // 获取历史消息
                let messages = await getData(
                    url = agno_agentos_url + '/sessions/' + session_id + '/runs',
                    with_token = true,
                    queryParams = { 'session_id': session_id, 'type': agno_type.slice(0, -1) }
                )
                // 遍历历史消息
                for (const message of messages) {
                    if (!message.hasOwnProperty('run_input') || !message.hasOwnProperty('events')) {
                        continue
                    }
                    let input_text = message['run_input']
                    let event_messages = message['events']
                    // 插入message_box
                    let { server_run_id, component } = get_message_box(input_text)
                    window.server_run_id = server_run_id;
                    // 新增消息组件
                    dash_clientside.set_props('chat-area-list', { children: [...dash_component_api.getLayout('chat-area-list').props.children, component] })
                    scroll_chat_area()
                    event_messages.forEach(item => { { window.sse_queue.enqueue(item); } }); // 放入队列
                    dash_clientside.set_props('dequeue-interval', { interval: 1 }) // 加速加载
                    dash_clientside.set_props('dequeue-interval', { disabled: false }) // 开始消耗队列，向消息组件插入字符串
                    await window.sse_queue.waitUntilEmpty() // 等待取完，再遍历下一个消息，保证一个消息对应一个server_run_id
                }
                dash_clientside.set_props('spin-chat-area-list', { spinning: false })
                dash_clientside.set_props('dequeue-interval', { interval: true_interval }) // 还原速度
                close_session() // 停止会话
                return session_id
            }
            return window.dash_clientside.no_update
        },
        handleUploadDocument: (lastUploadTaskRecord, input, maxLength) => {
            for (let record of lastUploadTaskRecord) {
                if (record.taskStatus === 'success') {
                    input += `\n\n<附件-${record.fileName}>\n${record.uploadResponse.md_content}\n</附件-${record.fileName}>`;
                }
            }
            return input.slice(0, maxLength)
        }
    }
});
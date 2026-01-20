// 改造console.error()以隐藏无关痛痒的警告信息
const originalConsoleError = console.error;
console.error = function (...args) {
    // 检查args中是否包含需要过滤的内容
    const shouldFilter = args.some(arg => typeof arg === 'string' && arg.includes('Warning:'));

    if (!shouldFilter) {
        originalConsoleError.apply(console, args);
    }
};

function uuidHex() {
    const hex = [];
    for (let i = 0; i < 16; i++) {
        hex[i] = Math.floor(Math.random() * 256);
    }
    // 设置版本号为 4
    hex[6] = (hex[6] & 0x0f) | 0x40;
    // 设置变体为 10xx
    hex[8] = (hex[8] & 0x3f) | 0x80;
    // 转成 32 位 hex 字符串
    return hex.map(b => b.toString(16).padStart(2, '0')).join('');
}



async function getData(url, with_token = false, queryParams = {}) {
    try {
        const headers = {};
        // 从sessionStorage获取token
        if (with_token) {
            const token = sessionStorage.getItem('store-bearer-token').replace(/^"(.+)"$/, '$1');
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
        }

        // 使用URL对象处理参数
        const baseURL = window.location.origin;
        const fullURL = url.startsWith('http') ? url : `${baseURL}${url.startsWith('/') ? url : '/' + url}`;
        const obj_url = new URL(fullURL);
        Object.entries(queryParams).forEach(([key, value]) => {
            if (value !== undefined && value !== null) {
                obj_url.searchParams.append(key, value);
            }
        });

        const res = await fetch(
            obj_url.toString(),
            {
                method: 'GET',
                headers: headers
            }
        );
        if (!res.ok) {
            throw new Error(res.status);
        }
        const jsonResponse = await res.json();
        return jsonResponse;
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

// 发送POST请求
async function postData(url, data, with_token) {
    try {
        const headers = {
            'Content-Type': 'application/json',
        };
        // 从sessionStorage获取token
        if (with_token) {
            const token = sessionStorage.getItem('store-bearer-token').replace(/^"(.+)"$/, '$1');
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
        }
        const response = await fetch(url, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(data)
        });

        // 检查响应状态
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // 解析JSON响应
        const jsonResponse = await response.json();
        return jsonResponse;

    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

(async () => {
    const response = await getData(
        url = '/component/message_box',
        with_token = false,
    )
    window.message_box = response.component;
})();

function get_message_box(message) {
    let server_run_id = uuidHex()
    let repr_message = JSON.stringify({ 'v': message }).match(/\{"v":"(.*)"\}/)[1]
    component = JSON.parse(window.message_box.replaceAll('message_placeholder', repr_message).replaceAll('server_run_id_placeholder', server_run_id))
    return {
        'server_run_id': server_run_id,
        'component': component
    }
}

// workflows类型单独新增AI消息框
(async () => {
    const response = await getData(
        url = '/component/message_box?only_assistant=true',
        with_token = false,
    )
    window.assistant_message_box = response.component;
})();
function get_assistant_message_box(step_id) {
    component = JSON.parse(window.assistant_message_box.replaceAll('server_run_id_placeholder', step_id))
    return {
        'component': component
    }
}

async function postSSE(url, options) {
    const {
        body,
        headers = {},
        onMessage,
        onError,
        onOpen,
        onClose,
        onAbort,
        signal,
    } = options;

    const safeCall = (fn, ...args) => {
        try {
            if (typeof fn === 'function') {
                return Promise.resolve(fn(...args));
            }
        } catch (e) {
            return Promise.reject(e);
        }
    };

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Accept': 'text/event-stream',
                ...headers,
            },
            body,
            signal,
        });

        if (!response.ok) {
            throw new Error('HTTP error ' + response.status);
        }

        await safeCall(onOpen, response);

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });

            const events = buffer.split('\n\n');
            buffer = events.pop();

            for (const event of events) {
                await parseSSE(event);
            }
        }

        buffer += decoder.decode(); // flush

        await safeCall(onClose);

    } catch (err) {
        if (err.name === 'AbortError') { // 如果是手动终止，调用onAbort和onClose函数
            await safeCall(() => onAbort?.());
            await safeCall(onClose);
            return
        }
        await safeCall(onError, err);
    }

    async function parseSSE(chunk) {
        const lines = chunk.split('\n');
        let data = '';

        for (const line of lines) {
            if (line.startsWith('data:')) {
                data += line.slice(5).trim() + '\n';
            }
        }

        if (data) {
            await safeCall(onMessage, data.trim());
        }
    }
}


window.sse_controller = null


async function start_sse(run_path, form, bearer_token) {
    let agno_agentos_url = dash_component_api.getLayout('store-agno-agentos-url').props.data
    run_url = agno_agentos_url + run_path
    window.sse_controller = new AbortController();
    postSSE(run_url, {
        body: form,
        headers: { 'Authorization': `Bearer ${bearer_token}` },
        signal: window.sse_controller.signal,
        onOpen() {
            console.debug('SSE 连接已建立');
        },
        onMessage: async (data) => {
            let json_data = JSON.parse(data)
            if (json_data?.run_id !== undefined) {
                dash_clientside.set_props('store-run-id', { data: json_data.run_id }) // 保存run_id，用于cancel操作
            }
            await window.sse_queue.enqueue(json_data);
        },
        onError(err) {
            console.error('SSE error:', err);
        },
        onClose() {
            window.sse_controller = null
            console.debug('SSE closed');
        },
        async onAbort() { // 终止sse的时候，顺便把远程任务的也关闭了
            run_id = dash_component_api.getLayout('store-run-id').props.data
            if (run_id) {
                cancel_url = run_url + '/' + run_id + '/cancel'
                await postData(
                    url = cancel_url,
                    data = {},
                    with_token = true,
                )
            }
        }
    });
}

function close_session(abort_sse = true) {
    switch_btn_send_input_status_out_of_sending() // 恢复按钮
    if (window.sse_controller !== null && abort_sse) {
        window.sse_controller.abort();   // 终止SSE
    }
    window.sse_queue.clear()
    dash_clientside.set_props('dequeue-interval', { disabled: true }) // 停止sse取出队列
}

function switch_btn_send_input_status_out_of_sending() {
    if (dash_component_api.getLayout('input-text').props.value.trim() === '') {
        dash_clientside.set_props('btn-send-input-status', { data: 'DISABLED' })
    } else {
        dash_clientside.set_props('btn-send-input-status', { data: 'NO_SEND' })
    }
}


class AgnoSseQueue {
    constructor() {
        this._queue = [];
        this._lock = false;
        this._pendingOperations = [];
    }

    /* ---------- 简单互斥锁 ---------- */

    async _executeWithLock(operation) {
        return new Promise((resolve, reject) => {
            const execute = async () => {
                while (this._lock) {
                    await new Promise(res => setTimeout(res, 0));
                }
                this._lock = true;
                try {
                    const result = await operation();
                    resolve(result);
                } catch (err) {
                    reject(err);
                } finally {
                    this._lock = false;
                    if (this._pendingOperations.length > 0) {
                        const next = this._pendingOperations.shift();
                        next();
                    }
                }
            };

            if (this._lock) {
                this._pendingOperations.push(execute);
            } else {
                execute();
            }
        });
    }

    /* ---------- 合并规则 ---------- */

    _canMerge(item1, item2) {
        if (!item1 || !item2) return false;

        const keys1 = Object.keys(item1);
        const keys2 = Object.keys(item2);

        if (keys1.length !== keys2.length) return false;

        for (const key of keys1) {
            if (!keys2.includes(key)) return false;

            // 只允许 content / reasoning_content 不一致
            if (!['created_at', 'content', 'reasoning_content'].includes(key)) {
                if (String(item1[key]) !== String(item2[key])) {
                    return false;
                }
            }
        }
        return true;
    }

    _mergeItems(base, next) {
        if (!base) return { ...next };
        if (!next) return { ...base };

        const merged = { ...next };

        for (const key of ['content', 'reasoning_content']) {
            if (typeof base[key] === 'string' && typeof next[key] === 'string') {
                merged[key] = base[key] + next[key];
            }
        }
        return merged;
    }

    /* ---------- 队列操作 ---------- */

    // 入队：不做任何合并
    async enqueue(item) {
        return this._executeWithLock(() => {
            this._queue.push(item);
            return this._queue.length;
        });
    }

    // 出队：遍历整个队列，合并所有可合并项，仅移除被合并的
    async dequeue() {
        return this._executeWithLock(() => {
            if (this._queue.length === 0) {
                return null;
            }

            let mergedItem = this._queue[0];
            const removeIndexes = [0];

            // 扫描整个队列（不因失败中断）
            for (let i = 1; i < this._queue.length; i++) {
                const item = this._queue[i];
                if (this._canMerge(mergedItem, item)) {
                    mergedItem = this._mergeItems(mergedItem, item);
                    removeIndexes.push(i);
                }
            }

            // 从后往前删除，避免 index 变化
            for (let i = removeIndexes.length - 1; i >= 0; i--) {
                this._queue.splice(removeIndexes[i], 1);
            }

            return mergedItem;
        });
    }

    size() {
        return this._queue.length;
    }

    isEmpty() {
        return this._queue.length === 0;
    }

    peek() {
        return this._queue.length > 0 ? this._queue[0] : null;
    }

    async clear() {
        return this._executeWithLock(() => {
            this._queue.length = 0;
            return true;
        });
    }

    async waitUntilEmpty(options = {}) {
        const {
            timeout = 0,   // ms，0 表示不超时
            interval = 100
        } = options;

        const start = Date.now();

        return new Promise((resolve, reject) => {
            const check = () => {
                if (this._queue.length === 0) {
                    resolve();
                    return;
                }

                if (timeout > 0 && Date.now() - start > timeout) {
                    reject(
                        new Error(
                            `等待队列为空超时，当前队列长度: ${this._queue.length}`
                        )
                    );
                    return;
                }

                setTimeout(check, interval);
            };

            check();
        });
    }
}



window.sse_queue = new AgnoSseQueue();



function set_event_collapse_title_text(text, step_id = null) {
    let message_box_id = null;
    if (step_id === null) {
        message_box_id = window.server_run_id
    } else {
        message_box_id = step_id
    }
    dash_clientside.set_props(
        { 'type': 'event-collapse-title-text', 'index': message_box_id },
        { children: text },
    )
}

function finish_run(step_id = null) {
    let message_box_id = null;
    if (step_id === null) {
        message_box_id = window.server_run_id
    } else {
        message_box_id = step_id
    }
    dash_clientside.set_props(
        { 'type': 'event-collapse-title-icon', 'index': message_box_id },
        { style: { visibility: 'hidden' } },
    )
}

function scroll_chat_area() {
    let scrollTarget = document.getElementById(dash_component_api.stringifyId('chat-area'))
    scrollTarget.scrollTo({
        top: scrollTarget.scrollHeight
    });
}

function append_assistant_output(text, { replace = false, step_id = null } = {}) {
    if (text === '') {
        return
    }
    let message_box_id = null;
    if (step_id === null) {
        message_box_id = window.server_run_id
    } else {
        message_box_id = step_id
    }
    let markdownStr = null
    if (replace) {
        markdownStr = text
    } else {
        markdownStr = dash_component_api.getLayout({ 'type': 'assistant-output', 'index': message_box_id }).props.markdownStr + text
    }
    dash_clientside.set_props(
        { 'type': 'assistant-output', 'index': message_box_id },
        { markdownStr: markdownStr },
    )
    scroll_chat_area()
}

function append_assistant_event_reasoning(text, { replace = false, step_id = null } = {}) {
    if (text === '') {
        return
    }
    let message_box_id = null;
    if (step_id === null) {
        message_box_id = window.server_run_id
    } else {
        message_box_id = step_id
    }
    let children = dash_component_api.getLayout({ 'type': 'event-collapse-events', 'index': message_box_id }).props.children;
    if (children.length > 0 && children[children.length - 1].props.className === 'reasoning') { // 前面也是reasoning，追加markdownStr
        if (replace) {
            children[children.length - 1].props.markdownStr = text
        } else {
            children[children.length - 1].props.markdownStr = children[children.length - 1].props.markdownStr + text
        }
        dash_clientside.set_props(
            { 'type': 'event-collapse-events', 'index': message_box_id },
            { children: children },
        )
    } else { // 前面是其他的，或者为空，新建markdown组件
        dash_clientside.set_props(
            { 'type': 'event-collapse-events', 'index': message_box_id },
            { children: [...children, { 'props': { 'children': null, 'style': { 'background': 'transparent', 'font': 12 }, 'className': 'reasoning', 'markdownStr': text, 'codeTheme': 'dracula', 'codeBlockStyle': { 'overflowX': 'auto' } }, 'type': 'FefferyMarkdown', 'namespace': 'feffery_markdown_components' }] },
        )
    }
    scroll_chat_area()
}

function append_assistant_event_tool(title, content, btn_show, icon, step_id = null) { // 追加工具按钮
    let message_box_id = null;
    if (step_id === null) {
        message_box_id = window.server_run_id
    } else {
        message_box_id = step_id
    }
    let uuid = uuidHex()
    let children = dash_component_api.getLayout({ 'type': 'show-tool-result-div', 'index': message_box_id }).props.children;
    let button = { 'props': { 'id': { 'type': 'show-tool-drawer', 'index': uuid }, 'children': btn_show, 'icon': { 'props': { 'icon': icon }, 'size': 'small', 'type': 'AntdIcon', 'namespace': 'feffery_antd_components' }, 'color': 'default', 'variant': 'filled' }, 'type': 'AntdButton', 'namespace': 'feffery_antd_components' }
    let drawer = { 'props': { 'id': { 'type': 'tool-drawer', 'index': uuid }, 'children': content, 'title': title, 'placement': 'right', 'width': '500px' }, 'type': 'AntdDrawer', 'namespace': 'feffery_antd_components' }
    dash_clientside.set_props(
        { 'type': 'show-tool-result-div', 'index': message_box_id },
        { children: [...children, button, drawer] },
    )
    scroll_chat_area()
}

window.statistic_token = {}

function clear_metrics() {
    window.statistic_token = {}
}

function merge_metrics(metric) {
    for (const [key, value] of Object.entries(metric)) {
        if (window.statistic_token[key] === undefined) {
            window.statistic_token[key] = value;
        } else {
            window.statistic_token[key] += value;
        }
    }
}

function formatObject(obj) {
    if (!obj || typeof obj !== 'object' || Array.isArray(obj)) {
        throw new Error('输入必须是对象');
    }

    // 获取所有键，并找到最长的键长度
    const keys = Object.keys(obj);
    if (keys.length === 0) return '';

    const maxKeyLength = Math.max(...keys.map(key => key.length));

    // 格式化每一行
    const lines = keys.map(key => {
        const keyStr = key.padEnd(maxKeyLength, ' ');
        const value = obj[key];

        // 确保值是数字，并按四舍五入取整
        if (typeof value !== 'number' || isNaN(value)) {
            throw new Error(`属性 "${key}" 的值必须是数字`);
        }

        const valueInt = Math.round(value);
        return `${keyStr} : ${valueInt}`;
    });

    return lines.join('\n');
}

function show_statistic_output(output, step_id = null) {
    let message_box_id = null;
    if (step_id === null) {
        message_box_id = window.server_run_id
    } else {
        message_box_id = step_id
    }
    dash_clientside.set_props(
        { 'type': 'copy-output', 'index': message_box_id },
        { text: output },
    )
    dash_clientside.set_props(
        { 'type': 'statistic-token-output', 'index': message_box_id },
        { title: formatObject(window.statistic_token) },
    )
    dash_clientside.set_props(
        { 'type': 'statistic-output', 'index': message_box_id },
        { style: {} },
    )
    scroll_chat_area()
}


function handle_agent(data, step_id = null) {
    let event_type = data.event
    if (event_type === 'RunStarted') {
        set_event_collapse_title_text('开始...', step_id)
        if (step_id === null) {
            clear_metrics()
        }
        return window.dash_clientside.no_update
    } else if (event_type === 'RunContent') {
        if (data.hasOwnProperty('reasoning_content')) { // 思考
            set_event_collapse_title_text('思考中...', step_id)
            append_assistant_event_reasoning(data.reasoning_content, { step_id: step_id })
        }
        if (data.hasOwnProperty('content')) { // 输出
            set_event_collapse_title_text('输出中...', step_id)
            append_assistant_output(data.content, { step_id: step_id })
        }
        return window.dash_clientside.no_update
    } else if (event_type === 'ToolCallStarted') {
        let tool_name = data.tool.tool_name
        let tool_args = data.tool.tool_args
        set_event_collapse_title_text(`调用[${tool_name}]中，参数为${JSON.stringify(tool_args)}...`, step_id)
        return window.dash_clientside.no_update
    } else if (event_type === 'ToolCallCompleted') {
        let tool_name = data.tool.tool_name
        let tool_args = data.tool.tool_args
        let title = `工具${tool_name}(${JSON.stringify(tool_args)})`
        set_event_collapse_title_text(`调用[${tool_name}]成功...`, step_id)
        append_assistant_event_tool(title, data.tool.result, tool_name, 'antd-repair', step_id)
        return window.dash_clientside.no_update
    } else if (event_type === 'RunCompleted') {
        set_event_collapse_title_text('完成', step_id)
        if (data.hasOwnProperty('reasoning_content')) { // 思考
            append_assistant_event_reasoning(data.reasoning_content, { replace: true, step_id: step_id })
        }
        append_assistant_output(data.content, { replace: true, step_id: step_id }) // 最后输出全部替换掉
        merge_metrics(data.metrics)
        finish_run(step_id)
        if (step_id === null) {
            show_statistic_output(data.content)
            close_session(abort_sse = false)
        }
    } else if (event_type === 'RunContentCompleted') {
        return window.dash_clientside.no_update
    }
    console.debug('agents获取数据，未解析', data)
    return window.dash_clientside.no_update
}

function handle_team(data, step_id = null) {
    let event_type = data.event
    if (event_type === 'TeamRunStarted') {
        let team_name = data.team_name
        set_event_collapse_title_text(`团队[${team_name}]开始...`, step_id)
        if (step_id === null) {
            clear_metrics()
        }
        return window.dash_clientside.no_update
    } else if (event_type === 'TeamRunContent') {
        let team_name = data.team_name
        if (data.hasOwnProperty('reasoning_content')) { // 思考
            set_event_collapse_title_text(`[${team_name}]团队思考中...`, step_id)
            append_assistant_event_reasoning(data.reasoning_content, { step_id: step_id })
        }
        if (data.hasOwnProperty('content')) { // 输出
            set_event_collapse_title_text(`[${team_name}]团队输出中...`, step_id)
            append_assistant_output(data.content, { step_id: step_id })
        }
        return window.dash_clientside.no_update
    } else if (event_type === 'TeamToolCallStarted') {
        let team_name = data.team_name
        let member_id = data.tool.tool_args.member_id
        let task = data.tool.tool_args.task
        set_event_collapse_title_text(`[${team_name}]团队派发任务给[${member_id}]：${task}`, step_id)
        return window.dash_clientside.no_update
    } else if (event_type === 'TeamToolCallStarted') {
        let team_name = data.team_name
        let member_id = data.tool.tool_args.member_id
        let task = data.tool.tool_args.task
        set_event_collapse_title_text(`[${team_name}]团队派发任务给[${member_id}]：${task}`, step_id)
        return window.dash_clientside.no_update
    } else if (event_type === 'TeamToolCallCompleted') { // 收成员作业，并总结
        let team_name = data.team_name
        let member_id = data.tool.tool_args.member_id
        let task = data.tool.tool_args.task
        let title = `${team_name}团队派发任务给[${member_id}]：${task}`
        set_event_collapse_title_text(`[${team_name}]团队[${member_id}]：${task}完成...`, step_id)
        append_assistant_event_tool(title, data.tool.result, member_id, 'antd-team', step_id)
        return window.dash_clientside.no_update
    } else if (event_type === 'TeamRunCompleted') {
        let team_name = data.team_name
        set_event_collapse_title_text(`团队[${team_name}]完成`, step_id)
        append_assistant_output(data.content, { replace: true, step_id: step_id })
        merge_metrics(data.metrics)
        if (data.hasOwnProperty('reasoning_content')) { // 思考
            append_assistant_event_reasoning(data.reasoning_content, { replace: true, step_id: step_id })
        }
        finish_run(step_id)
        if (step_id === null) {
            show_statistic_output(data.content)
            close_session(abort_sse = false)
        }
        return window.dash_clientside.no_update
    } else if (event_type === 'TeamRunContentCompleted') {
        return window.dash_clientside.no_update
    } else if (event_type === 'ToolCallStarted') { // 成员agent事件
        let agent_name = data.agent_name
        let tool_name = data.tool.tool_name
        let tool_args = data.tool.tool_args
        set_event_collapse_title_text(`[${agent_name}]调用[${tool_name}]中，参数为${JSON.stringify(tool_args)}...`, step_id)
        return window.dash_clientside.no_update
    } else if (event_type === 'ToolCallCompleted') {
        let agent_name = data.agent_name
        let tool_name = data.tool.tool_name
        let tool_args = data.tool.tool_args
        let title = `工具${tool_name}(${JSON.stringify(tool_args)})`
        set_event_collapse_title_text(`[${agent_name}]调用[${tool_name}]成功...`, step_id)
        append_assistant_event_tool(title, data.tool.result, tool_name, 'antd-repair', step_id)
        return window.dash_clientside.no_update
    } else if (event_type === 'RunStarted') {  // 成员的开始标志
        return window.dash_clientside.no_update
    } else if (event_type === 'RunContent') {  // 成员的流回答
        return window.dash_clientside.no_update
    } else if (event_type === 'RunContentCompleted') {  // 成员的结束标志
        return window.dash_clientside.no_update
    } else if (event_type === 'RunCompleted') {  // 成员的结束标志
        merge_metrics(data.metrics)
        return window.dash_clientside.no_update
    }
    console.debug('teams获取数据，未解析', data)
    return window.dash_clientside.no_update
}

window.global_step_id = null
window.steps_info = null
async function handle_workflow(data) {
    let event_type = data.event
    if (event_type === 'WorkflowStarted') { // 工作流事件
        let workflow_name = data.workflow_name
        set_event_collapse_title_text(`工作流${workflow_name}开始...`)
        clear_metrics()
        finish_run()
        return window.dash_clientside.no_update
    } else if (event_type === 'WorkflowCompleted') { // 工作流结束
        let workflow_name = data.workflow_name
        set_event_collapse_title_text(`工作流[${workflow_name}]完成`, window.global_step_id)
        append_assistant_output(data.content, { replace: true, step_id: window.global_step_id })
        show_statistic_output(data.content, window.global_step_id)
        finish_run(window.global_step_id)
        close_session(abort_sse = false)
        return window.dash_clientside.no_update
    }
    if (window.steps_info === null) {
        let agno_agentos_url = dash_component_api.getLayout('store-agno-agentos-url').props.data
        window.steps_info = await getData(
            url = agno_agentos_url + '/steps_info',
            with_token = true,
        )
    }
    let step_name = data.step_name
    let step_id = data.step_id
    window.global_step_id = step_id
    if (event_type === 'StepStarted') { // 步骤开始，新建AI消息框
        let { component } = get_assistant_message_box(step_id)
        dash_clientside.set_props(
            'chat-area-list',
            { children: [...dash_component_api.getLayout('chat-area-list').props.children, component] },
        )
        set_event_collapse_title_text(`步骤[${step_name}]开始...`, step_id)
        return window.dash_clientside.no_update
    } else if (event_type === 'StepCompleted') { // 步骤结束
        set_event_collapse_title_text(`步骤[${step_name}]完成...`, step_id)
        if (window.steps_info[step_name] === 'executor') {
            append_assistant_output(data.content, { replace: true, step_id: step_id })
        }
        finish_run(step_id)
        return window.dash_clientside.no_update
    } else if (step_name !== undefined) { // 传递给agent或teams处理
        if (window.steps_info[step_name] === 'agent') {
            handle_agent(data, step_id)
        } else if (window.steps_info[step_name] === 'team') {
            handle_team(data, step_id)
        }
        return window.dash_clientside.no_update
    }
    console.debug('workflows获取数据，未解析', data)
    return window.dash_clientside.no_update
}
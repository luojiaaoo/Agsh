from flask import Blueprint, jsonify, request
import traceback
from loguru import logger
from components import message_box
import json

component_bp = Blueprint('component', __name__)


# 获取用户消息盒子组件用于渲染，并且包含sse请求组件，开始请求大模型回复
@component_bp.route('/message_box', methods=['get'])
def get_user_box():
    try:
        only_assistant = request.args.get('only_assistant') == 'true'
        component = message_box.render(only_assistant=only_assistant)
        return jsonify({'component': json.dumps(component)}), 200
    except Exception as e:
        logger.error(f'获取用户消息盒子组件失败: {e}\n{traceback.format_exc()}')

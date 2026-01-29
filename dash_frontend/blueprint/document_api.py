from flask import Blueprint, jsonify, request, abort
import traceback
from loguru import logger
from utils.document_util import make_file_markdown
from configure import conf
from io import BytesIO


document_bp = Blueprint('document', __name__)


@document_bp.route('/make_file_markdown', methods=['post'])
def markdown():
    try:
        vision_enabled = request.values.get('vision_enabled', False)
        # uploadId = request.values.get('uploadId')
        filename = request.files['file'].filename
        with BytesIO() as f:
            for chunk in iter(lambda: request.files['file'].read(1024 * 1024 * 10), b''):
                f.write(chunk)
            file_bytes = f.getvalue()
        rt_json = make_file_markdown(file_name_bytes=(filename, file_bytes), vision_enabled=vision_enabled)
        return jsonify(rt_json), 200
    except Exception as e:
        logger.error(f'文件解析失败: {e}\n{traceback.format_exc()}')
        abort(400, description=f'{filename}解析失败')

from flask import Blueprint, jsonify, request
import traceback
from loguru import logger
from utils.document_util import make_files_markdown


document_bp = Blueprint('document', __name__)


@document_bp.route('/make_files_markdown', methods=['post'])
def get_user_box():
    try:
        files = request.files.getlist('files')
        if not files or all(f.filename == '' for f in files):
            return jsonify({'error': '没有选择文件'}), 400
        files = [(f.filename, f.read()) for f in files if f and f.filename.strip() != '']
        rt_json = make_files_markdown(files, max_token=10000)
        return jsonify(rt_json), 200
    except Exception as e:
        logger.error(f'文件解析失败: {e}\n{traceback.format_exc()}')

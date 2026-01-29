from flask import Blueprint, jsonify, request
import traceback
from loguru import logger
from utils.document_util import make_files_markdown
from configure import conf
from typing import List, Tuple


document_bp = Blueprint('document', __name__)


@document_bp.route('/make_files_markdown', methods=['post'])
def markdown():
    """
    Endpoint to convert uploaded files to markdown format.

    Receives a POST request with files and an optional 'vision_enabled' flag.
    - Expects files to be uploaded via multipart/form-data under the 'files' field.
    - Optional form field 'vision_enabled' (boolean as string) enables vision processing if set to 'true'.

    Returns:
        JSON response containing the markdown conversion result or an error message.

    Responses:
        200: Successfully processed files and returned markdown.
        400: No files were selected for upload.
        500: Internal server error during file processing.
    """
    try:
        files: List[Tuple[str, bytes]] = request.files.getlist('files')
        if not files or all(f.filename.strip() == '' for f in files):
            return jsonify({'error': '没有选择文件'}), 400
        vision_enabled = request.form.get('vision_enabled', 'false').lower() == 'true'
        files = [(f.filename, f.read()) for f in files if f and f.filename.strip() != '']
        rt_json = make_files_markdown(files_name_bytes=files, vision_enabled=vision_enabled, max_token=conf.document_max_token)
        return jsonify(rt_json), 200
    except Exception as e:
        logger.error(f'文件解析失败: {e}\n{traceback.format_exc()}')

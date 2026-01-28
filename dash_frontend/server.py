import dash
from configure import conf
from blueprint import chat_api,document_api
from flask import send_file, abort
import os

app = dash.Dash(
    __name__,
    title=conf.app_title,
    update_title=None,
    suppress_callback_exceptions=True,
)

server = app.server
server.register_blueprint(
    chat_api.component_bp,
    url_prefix='/component',
)
server.register_blueprint(
    document_api.document_bp,
    url_prefix='/document',
)



@server.route('/download/<session_id>/<filename>')
def download_file(session_id, filename):
    download_dir = os.path.join('..', 'downloads', session_id)
    file_path = os.path.join(download_dir, filename)
    if not os.path.exists(file_path):
        abort(400, description='没有这个文件')
    return send_file(file_path, as_attachment=True)


@server.route('/list/<session_id>')
def list_files(session_id):
    try:
        download_dir = os.path.join('..', 'downloads', session_id)
        if not os.path.exists(download_dir):
            abort(400, description='没有这个目录')
        files = []
        for item in os.listdir(download_dir):
            item_path = os.path.join(download_dir, item)
            if os.path.isfile(item_path):
                size = os.path.getsize(item_path)
                # 转换为可读大小
                if size < 1024:
                    size_str = f'{size} B'
                elif size < 1024 * 1024:
                    size_str = f'{size / 1024:.1f} KB'
                else:
                    size_str = f'{size / (1024 * 1024):.1f} MB'
                files.append({'name': item, 'size': size_str, 'path': item_path})
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>文件下载列表</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #333; }}
                .file-list {{ margin-top: 20px; }}
                .file-item {{ 
                    padding: 10px; 
                    border: 1px solid #ddd; 
                    margin: 5px 0;
                    background: #f9f9f9;
                }}
                .file-name {{ font-weight: bold; }}
                .file-size {{ color: #666; font-size: 0.9em; }}
                .download-btn {{
                    background: #4CAF50;
                    color: white;
                    padding: 5px 10px;
                    text-decoration: none;
                    border-radius: 3px;
                    display: inline-block;
                    margin-left: 10px;
                }}
                .download-btn:hover {{ background: #45a049; }}
            </style>
        </head>
        <body>
            <h1>📁 可下载文件列表</h1>
            <p>点击文件名下载文件</p>
            <div class="file-list">
        """
        for file in files:
            html += f"""
            <div class="file-item">
                <span class="file-name">{file['name']}</span>
                <span class="file-size">({file['size']})</span>
                <a href="/download/{session_id}/{file['name']}" class="download-btn">下载</a>
            </div>
            """
        html += (
            """
        </body>
        </html>
        """
        )
        return html

    except Exception as e:
        return f'<h1>错误</h1><p>{str(e)}</p>'


if __name__ == '__main__':
    app.run(debug=True)

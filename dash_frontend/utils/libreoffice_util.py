import os
import tempfile
import subprocess
import shutil
import threading
from typing import Tuple, List

# 全局锁，确保多个用户同时访问时，LibreOffice 进程串行执行，避免并发冲突
_libreoffice_lock = threading.Lock()


def _get_libreoffice_command() -> str:
    """获取可用的 LibreOffice 命令"""
    libreoffice_commands = ['soffice', 'libreoffice', '/usr/bin/soffice', 'C:\\Program Files\\LibreOffice\\program\\soffice.exe']

    for cmd in libreoffice_commands:
        if shutil.which(cmd) or os.path.exists(cmd):
            return cmd

    raise RuntimeError(
        '未找到 LibreOffice。请安装 LibreOffice：\n'
        'Windows: https://www.libreoffice.org/download/download/\n'
        'Linux: sudo apt install libreoffice\n'
        'macOS: brew install --cask libreoffice'
    )


def _convert_with_libreoffice(input_path: str, output_dir: str) -> str:
    """使用 LibreOffice 转换文档为 PDF"""
    cmd = _get_libreoffice_command()

    try:
        # 使用全局锁，确保同一时间只有一个 soffice 进程在运行
        with _libreoffice_lock:
            result = subprocess.run([cmd, '--headless', '--convert-to', 'pdf', '--outdir', output_dir, input_path], capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            raise RuntimeError(f'LibreOffice 转换失败: {result.stderr}')

        # 生成输出文件路径
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(output_dir, f'{base_name}.pdf')

        if not os.path.exists(output_path):
            raise RuntimeError(f'转换后的 PDF 文件未找到: {output_path}')

        return output_path

    except subprocess.TimeoutExpired:
        raise RuntimeError('LibreOffice 转换超时（30秒）')
    except Exception as e:
        import traceback

        traceback.print_exc()
        raise RuntimeError(f'LibreOffice 转换失败: {str(e)}')


def convert_office_to_pdf(file_bytes: bytes, original_filename: str) -> Tuple[bytes, str]:
    """
    使用 LibreOffice 将 Office 文档（doc/docx/ppt/pptx）转换为 PDF

    Args:
        file_bytes: 原始文件的字节内容
        original_filename: 原始文件名

    Returns:
        Tuple[bytes, str]: PDF 文件的字节内容和新文件名

    Raises:
        RuntimeError: 如果未安装 LibreOffice 或转换失败
    """
    file_ext = os.path.splitext(original_filename)[1].lower()
    # 如果已经是 PDF，直接返回
    if file_ext == '.pdf':
        return file_bytes, original_filename

    # 检查是否需要转换
    if file_ext not in ['.doc', '.docx', '.ppt', '.pptx']:
        return file_bytes, original_filename
    # 检查 LibreOffice 是否可用
    _get_libreoffice_command()
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_input_path = os.path.join(temp_dir, f'input{file_ext}')
        with open(temp_input_path, 'wb') as f:
            f.write(file_bytes)
        output_path = _convert_with_libreoffice(temp_input_path, temp_dir)
        with open(output_path, 'rb') as pdf_file:
            pdf_bytes = pdf_file.read()
        pdf_filename = os.path.splitext(original_filename)[0] + '.pdf'
        return pdf_bytes, pdf_filename


def convert_office_to_pdf_batch(file_name_bytes: List[Tuple[str, bytes]]) -> List[Tuple[str, bytes]]:
    """
    批量转换 Office 文档为 PDF，串行处理，保持文件顺序

    Args:
        file_name_bytes: 文件名和字节内容的列表

    Returns:
        List[Tuple[str, bytes]]: 转换后的文件名和字节内容列表（顺序与输入一致）
    """
    result: List[Tuple[str, bytes]] = []
    errors = []

    for filename, file_bytes in file_name_bytes:
        file_ext = os.path.splitext(filename)[1].lower()
        needs_convert = file_ext in ['.doc', '.docx', '.ppt', '.pptx']
        if not needs_convert:
            result.append((filename, file_bytes))
            continue

        try:
            converted_bytes, converted_filename = convert_office_to_pdf(file_bytes, filename)
            result.append((converted_filename, converted_bytes))
        except Exception as e:
            errors.append(f'{filename}: {str(e)}')

    if errors:
        raise RuntimeError('以下文件转换失败：\n' + '\n'.join(errors))

    return result

from configure import conf
from typing import Tuple
from markitdown import MarkItDown
from openai import OpenAI
from io import BytesIO


def document_to_markdown(file_bytes: bytes, vision_enabled: bool):
    client = OpenAI(base_url=conf.vision_model_base_url, api_key=conf.vision_model_api_key)
    if vision_enabled:
        md = MarkItDown(llm_client=client, llm_model='Qwen2.5-VL-32B-Instruct', llm_prompt='为这张图片撰写一段详细的说明文字。')
    else:
        md = MarkItDown(enable_plugins=False)
    result = md.convert(BytesIO(file_bytes))
    return result.text_content


def make_file_markdown(file_name_bytes: Tuple[str, bytes], vision_enabled: bool) -> dict:
    rt_json = {}
    file_name, file_bytes = file_name_bytes
    md_content = document_to_markdown(file_bytes, vision_enabled)
    rt_json['md_content'] = md_content
    rt_json['message'] = f'{file_name}解析完成'
    return rt_json

from configure import conf
from typing import Tuple, List
import tiktoken
from enum import StrEnum
from markitdown import MarkItDown
from openai import OpenAI
from io import BytesIO


class DocumentParseSplitType(StrEnum):
    FULL = 'FULL'
    SPLIT = 'SPLIT'
    NULL = 'NULL'
    OVERFLOW = 'OVERFLOW'


def tokenizer_len(text: str) -> int:
    tokenizer = tiktoken.get_encoding('o200k_base')
    return len(tokenizer.encode(text, disallowed_special=()))


def split_text_by_token(text: str, exist_token: int, max_token: int) -> str:
    if len(text.strip()) < 20:
        return DocumentParseSplitType.NULL, ''
    tokenizer = tiktoken.get_encoding('o200k_base')
    tokens = tokenizer.encode(text, disallowed_special=())
    if exist_token + len(tokens) <= max_token:
        return DocumentParseSplitType.FULL, text
    else:
        allowed_tokens = max_token - exist_token
        truncated_tokens = tokens[:allowed_tokens]
        if (i := tokenizer.decode(truncated_tokens)) and len(i.strip()) >= 20:
            return DocumentParseSplitType.SPLIT, i
        else:
            return DocumentParseSplitType.OVERFLOW, ''


def document_to_markdown(file_bytes: bytes, vision_enabled: bool):
    client = OpenAI(base_url=conf.vision_model_base_url, api_key=conf.vision_model_api_key)
    if vision_enabled:
        md = MarkItDown(llm_client=client, llm_model='Qwen2.5-VL-32B-Instruct', llm_prompt='为这张图片撰写一段详细的说明文字。')
    else:
        md = MarkItDown(enable_plugins=False)
    result = md.convert(BytesIO(file_bytes))
    return result.text_content


def make_files_markdown(files_name_bytes: List[Tuple[str, bytes]], vision_enabled: bool, max_token: int) -> dict:
    rt_json = {'status': 'go_on_upload', 'message': None, 'results': {}}
    null_docs = []
    split_docs = []
    overflow_docs = []
    accumulated_token = 0
    go_on_convert = True
    for file_name, file_bytes in files_name_bytes:
        if go_on_convert:
            md_content = document_to_markdown(file_bytes, vision_enabled)
            type_, text = split_text_by_token(md_content, accumulated_token, max_token)
        else:
            type_, text = DocumentParseSplitType.OVERFLOW, ''  # 已经溢出，停止解析
        if type_ in (DocumentParseSplitType.OVERFLOW, DocumentParseSplitType.SPLIT):  # 溢出了，停止解析
            go_on_convert = False
            rt_json['status'] = 'stop_upload'
        if text:
            rt_json['results'][file_name] = text
            accumulated_token += tokenizer_len(text)
        if type_ == DocumentParseSplitType.NULL:
            null_docs.append(file_name)
        elif type_ == DocumentParseSplitType.SPLIT:
            split_docs.append(file_name)
        elif type_ == DocumentParseSplitType.OVERFLOW:
            overflow_docs.append(file_name)
    null_out = f'存在无法解析内容的文件：{null_docs}；' if null_docs else ''
    split_out = f'内容过长被截断的文件：{split_docs}；' if split_docs else ''
    overflow_out = f'内容过长无法解析的文件：{overflow_docs};' if overflow_docs else ''
    rt_json['message'] = f'解析完成 {null_out}{split_out}{overflow_out}'
    return rt_json

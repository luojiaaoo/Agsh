import requests
from configure import conf
from typing import Tuple
import tiktoken
from enum import StrEnum


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


def make_files_markdown(file_name_bytes: Tuple[str, bytes], max_token: int = 10000):
    url = conf.mineru_api_url
    payload = {
        'lang_list': 'ch',
        'backend': 'pipeline',
        'parse_method': 'auto',
        'formula_enable': 'true',
        'table_enable': 'true',
        'return_md': 'true',
        'return_middle_json': 'false',
        'return_model_output': 'false',
        'return_content_list': 'false',
        'return_images': 'false',
        'response_format_zip': 'false',
        'start_page_id': '0',
        'end_page_id': '99999',
    }
    files = [('files', i) for i in file_name_bytes]
    headers = {'Accept': 'application/json'}
    response = requests.request('POST', url, headers=headers, data=payload, files=files)
    response.raise_for_status()
    rt_json = {'message': None, 'results': {}}
    null_docs = []
    split_docs = []
    overflow_docs = []
    accumulated_token = 0
    for doc_name, contents in response.json()['results'].items():
        md_content = contents['md_content']
        type_, text = split_text_by_token(md_content, accumulated_token, max_token)
        if text:
            rt_json['results'][doc_name] = text
            accumulated_token += tokenizer_len(text)
        if type_ == DocumentParseSplitType.NULL:
            null_docs.append(doc_name)
        elif type_ == DocumentParseSplitType.SPLIT:
            split_docs.append(doc_name)
        elif type_ == DocumentParseSplitType.OVERFLOW:
            overflow_docs.append(doc_name)
    null_out = f'存在无法解析内容的文件：{null_docs}；' if null_docs else ''
    split_out = f'内容过长被截断的文件：{split_docs}；' if split_docs else ''
    overflow_out = f'内容过长无法解析的文件：{overflow_docs};' if overflow_docs else ''
    rt_json['message'] = f'解析完成 {null_out}{split_out}{overflow_out}'
    return rt_json

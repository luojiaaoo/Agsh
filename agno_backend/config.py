from pydantic_settings import BaseSettings
from dotenv import load_dotenv


class Settings(BaseSettings):
    vllm_base_url: str
    vllm_api_key: str
    zai_base_url: str
    zai_api_key: str


class QingtianSettings(BaseSettings):
    qingtian_url: str
    qingtian_web_scrape_api_key: str
    qingtian_volcano_search_api_key: str
    qingtian_bing_search_api_key: str


load_dotenv('.env')

settings = Settings()
qingtian_settings = QingtianSettings()

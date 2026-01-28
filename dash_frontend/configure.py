import tomllib
import os


class Config:
    def __init__(self, toml_filepath):
        with open(toml_filepath, 'rb') as config_file:
            self.config = tomllib.load(config_file)

    @property
    def host(self):
        return self.config['config']['host']

    @property
    def port(self):
        return self.config['config']['port']

    @property
    def is_launch_prod(self):
        return self.config['config']['launch_mode'] == 'prod'

    @property
    def app_title(self):
        return self.config['config']['app_title']

    ##### 日志配置
    @property
    def log_filepath(self):
        t = self.config['config']['log_filepath']
        os.makedirs(os.path.dirname(t), exist_ok=True)
        return t

    @property
    def log_level(self):
        return self.config['config']['log_level']

    @property
    def agno_agentos_url(self):
        return self.config['config']['agno_agentos_url']

    @property
    def agno_id(self):
        return self.config['config']['agno_id']
    
    @property
    def agno_type(self):
        return self.config['config']['agno_type']
    
    @property
    def agno_agentos_jwt_secret(self):
        return self.config['config']['agno_agentos_jwt_secret']
    
    # 文档解析接口
    @property
    def mineru_api_url(self):
        return self.config['document']['mineru_api_url']


conf = Config('../config.toml')

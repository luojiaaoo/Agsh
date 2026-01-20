from agno.os.middleware import JWTMiddleware
from fastapi import Request
from yarl import URL


class JWTMiddlewareWithExclusion(JWTMiddleware):
    def __init__(self, app, exclude_urls: list[str], **kwargs):
        super().__init__(app, **kwargs)
        self.exclude_urls = exclude_urls  # 完整 URL 列表

    async def dispatch(self, request: Request, call_next):
        url = URL(str(request.headers.get("origin")))
        host_with_scheme = f'{url.scheme}://{url.host}'
        if host_with_scheme in self.exclude_urls:
            # 如果 URL 在排除列表中，直接跳过验证
            return await call_next(request)
        # 否则执行原来的 JWT 验证逻辑
        return await super().dispatch(request, call_next)

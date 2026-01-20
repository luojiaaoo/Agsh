from datetime import datetime, timedelta, timezone
from configure import conf
import jwt


def gen_access_token(user_id, session_id):
    to_encode = {
        'iss': conf.app_title,
        'sub': user_id,
        'iat': datetime.now(timezone.utc),
        'exp': datetime.now(timezone.utc) + timedelta(minutes=15),  # 15分钟有效期
        'session_id': session_id,
    }
    return jwt.encode(to_encode, conf.agno_agentos_jwt_secret, algorithm='HS256')

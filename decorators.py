from fastapi import HTTPException
from functools import wraps
def require_role(*roles):
    """
    Декоратор для ограничения доступа к эндпоинту по ролям.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            token_data = kwargs.get('token_data')
            if token_data['role'] not in roles:
                raise HTTPException(status_code=403, detail='Недостаточно прав')
            return await func(*args, **kwargs)
        return wrapper
    return decorator

import jwt
from enum import Enum
from .single import SingletonMeta
from fastapi import HTTPException,Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import settings
from datetime import datetime
from starlette.status import HTTP_401_UNAUTHORIZED,HTTP_403_FORBIDDEN

class TokenTypeEnum(Enum):
    ACCESS_TOKEN = 1
    REFRESH_TOKEN = 2


class AuthHandler(metaclass=SingletonMeta):
    secret = settings.JWT_SECRET_KEY
    security = HTTPBearer()

    def _encode_token(self, user_id: int, type: TokenTypeEnum):
        payload = dict(
            iss=user_id,
            sub=int(type.value)
        )
        to_encode = payload.copy()
        if type == TokenTypeEnum.ACCESS_TOKEN:
            exp = datetime.now() + settings.JWT_ACCESS_TOKEN_EXPIRES
        else:
            exp = datetime.now() + settings.JWT_REFRESH_TOKEN_EXPIRES
        to_encode.update({"exp": int(exp.timestamp())})
        return jwt.encode(to_encode, self.secret, algorithm='HS256')

    def encode_login_token(self, user_id: int):
        access_token = self._encode_token(user_id, TokenTypeEnum.ACCESS_TOKEN)
        refresh_token = self._encode_token(user_id, TokenTypeEnum.REFRESH_TOKEN)
        login_token = dict(
            access_token=f"{access_token}",
            refresh_token=f"{refresh_token}"
        )
        return login_token

    def encode_update_token(self, user_id:int):
        access_token = self._encode_token(user_id, TokenTypeEnum.ACCESS_TOKEN)
        update_token = dict(
            access_token=f"{access_token}"
        )
        return update_token

    def decode_access_token(self,token):
        try:
            payload=jwt.decode(token,self.secret,algorithms=["HS256"])
            if payload['sub']!=int(TokenTypeEnum.ACCESS_TOKEN.value):
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail='Token类型错误！')
            return payload['iss']
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail='Access Token已过期！')
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail='Access Token不可用！')

    def decode_refresh_token(self, token):
        # REFRESH TOKEN：不可用（过期，或有问题），都用401错误
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            if payload['sub'] != int(TokenTypeEnum.REFRESH_TOKEN.value):
                raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail='Token类型错误！')
            return payload['iss']
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail='Refresh Token已过期！')
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail='Refresh Token不可用！')

    def auth_access_dependency(self,auth:HTTPAuthorizationCredentials = Security(security)):
        return self.decode_access_token(auth.credentials)

    def auth_refresh_dependency(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_refresh_token(auth.credentials)
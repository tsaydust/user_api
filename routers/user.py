from fastapi import APIRouter, Depends, UploadFile, status
import string
import random
from utils.alysms import AliyunSMSSender
from schemas.response import ResultModel, LoginedModel, UpdatedAvatarModel, UserModel
from schemas.request import LoginModel, UpdateUsernameModel, UpdatePasswordModel
from utils.cache import SecRedis
from fastapi.exceptions import HTTPException
from services.user import UserServiceClient
from utils.auth import AuthHandler
from utils.alyoss import oss_upload_image

router = APIRouter(prefix='/user', tags=['user'])
sms_sender = AliyunSMSSender()
sec_redis = SecRedis()
user_service_client = UserServiceClient()
auth_handler = AuthHandler()


@router.get('/smscode/{mobile}', response_model=ResultModel)
async def get_smscode(mobile: str):
    code = "".join(random.sample(string.digits, 4))
    await sms_sender.send_code(mobile, code)
    await sec_redis.set_sms_code(mobile, code)
    print('code:', code)
    return ResultModel()


@router.post('/login', response_model=LoginedModel)
async def login(data: LoginModel):
    mobile = data.mobile
    code = data.code
    cache_code = await sec_redis.get_sms_code(mobile)
    if code != cache_code:
        raise HTTPException(status_code=400, detail="验证码错误！")

    user = await user_service_client.get_or_create_user_by_mobile(mobile=mobile)
    tokens = auth_handler.encode_login_token(user_id=user.id)
    await sec_redis.set_refresh_token(user.id, tokens['refresh_token'])
    return {
        'user': user,
        'access_token': tokens['access_token'],
        'refresh_token': tokens['refresh_token']
    }


@router.get('/access/token')
async def access_token_view(user_id: int = Depends(auth_handler.auth_access_dependency)):
    return {"detail": "access_token验证成功！", 'user_id': user_id}


@router.get('/refresh/token')
async def refresh_token_view(user_id: int = Depends(auth_handler.auth_refresh_dependency)):
    # 调用/user/refresh/token，如果refresh token没有过期
    # 那么就重新返回一个access token
    access_token = auth_handler.encode_update_token(user_id)
    return access_token


@router.post('/logout', response_model=ResultModel)
async def logout(user_id: int = Depends(auth_handler.auth_access_dependency)):
    await sec_redis.delete_refresh_token(user_id)
    return ResultModel()


@router.put('/update/username', response_model=ResultModel)
async def update_username(data: UpdateUsernameModel, user_id: int = Depends(auth_handler.auth_access_dependency)):
    username = data.username
    await user_service_client.update_username(user_id, username)
    return ResultModel()


@router.put('/update/password', response_model=ResultModel)
async def update_password(data: UpdatePasswordModel, user_id: int = Depends(auth_handler.auth_access_dependency)):
    password = data.password
    await user_service_client.update_password(user_id, password)
    return ResultModel()


@router.post('/update/avatar', response_model=UpdatedAvatarModel)
async def update_avatar(file: UploadFile, user_id: int = Depends(auth_handler.auth_access_dependency)):
    file_url = await oss_upload_image(file)
    if file_url:
        await user_service_client.update_avatar(user_id, file_url)
        return {'file_url': file_url}
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='头像上传失败！')


@router.get('/mine', response_model=UserModel)
async def get_mine_info(user_id: int = Depends(auth_handler.auth_access_dependency)):
    user = await user_service_client.get_user_by_id(user_id)
    return user

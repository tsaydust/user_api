import grpc
from utils.single import SingletonMeta
from services.protos import user_pb2, user_pb2_grpc
from .decorators import grpc_error_handler
from utils.consul_services import CustomConsul
from loguru import logger
custom_consul = CustomConsul()

class UserStub:
    def __init__(self):
        # self.ip = '127.0.0.1:5001'
        pass

    @property
    def user_service_address(self):
        ip,port = custom_consul.get_one_address()
        logger.info(f"获取到的地址：{ip}:{port}")
        return f"{ip}:{port}"

    async def __aenter__(self):
        self.channel = grpc.aio.insecure_channel(self.user_service_address)
        stub = user_pb2_grpc.UserStub(self.channel)
        return stub

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.channel.close()


class UserServiceClient(metaclass=SingletonMeta):
    @grpc_error_handler
    async def get_or_create_user_by_mobile(self, mobile: str):
        async with UserStub() as stub:
            request = user_pb2.GetUserByMobileRequest(mobile=mobile)
            response = await stub.GetOrCreateUserByMobile(request)
            return response.user

    @grpc_error_handler
    async def update_password(self, id: int, password: str):
        async with UserStub() as stub:
            request = user_pb2.UpdatePasswordRequest(id=id, password=password)
            await stub.UpdatePassword(request)

    @grpc_error_handler
    async def update_username(self, id: int, username: str):
        async with UserStub() as stub:
            request = user_pb2.UpdateUsernameRequest(id=id, username=username)
            await stub.UpdateUsername(request)

    @grpc_error_handler
    async def update_avatar(self, user_id: int, avatar: str):
        async with UserStub() as stub:
            request = user_pb2.UpdateAvatarRequest(id=user_id, avatar=avatar)
            await stub.UpdateAvatar(request)

    @grpc_error_handler
    async def get_user_by_mobile(self, mobile: str):
        async with UserStub() as stub:
            request = user_pb2.GetUserByMobileRequest(mobile=mobile)
            response = await stub.GetUserByMobile(request)
            return response.user

    @grpc_error_handler
    async def get_user_list(self, page: int = 1, size: int = 10):
        async with UserStub() as stub:
            request = user_pb2.GetUserPageRequest(page=page, size=size)
            response = await stub.GetUserList(request)
            return response.users

    @grpc_error_handler
    async def verify_user(self, mobile: str, password: str):
        async with UserStub() as stub:
            request = user_pb2.VerifyUserRequest(mobile=mobile, password=password)
            response = await stub.VerifyUser(request)
            return response.user

    @grpc_error_handler
    async def get_user_by_id(self, user_id: int):
        async with UserStub() as stub:
            request = user_pb2.GetUserByIdRequest(id=user_id)
            response = await stub.GetUserById(request)
            return response.user

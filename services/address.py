from utils.single import SingletonMeta
from .decorators import grpc_error_handler
from services.protos import address_pb2, address_pb2_grpc
import grpc
from utils.consul_services import CustomConsul

custom_consul = CustomConsul()

class AddressStub:
    def __init__(self):
        # self.ip = '127.0.0.1:5001'
        pass

    @property
    def user_service_address(self):
        ip,port = custom_consul.get_one_address()
        return f"{ip}:{port}"

    async def __aenter__(self):
        self.channel = grpc.aio.insecure_channel(self.user_service_address)
        stub = address_pb2_grpc.AddressStub(self.channel)
        return stub

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.channel.close()


class AddressServiceClient(metaclass=SingletonMeta):

    @grpc_error_handler
    async def create_address(
            self,
            user_id: int,
            realname: str,
            mobile: str,
            region: str,
            detail: str
    ):
        async with AddressStub() as stub:
            request = address_pb2.CreateAddressRequest(
                user_id=user_id,
                realname=realname,
                mobile=mobile,
                region=region,
                detail=detail
            )
            response = await stub.CreateAddress(request)
            return response.address

    @grpc_error_handler
    async def update_address(
            self,
            id: str,
            realname: str,
            mobile: str,
            region: str,
            detail: str,
            user_id: int,
    ):
        async with AddressStub() as stub:
            request = address_pb2.UpdateAddressRequest(
                id=id,
                user_id=user_id,
                realname=realname,
                mobile=mobile,
                region=region,
                detail=detail
            )
            await stub.UpdateAddress(request)

    @grpc_error_handler
    async def delete_address(self, user_id: int, id: str):
        async with AddressStub() as stub:
            request = address_pb2.DeleteAddressRequest(user_id=user_id, id=id)
            await stub.DeleteAddress(request)

    @grpc_error_handler
    async def get_address_by_id(self, user_id: int, id: str):
        async with AddressStub() as stub:
            request = address_pb2.AddressIdRequest(user_id=user_id, id=id)
            response = await stub.GetAddressById(request)
            return response.address

    @grpc_error_handler
    async def get_address_list(self, user_id: int, page: int=1, size: int=10):
        async with AddressStub() as stub:
            request = address_pb2.AddressListRequest(user_id=user_id, page=page, size=size)
            response = await stub.GetAddressList(request)
            return response.addresses

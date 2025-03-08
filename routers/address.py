from utils.auth import AuthHandler
from fastapi import APIRouter, Depends
from services.address import AddressServiceClient
from schemas.request import CreateAddressModel, DeleteAddressModel, UpdateAddressModel, GetAddressListModel
from schemas.response import AddressModel, AddressListModel, ResultModel

address_service_client = AddressServiceClient()
auth_handler = AuthHandler()
router = APIRouter(prefix="/address", tags=["address"])


@router.post(path="/create", response_model=AddressModel)
async def create_address(data: CreateAddressModel, user_id: int = Depends(auth_handler.auth_access_dependency)):
    realname = data.realname
    mobile = data.mobile
    region = data.region
    detail = data.detail
    address = await address_service_client.create_address(
        user_id=user_id,
        realname=realname,
        mobile=mobile,
        region=region,
        detail=detail
    )
    return address


@router.get(path='/detail/{id}', response_model=AddressModel)
async def get_address(id: str, user_id: int = Depends(auth_handler.auth_access_dependency)):
    address = await address_service_client.get_address_by_id(user_id=user_id, id=id)
    return address


@router.get(path="/list", response_model=AddressListModel)
async def get_address_list(page: int = 1, size: int = 10, user_id: int = Depends(auth_handler.auth_access_dependency)):
    addresses = await address_service_client.get_address_list(page=page, size=size, user_id=user_id)
    return {"addresses": addresses}


@router.delete('/delete', response_model=ResultModel)
async def delete_address(data: DeleteAddressModel, user_id: int=Depends(auth_handler.auth_access_dependency)):
    await address_service_client.delete_address(user_id, data.id)
    return ResultModel()


@router.put('/update', response_model=ResultModel)
async def update_address(data: UpdateAddressModel, user_id: int=Depends(auth_handler.auth_access_dependency)):
    await address_service_client.update_address(
        id=data.id,
        realname=data.realname,
        mobile=data.mobile,
        region=data.region,
        detail=data.detail,
        user_id=user_id,
    )
    return ResultModel()

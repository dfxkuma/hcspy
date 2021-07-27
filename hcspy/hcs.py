import aiohttp
from typing import Optional, List

from .http import HTTPClient, Route
from .model import School
from .errors import AuthorizeError
from .user import User


class HCSClient:
    def __init__(
        self,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        if not session:
            session = aiohttp.ClientSession()
        self._http_client = HTTPClient(session=session)

    @property
    def endpoint(self) -> str:
        return Route.BASE

    async def search_school(self, name: str) -> List[School]:
        response = await self._http_client.search_school(name=name)
        return [
            School(
                school["orgCode"],
                school["kraOrgNm"],
                school["engOrgNm"],
                school["lctnScNm"],
                school["addres"],
                school["atptOfcdcConctUrl"],
            )
            for school in response
        ]

    async def get_token(self, school: School, name: str, birthday: str) -> str:
        response = await self._http_client.get_token(
            endpoint=school.endpoint, code=school.id, name=name, birthday=birthday
        )
        return response["token"]

    async def transkey(self, school: School, token: str, password: str):
        return await self._http_client.transkey(
            endpoint=self.endpoint, token=token, password=password
        )

    async def login(
        self, name: str, school_name: str, birthday: str, password: str
    ):
        _school = await self.search_school(name=school_name)[0]
        _token = await self.get_token(school=_school, name=name, birthday=birthday)
        if not await self._http_client.password_exist(
            endpoint=_school.endpoint, token=_token.get("token")
        ):
            raise AuthorizeError("설정된 비밀번호가 없습니다.")
        _token = await self._http_client.transkey(
            endpoint=self.endpoint, token=_token.get("token"), password=password
        )
        _group = await self._http_client.get_group(
            endpoint=_school.endpoint, token=_token.get("token")
        )
        return [
            User().from_dict(
                group_data=i,
                login_data=await self._http_client.get_user(
                    endpoint=_school.endpoint,
                    code=_school.id,
                    user_id=i.get("userPNo"),
                ),
                agreementRequired=_token.get("agreementRequired"),
                birthday=birthday,
                school=_school,
                password=password,
            )
            for i in _group
        ]

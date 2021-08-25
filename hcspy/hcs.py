import aiohttp
from typing import Optional, List

from .http import HTTPClient, Route
from .model import School
from .errors import AuthorizeError
from .user import User


class HCSClient:
    """ "https://hcs.eduro.go.kr api 레퍼 Client 입니다."""

    def __init__(
        self,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        """Client를 http client와 함께 생성합니다

        Parameters
        ----------
        session: Optional[aiohttp.ClientSession]
            세 세션을 생성하지 않고 기존 세션을 사용합니다.
        """
        if not session:
            session = aiohttp.ClientSession()
        self._http_client = HTTPClient(session=session)

    @property
    def endpoint(self) -> str:
        return Route.BASE

    async def search_school(
        self, name: str, level: Optional[str] = None, area: Optional[str] = None
    ) -> List[School]:
        """학교를 검색합니다

        Parameters
        ----------
        name: str
            검색할 학교 이름이나 키워드를 입력합니다
        level: Optional[str]
            학교 유형을 선택합니다.
        area: Optional[str]
            학교 지역을 선택합니다.
        """
        response = await self._http_client.search_school(
            name=name, level=level, area=area
        )
        return [
            School(
                school["orgCode"],
                school["kraOrgNm"],
                school["engOrgNm"],
                school["lctnScNm"],
                school["addres"],
                "https://" + school["atptOfcdcConctUrl"],
            )
            for school in response
        ]

    async def get_token(self, school: School, name: str, birthday: str) -> str:
        """
        api를 사용하기 위한 토큰을 발급합니다.

        Parameters
        ----------
        school: School
            토큰을 발급할 학교를 입력합니다.
        name: str
            사용자 이름을 입력합니다.
        birthday: str
            본인의 생년월일 8자리를 입력합니다.
        """
        response = await self._http_client.get_token(
            endpoint=school.endpoint, code=school.id, name=name, birthday=birthday
        )
        return response

    async def transkey(self, token: str, password: str):
        """
        보안 키페드를 생성해 비밀번호를 입력합니다.

        Parameters
        ----------
        token: str
            사용자 토큰을 입력합니다.
        password: str
            사용자 비밀번호 4자리를 입력합니다.
        """
        return await self._http_client.login(
            endpoint=self.endpoint, token=token, password=password
        )

    async def login_fast(
        self, name: str, school_name: str, birthday: str, password: str
    ):
        """
        기본 정보를 빠르게 입력하여 로그인을 진행합니다.

        Parameters
        ----------
        name: str
            사용자 이름을 입력합니다
        school_name: str
            학교 이름을 입력합니다.검색 결과의 첫번째 학교로 지정합니다.
        birthday: str
            사용자 생년월일 8자리를 입력합니다.
        password: str
            사용자 비밀번호 4자리를 입력합니다.
        """
        schools = await self.search_school(name=school_name)
        _school = schools[0]
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

    async def login(self, school: School, name: str, birthday: str, password: str):
        """자가진단 사이트에 로그인을 진행합니다.

        Parameters
        ----------
        school: School
            사용자의 학교 객체를 입력합니다.
        name: str
            사용자의 이름을 입력합니다.
        birthday: str
            사용자 생년월일 8자리를 입력합니다.
        password: str
            사용자 비밀번호 4자리를 입력합니다.
        """
        _token = await self.get_token(school=school, name=name, birthday=birthday)
        if not await self._http_client.password_exist(
            endpoint=school.endpoint, token=_token.get("token")
        ):
            raise AuthorizeError("설정된 비밀번호가 없습니다.")
        _token = await self._http_client.login(
            endpoint=school.endpoint, token=_token.get("token"), password=password
        )
        _group = await self._http_client.get_group(
            endpoint=school.endpoint, token=_token
        )
        return [
            User().from_dict(
                group_data=i,
                login_data=await self._http_client.get_user(
                    endpoint=school.endpoint,
                    code=school.id,
                    user_id=i.get("userPNo"),
                    token=_token,
                ),
                agreementRequired=i.get("agreementRequired"),
                birthday=birthday,
                school=school,
                password=password,
                http_session=self._http_client,
            )
            for i in _group
        ]

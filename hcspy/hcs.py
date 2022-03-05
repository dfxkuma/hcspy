from typing import List, Optional, Any

import aiohttp
import asyncio

from .errors import AuthorizeError
from .http import HTTPClient, Route
from .model import School
from .user import User
from .utils import duplicate, duplicated


@duplicated
class HCSClient:
    """ "https://hcs.eduro.go.kr api 레퍼 Client 입니다."""

    __slots__ = "_http_client"

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

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def close(self):
        await self._http_client.close()

    @duplicate("search_organization", "search_university")
    async def search_school(
        self,
        search_type: str,
        name: str,
        level: Optional[str] = None,
        area: Optional[str] = None,
    ) -> List[School]:
        """학교를 검색합니다

        Parameters
        ----------
        search_type: str
            기관 타입을 선택합니다.
        name: str
            검색할 학교 이름이나 키워드를 입력합니다
        level: Optional[str]
            학교 유형을 선택합니다.
        area: Optional[str]
            학교 지역을 선택합니다.
        """
        response = await self._http_client.search_school(
            name=name,
            level=level,
            area=area,
            search_type=search_type,
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

    async def find_user(
        self, school: School, name: str, birthday: str, school_type: str = "school"
    ) -> Any:
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
        school_type: str
            기관의 종류를 입력합니다.
        """
        response = await self._http_client.find_user(
            endpoint=school.endpoint,
            code=school.id,
            name=name,
            birthday=birthday,
            school_type=school_type,
        )
        return response

    @duplicate("login_with_token")
    async def token_login(
        self, school: School, token: str, password: str
    ) -> List[User]:
        """
        자가진단 사이트에 유저 토큰으로 로그인합니다.
        Parameters
        ----------
        school: School
            사용자의 학교 객체를 입력합니다.
        token: str
            유저 토큰을 입력합니다.
        password: str
            사용자 비밀번호 4자리를 입력합니다.
        """
        user_token = await self._http_client.use_security_keypad(
            endpoint=school.endpoint,
            token=token,
            password=password,
        )
        if user_token.get("isError") is True and user_token.get("errorCode") == 1001:
            failed_count = user_token["data"].get("failCnt")
            raise AuthorizeError(f"비밀번호가 다릅니다 (시도 횟수: {failed_count}/5)")
        group = await self._http_client.get_group(
            endpoint=school.endpoint, token=user_token["token"]
        )
        return [
            User(
                user_data=await self._http_client.get_user(
                    endpoint=school.endpoint,
                    code=school.id,
                    user_id=user.get("userPNo"),
                    token=user_token["token"],
                ),
                group_data=user,
                info_data={
                    "school": school,
                    "birthday": None,
                    "password": int(password),
                    "agreement_required": True
                    if user_token.get("pInfAgrmYn") == "Y"
                    else False,
                },
                state=self._http_client,
                token=user_token["token"],
            )
            for user in group
        ]

    @duplicate("get_group")
    async def login(
        self,
        school: School,
        name: str,
        birthday: str,
        password: str,
        school_type: str = "school",
    ) -> List[User]:
        """자가진단 사이트에 로그인을 진행합니다.

        Parameters
        ----------
        school: School
            사용자의 학교 객체를 입력합니다.
        name: str
            사용자의 이름을 입력합니다.
        birthday: str
            사용자 생년월일 6자리를 입력합니다.
        password: str
            사용자 비밀번호 4자리를 입력합니다.
        school_type: str
            기관 타입을 입력합니다.
        """
        user_data = await self.find_user(
            school=school, name=name, birthday=birthday, school_type=school_type
        )
        if not user_data.get("pInfAgrmYn") == "N":
            await self._http_client.update_agreement(
                endpoint=school.endpoint, token=user_data.get("token")
            )
        if not await self._http_client.password_exist(
            endpoint=school.endpoint,
            token=user_data.get("token"),
        ):
            raise AuthorizeError("설정된 비밀번호가 없습니다. 자가진단 사이트에서 초기 비밀번호를 설정하세요.")
        user_token = await self._http_client.use_security_keypad(
            endpoint=school.endpoint, token=user_data.get("token"), password=password
        )
        if user_token.get("isError") is True and user_token.get("errorCode") == 1001:
            failed_count = user_token["data"].get("failCnt")
            raise AuthorizeError(f"비밀번호가 다릅니다 (시도 횟수: {failed_count}/5)")
        group = await self._http_client.get_group(
            endpoint=school.endpoint, token=user_token["token"]
        )
        return [
            User(
                user_data=await self._http_client.get_user(
                    endpoint=school.endpoint,
                    code=school.id,
                    user_id=user.get("userPNo"),
                    token=user_token["token"],
                ),
                group_data=user,
                info_data={
                    "school": school,
                    "birthday": int(birthday),
                    "password": int(password),
                    "agreement_required": True
                    if user_data.get("pInfAgrmYn") == "Y"
                    else False,
                },
                state=self._http_client,
                token=user_token["token"],
            )
            for user in group
        ]

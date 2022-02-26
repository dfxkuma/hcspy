import contextlib
from json import dumps
from typing import Any, ClassVar, Dict, Literal, Optional, Union

import aiohttp

from .data import school_areas, school_levels
from .errors import AuthorizeError, HTTPException, PasswordLengthError, SchoolNotFound
from .keypad import KeyPad
from .transkey import mTransKey
from .utils import encrypt_login, multi_finder, url_create_with


def content_type(response: Any) -> Any:
    with contextlib.suppress(Exception):
        return response.json()
    return response.text()


class Route:
    BASE: ClassVar[str] = "https://hcs.eduro.go.kr/v2"

    def __init__(self, method: Literal["GET", "POST"], path: str) -> None:
        self.path: str = path
        self.method: str = method
        url: str = self.BASE + self.path
        self.url: str = url

    @property
    def endpoint(self) -> str:
        return self.BASE

    @endpoint.setter
    def endpoint(self, value: str) -> None:
        self.url = value + self.path


class HTTPRequest:
    def __init__(
        self,
        session: aiohttp.ClientSession = aiohttp.ClientSession(),
    ):
        """새 http 세션을 생성합니다.

        Parameters
        ----------
        session: Optional[aiohttp.ClientSession]
            기존 세션을 생성합니다.세션이 없을 경우 요청할 때 새로 생성합니다.
        """
        self.session: aiohttp.ClientSession = session
        self._cookie_jar = aiohttp.CookieJar()

    @staticmethod
    def set_header(header: Dict[str, str]) -> Dict[str, str]:
        """자가진단 사이트에 필요한 기본 헤더를 생성합니다.

        Parameters
        ----------
        header: Dict[str, str]
            기존 해더 dict 객체를 입력합니다.
        """
        header["Accept"] = "application/json, text/plain, */*"
        header["Accept-Encoding"] = "gzip, deflate, br"
        header[
            "Accept-Language"
        ] = "en-GB,en;q=0.9,ko-KR;q=0.8,ko;q=0.7,ja-JP;q=0.6,ja;q=0.5,zh-TW;q=0.4,zh;q=0.3,en-US;q=0.2"
        header["Cache-Control"] = "no-cache"
        header["Connection"] = "keep-alive"
        header["Origin"] = "https://hcs.eduro.go.kr"
        header["Pragma"] = "no-cache"
        header["Referer"] = "https://hcs.eduro.go.kr/"
        header["Sec-Fetch-Dest"] = "empty"
        header["Sec-Fetch-Mode"] = "cors"
        header["Sec-Fetch-Site"] = "same-site"
        header["User-Agent"] = (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/13.0.3 Mobile/15E148 Safari/604.1 "
        )
        header["X-Requested-With"] = "XMLHttpRequest"
        return header

    async def request(self, route: Route, **kwargs: Any) -> Any:
        """
        새 http 요청을 실행합니다.

        Parameters
        ----------
        route: Route
            url을 입력합니다.

        """
        method = route.method
        url = route.url
        headers: Dict[str, Any] = kwargs.get("headers", {})

        headers = self.set_header(headers)

        if "json" in kwargs:
            _content_type = "x-www-form-urlencoded" if method == "GET" else "json"
            headers["Content-Type"] = f"application/{_content_type};charset=UTF-8"
        if self._cookie_jar:
            kwargs["cookie_jar"] = self._cookie_jar

        async with self.session.request(method, url, **kwargs) as response:
            data = await content_type(response)
        if response.status != 200:
            raise HTTPException(response.status, data)

        return data


class HTTPClient:
    __slots__ = ("_session", "_http")

    def __init__(
        self, session: aiohttp.ClientSession = aiohttp.ClientSession()
    ) -> None:
        """새 http client를 세션과 함께 생성합니다"""
        self._session = session
        self._http = HTTPRequest(session=self._session)

    @property
    def http_session(self) -> HTTPRequest:
        return self._http

    async def search_school(
        self,
        search_type: str,
        name: str,
        level: Optional[str] = None,
        area: Optional[str] = None,
    ) -> Any:
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
        if search_type == "school":
            level = multi_finder(data=school_levels, keyword=level, prefix="level")
            area = multi_finder(data=school_areas, keyword=area, prefix="area")
            route = url_create_with(
                "/searchSchool",
                orgName=name,
                lctnScCode=area,
                schulCrseScCod=level,
                loginType=search_type,
            )
        elif search_type == "univ":
            route = url_create_with(
                "/searchSchool",
                orgName=name,
                loginType=search_type,
            )
        else:
            raise NotImplemented(f"{search_type} 유형 기관은 지원하지 않습니다.")
        response = await self._http.request(Route("GET", route))
        if len(response["schulList"]) == 0:
            raise SchoolNotFound(f"{name} 학교를 찾지 못했습니다.")
        return response["schulList"]

    async def find_user(
        self,
        endpoint: str,
        code: str,
        name: str,
        birthday: str,
        school_type: str = "school",
    ) -> Any:
        """
        api를 사용하기 위한 토큰을 발급합니다.

        Parameters
        ----------
        endpoint: str
            학교 api 주소를 입력합니다.
        code: str
            학교 코드를 입력합니다.
        name: str
            사용자 이름을 입력합니다.
        birthday: str
            본인의 생년월일 6자리를 입력합니다.
        school_type: str
            기관 타입을 선택합니다.
        """
        route = Route("POST", "/v2/findUser")
        route.endpoint = endpoint
        try:
            response = await self._http.request(
                route,
                json={
                    "birthday": encrypt_login(birthday),
                    "loginType": school_type,
                    "name": encrypt_login(name),
                    "orgCode": code,
                    "stdntPHo": None,
                },
            )
            return response
        except HTTPException as e:
            if e.code == 500:
                raise AuthorizeError("입력한 정보가 일치하지 않습니다.")

    async def update_agreement(self, endpoint: str, token: str) -> Any:
        """
        자가진단 이용약관에 동의합니다.

        Parameters
        ----------
        endpoint: str
            학교 api 주소를 입력합니다.
        token: str
            사용자 토큰을 입력합니다.
        """
        route = Route("POST", "/v2/updatePInfAgrmYn")
        route.endpoint = endpoint
        response = await self._http.request(route, headers={"Authorization": token})
        return response

    async def password_exist(self, endpoint: str, token: str) -> bool:
        """
        비밀번호를 설정했는지 확인합니다.

        Parameters
        ----------
        endpoint: str
            학교 api 주소를 입력합니다.
        token: str
            사용자 토큰을 입력합니다.
        """
        route = Route("POST", "/v2/hasPassword")
        route.endpoint = endpoint
        response = await self._http.request(route, headers={"Authorization": token})
        return bool(response)

    async def register_password(self, endpoint: str, token: str, password: str) -> Any:
        """
        비밀번호를 설정했는지 확인합니다.

        Parameters
        ----------
        endpoint: str
            학교 api 주소를 입력합니다.
        token: str
            사용자 토큰을 입력합니다.
        password: str
            설정할 비밀번호 4자리를 입력합니다.
        """
        if len(password) != 4:
            raise PasswordLengthError("비밀번호는 숫자 4자리만 허용됩니다.")
        data = {"deviceUuid": "", "password": encrypt_login(password)}
        route = Route("POST", "/v2/registerPassword")
        route.endpoint = endpoint
        response = await self._http.request(
            route, json=data, headers={"Authorization": token}
        )
        return response

    async def check_survey(
        self,
        endpoint: str,
        token: str,
        log_name: Optional[str] = None,
    ) -> Any:
        """자가진단을 모두 증상 없음으로 체크합니다.

        Parameters
        ----------
        endpoint: str
            학교 api 주소를 입력합니다.
        token: str
            사용자 토큰을 입력합니다.

        log_name: Optional[str]
            자가진단 로그 이름을 지정합니다.
        """
        route = Route("POST", "/registerServey")
        route.endpoint = endpoint
        data = {
            "rspns01": "1",
            "rspns02": "1",
            "rspns03": None,
            "rspns04": None,
            "rspns05": None,
            "rspns06": None,
            "rspns07": "0",
            "rspns08": "0",
            "rspns09": "0",
            "rspns10": None,
            "rspns11": None,
            "rspns12": None,
            "rspns13": None,
            "rspns14": None,
            "rspns15": None,
            "rspns00": "Y",
            "deviceUuid": "",
            "upperToken": token,
            "upperUserNameEncpt": log_name,
        }
        response = await self._http.request(
            route, json=data, headers={"Authorization": token}
        )
        return response

    async def change_password(
        self, endpoint: str, token: str, password: str, new_password: str
    ) -> Any:
        """자가진단 비밀번호를 변경합니다

        Parameters
        ----------
        endpoint: str
            학교 api 주소를 입력합니다.
        token: str
            사용자 토큰을 입력합니다.
        password: str
            기존 비밀번호 4자리를 입력합니다.
        new_password: str
            새로운 비밀번호 4자리를 입력합니다.
        """
        if len(password) != 4 or len(new_password) != 4:
            raise PasswordLengthError("비밀번호는 숫자 4자리만 허용됩니다.")
        route = Route("POST", "/v2/changePassword")
        route.endpoint = endpoint
        data = {
            "password": encrypt_login(password),
            "newPassword": encrypt_login(new_password),
        }
        response = await self._http.request(
            route, json=data, headers={"Authorization": token}
        )
        return response

    async def use_security_keypad(
        self, endpoint: str, token: str, password: str
    ) -> Any:
        """보안 키보드를 사용해 서버에 데이터를 요청합니다

        Parameters
        ----------
        endpoint: str
            학교 api 주소를 입력합니다.
        token: str
            사용자 토큰을 입력합니다.
        password: str
            사용자 비밀번호 4자리를 입력합니다.
        """
        mtk = mTransKey("https://hcs.eduro.go.kr/transkeyServlet")
        keypad: KeyPad = await mtk.new_keypad(
            "number", "password", "password", "password"
        )
        encrypted: str = keypad.encrypt_password(password)
        hm: str = mtk.hmac_digest(encrypted.encode())
        route = Route("POST", "/v2/validatePassword")
        route.endpoint = endpoint
        data: Dict[str, Any] = {
            "password": dumps(
                {
                    "raon": [
                        {
                            "id": "password",
                            "enc": encrypted,
                            "hmac": hm,
                            "keyboardType": "number",
                            "keyIndex": mtk.keyIndex,
                            "fieldType": "password",
                            "seedKey": mtk.crypto.get_encrypted_key(),
                            "initTime": mtk.initTime,
                            "ExE2E": "false",
                        }
                    ]
                },
            ),
            "deviceUuid": "",
            "makeSession": True,
        }
        response = await self._http.request(
            route, json=data, headers={"Authorization": token}
        )
        return response

    async def get_group(self, endpoint: str, token: str) -> Any:
        """해당 계정으로 등록된 유저들을 가져옵니다.

        Parameters
        ----------
        endpoint: str
            학교 api 주소를 입력합니다.
        token: str
            사용자 토큰을 입력합니다.
        """
        route = Route("POST", "/v2/selectUserGroup")
        route.endpoint = endpoint
        response = await self._http.request(
            route, json={}, headers={"Authorization": token}
        )
        return response

    async def get_user(self, endpoint: str, code: str, user_id: str, token: str) -> Any:
        """해당 계정에 등록된 유저 정보를 가져옵니다.

        Parameters
        ----------
        endpoint: str
            학교 api 주소를 입력합니다.
        code: str
            학교 코드를 입력합니다.
        user_id: str
            유저 id를 입력합니다.
        token: str
            사용자 토큰을 입력합니다.
        """
        route = Route("POST", "/v2/getUserInfo")
        route.endpoint = endpoint
        response = await self._http.request(
            route,
            json={"orgCode": code, "userPNo": user_id},
            headers={"Authorization": token},
        )
        return response

    async def get_notice_list(
        self, endpoint: str, token: str, page: int = 0, count: int = 30
    ) -> Any:
        """자가진단 공지사항을 가져옵니다.

        Parameters
        ----------
        endpoint: str
            학교 api 주소를 입력합니다.
        token: str
            사용자 토큰을 입력합니다.
        page: int
            페이지를 입력합니다. 기본값은 0 입니다.
        count: int
           최대로 가져올 공지사항의 갯수를 설정합니다. 기본값은 30 입니다.
        """
        url: str = url_create_with(
            "/v2/selectNoticeList",
            currentPageNumber=page,
            listCount=count,
        )
        route = Route(
            "GET",
            url,
        )
        route.endpoint = endpoint
        response = await self._http.request(
            route,
            json={},
            headers={"Authorization": token},
        )
        return response

    async def get_notice_content(self, endpoint: str, token: str, code: str) -> Any:
        """공지사항의 내용을 가져옵니다.

        Parameters
        ----------
        endpoint: str
            학교 api 주소를 입력합니다.
        token: str
            사용자 토큰을 입력합니다.
        code: str
            공지사항의 글 id를 입력합니다.
        """
        url = url_create_with(
            "/v2/selectNotice",
            idxNtc=code,
        )
        route = Route("GET", url)
        route.endpoint = endpoint
        response = await self._http.request(
            route,
            json={},
            headers={"Authorization": token},
        )
        return response["contentsNtc"]

    async def logout(self, endpoint: str, token: str) -> Any:
        """
        자가진단에서 로그아웃합니다.

        Parameters
        ----------
        endpoint: str
            학교 api 주소를 입력합니다.
        token: str
            사용자 토큰을 입력합니다.
        """
        route = Route("GET", "/v2/logout")
        route.endpoint = endpoint
        _response = await self._http.request(
            route,
            json={},
            headers={"Authorization": token},
        )

    async def search_hospital(
        self,
        endpoint: str,
        token: str,
        location: Optional[str] = None,
        name: Optional[str] = None,
    ) -> Any:
        """
        보건소나 병원을 검색합니다.

        Parameters
        ----------
        endpoint: str
            학교 api 주소를 입력합니다.
        token: str
            사용자 토큰을 입력합니다.
        location: Optional[str]
            보건소나 병원 지역을 지정합니다.
        name: Optional[str]
            보간소나 병원 이름 또는 키워드를 지정합니다.
        """
        url = url_create_with(
            "/v2/selectHospitals",
            lctnScNm=location,
            hsptNm=name,
        )
        route = Route(
            "GET",
            url,
        )
        route.endpoint = endpoint
        response: Any = await self._http.request(
            route,
            headers={"Authorization": token},
        )
        return response

    async def request(self, *args: Any, **kwargs: Any) -> Any:
        return await self._http.request(*args, **kwargs)

    async def close(self) -> None:
        """http 세션을 닫습니다"""
        await self._http.session.close()

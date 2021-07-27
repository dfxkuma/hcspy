from .http import HTTPClient
from typing import Optional, Any, List
from .errors import AlreadyAgreed
from .model import Board
from asyncio import get_event_loop


class User:
    def __init__(self) -> None:
        self.agreement_required = None
        self.name = None
        self.birthday = None
        self._token = None
        self.checked = None
        self.register_at = None
        self.register_at_ymd = None
        self.is_healthy = None
        self.uid = None
        self.school = None
        self.password = None
        self._http = HTTPClient()

    def __repr__(self) -> str:
        return f"<User name={self.name} uid={self.uid} school={self.school.name}>"

    def from_dict(self, group_data: dict, login_data: dict, **kwargs) -> Any:
        self.agreement_required = kwargs.get("agreementRequired")
        self.name = login_data.get("userName")
        self.birthday = kwargs.get("birthday")
        self._token = group_data.get("token")
        self.checked = group_data.get("otherYn")
        self.register_at = login_data.get("registerDtm")
        self.register_at_ymd = login_data.get("registeredAtYMD")
        self.is_healthy = login_data.get("isHealthy", None)
        self.uid = group_data.get("userPNo")
        self.school = kwargs.get("school")
        self.password = kwargs.get("password")
        return self

    async def check(self, log_name: Optional[str] = None) -> None:
        if not log_name:
            log_name = self.name
        await self._http.check_survey(
            endpoint=self.school.endpoint, token=self._token, log_name=log_name
        )

    async def change_password(
        self, password: Optional[str] = None, new_password: str = None
    ) -> None:
        if not new_password:
            raise KeyError("새로운 비밀번호를 지정하세요")
        if not password:
            password = self.password
        await self._http.change_password(
            endpoint=self.school.endpoint,
            token=self._token,
            password=password,
            new_password=new_password,
        )
        self.password = new_password

    async def update_agreement(self) -> None:
        if not self.agreement_required:
            raise AlreadyAgreed("이미 약관에 동의했습니다.")
        await self._http.update_agreement(
            endpoint=self.school.endpoint, token=self._token
        )

    async def get_notice(self, page: int = 0) -> List[Board]:
        response = await self._http.get_notice_list(
            endpoint=self.school.endpoint, token=self._token, page=page
        )
        return [
            Board(
                board["idxNtc"],
                board["titleNtc"],
                board["popupYn"],
                board["cretDtm"],
                board["orgCode"],
                board["kraOrgNm"],
                board["updName"],
                await self._http.get_notice_content(
                    endpoint=self.school.endpoint,
                    token=self._token,
                    code=board["idxNtc"],
                ),
            )
            for board in response
        ]

    async def close(self) -> None:
        await self._http.logout(endpoint=self.school.endpoint, token=self._token)
        await self._http.close()

    def __del__(self) -> None:
        _loop = get_event_loop()
        if _loop.is_running():
            _loop.create_task(self._http.close())
        else:
            _loop.run_until_complete(self._http.close())

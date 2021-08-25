from typing import Optional, Any, List
from .errors import AlreadyAgreed
from .model import Board, Hospital


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
        self._http = None

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
        self._http = kwargs.get("http_session")
        return self

    async def password_exist(self) -> bool:
        """비밀번호를 설정했는지 확인합니다."""
        return await self._http.password_exist(
            endpoint=self.school.endpoint, token=self._token
        )

    async def register_password(self, password: str) -> None:
        """자가진단을 진행하기 위해 비밀번호를 생성합니다.

        Parameters
        ----------
        password: str
            설정할 비밀번호 4자리를 입력합니다.
        """
        await self._http.register_password(
            endpoint=self.school.endpoint, token=self._token, password=password
        )

    async def check(self, log_name: Optional[str] = None) -> None:
        """자가진단을 모두 증상 없음으로 체크합니다.

        Parameters
        ----------
        log_name: Optional[str]
            자가진단 로그 이름을 지정합니다.
        """
        if not log_name:
            log_name = self.name
        data = await self._http.get_user(
            endpoint=self.school.endpoint,
            code=self.school.id,
            user_id=self.uid,
            token=self._token,
        )
        await self._http.check_survey(
            endpoint=self.school.endpoint, token=data.get("token"), log_name=log_name
        )

    async def change_password(
        self, password: Optional[str] = None, new_password: str = None
    ) -> None:
        """자가진단 비밀번호를 변경합니다

        Parameters
        ----------
        password: Optional[str]
            기존 비밀번호 4자리를 입력합니다. 입력값이 없을 경우 자동으로 비밀번호를 가져옵니다.
        new_password: str
            새로운 비밀번호 4자리를 입력합니다.
        """
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
        """
        자가진단 이용약관에 동의합니다.
        """
        if not self.agreement_required:
            raise AlreadyAgreed("이미 약관에 동의했습니다.")
        await self._http.update_agreement(
            endpoint=self.school.endpoint, token=self._token
        )

    async def get_notice(self, page: int = 0) -> List[Board]:
        """자가진단 공지사항을 가져옵니다.

        Parameters
        ----------
        page: int
            페이지를 지정합니다. 기본값은 0입니다.

        """
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

    async def search_hospital(
        self, location: str = None, name: str = None
    ) -> Optional[List[Hospital]]:
        """
        보건소나 병원을 검색합니다.

        Parameters
        ----------
        location: Optional[str]
            보건소나 병원 지역을 지정합니다.
        name: Optional[str]
            보간소나 병원 이름 또는 키워드를 지정합니다.
        """
        response = await self._http.search_hospital(
            endpoint=self.school.endpoint,
            token=self._token,
            location=location,
            name=name,
        )
        return [
            Hospital(
                name=hospital["hsptNm"],
                state=hospital["sido"],
                city=hospital["sigNm"],
                schedule_weekday=hospital["weekdayBizHour"],
                schedule_saturday=hospital["satBizHour"],
                schedule_sunday=hospital["sunBizHour"],
                tell=hospital["ofcTelNo"],
                map_url=f'https://www.mohw.go.kr/react/ncov_map_page.jsp?region={hospital["sido"]}&town={hospital["sigNm"]}&hospitalNm={hospital["hsptNm"]}',
            )
            for hospital in response
        ]

    async def close(self) -> None:
        """자가진단에서 로그아웃합니다."""
        await self._http.logout(endpoint=self.school.endpoint, token=self._token)
        await self._http.close()

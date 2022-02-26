from typing import Any, List, Optional, Dict, Union, Literal

import io
from .errors import AlreadyAgreed
from .model import Board, Hospital, School
from .http import HTTPClient, Route
from .data import covid_19_guidelines, covid_self_test_guide_youtubeURL


class User:
    def __init__(
        self,
        user_data: Dict[str, Any],
        group_data: Dict[str, Any],
        info_data: Dict[str, Any],
        state: HTTPClient,
        token: str,
    ) -> None:
        self.state: HTTPClient = state
        self.state_token: str = token
        self.id: int = int(group_data.get("userPNo", 0))
        self.name: str = str(user_data.get("userName"))
        self.school: School = info_data.get("school", None)
        self.birthday: int = info_data.get("birthday", 0)
        self.password: int = info_data.get("password", 0)
        self.is_checked_survey: bool = user_data.get("isHealthy", True)
        self.wrong_password_count: int = user_data.get("wrongPassCnt", 0)
        self.unread_notice_count: int = user_data.get("newNoticeCount", 0)
        self.additional_survey_count: int = user_data.get("extSurveyCount", 0)
        self.unchecked_survey_count: int = user_data.get("extSurveyRemainCount", 0)
        self.agreement_required: bool = info_data.get("agreement_required", False)
        self.is_account_locked: bool = (
            True if user_data.get("lockYn", False) == "Y" else False
        )
        self.is_logout: bool = False

    def __repr__(self) -> str:
        return f"<User id={self.id} name={self.name} is_logout={self.is_logout}>"

    async def password_exist(self) -> bool:
        """비밀번호를 설정했는지 확인합니다."""
        return await self.state.password_exist(
            endpoint=self.school.endpoint, token=self.state_token
        )

    async def register_password(self, password: str) -> None:
        """자가진단을 진행하기 위해 비밀번호를 생성합니다.
        Parameters
        ----------
        password: str
            설정할 비밀번호 4자리를 입력합니다.
        """
        await self.state.register_password(
            endpoint=self.school.endpoint, token=self.state_token, password=password
        )

    async def check(
        self,
        log_name: Optional[str] = None,
    ) -> None:
        """자가진단을 실행합니다.
        모든 데이터는 아니요로 체크됩니다 (2번 문항은 검사하지 않음)
        ※ 이 설문지는 코로나-19 감염예방을 위하여 학생의 건강 상태를 확인하는 내용입니다.
        ※ 설문에 성실하게 응답하여 주시기 바랍니다.
        ※ 코로나19가 의심되는 경우 진단검사를 받아주세요.
        영문 설문지는 아래 사이트를 참고하세요.
            - 건강상태 자가진단 페이지: https://hcs.eduro.go.kr/#/survey (Language: English로 설정)

        Parameters
        ----------
        log_name: Optional[str]
            자가진단 로그 이름을 지정합니다.
        """
        if not log_name:
            log_name = self.name
        data: Any = await self.state.get_user(
            endpoint=self.school.endpoint,
            code=self.school.id,
            user_id=str(self.id),
            token=self.state_token,
        )
        await self.state.check_survey(
            endpoint=self.school.endpoint,
            token=data.get("token"),
            log_name=log_name,
        )

    async def change_password(self, password: int) -> None:
        """자가진단 비밀번호를 변경합니다
        Parameters
        ----------
        password: str
            새로운 비밀번호 4자리를 입력합니다.
        """
        await self.state.change_password(
            endpoint=self.school.endpoint,
            token=self.state_token,
            password=str(self.password),
            new_password=str(password),
        )
        self.password = password

    async def update_agreement(self) -> None:
        """
        자가진단 이용약관에 동의합니다.
        """
        if not self.agreement_required:
            raise AlreadyAgreed("이미 약관에 동의했습니다.")
        await self.state.update_agreement(
            endpoint=self.school.endpoint, token=self.state_token
        )

    async def get_notice(self, page: int = 0) -> List[Board]:
        """자가진단 공지사항을 가져옵니다.
        Parameters
        ----------
        page: int
            페이지를 지정합니다. 기본값은 0입니다.
        """
        response = await self.state.get_notice_list(
            endpoint=self.school.endpoint, token=self.state_token, page=page
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
                await self.state.get_notice_content(
                    endpoint=self.school.endpoint,
                    token=self.state_token,
                    code=board["idxNtc"],
                ),
            )
            for board in response
        ]

    async def search_hospital(
        self, location: Optional[str] = None, name: Optional[str] = None
    ) -> List[Hospital]:
        """
        보건소나 병원을 검색합니다.
        Parameters
        ----------
        location: Optional[str]
            보건소나 병원 지역을 지정합니다.
        name: Optional[str]
            보간소나 병원 이름 또는 키워드를 지정합니다.
        """
        response = await self.state.search_hospital(
            endpoint=self.school.endpoint,
            token=self.state_token,
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
                map_url="https://www.mohw.go.kr/react/ncov_map_page.jsp"
                f'?region={hospital["sido"]}&town={hospital["sigNm"]}&hospitalNm={hospital["hsptNm"]}',
            )
            for hospital in response
        ]

    async def get_safety_guidelines(
        self, response_type: Literal["text", "image"]
    ) -> Union[str, io.BytesIO]:
        """
        학교방역 수칙안내를 가져옵니다
        COVID-19 Safety and Quarantine Guildlines
        Parameters
        ----------
        response_type: Literal["text", "image"]
            가져올 형식을 선택합니다.
            텍스트 타입: text, 이미지 타입: image
        """
        if response_type == "text":
            return covid_19_guidelines
        elif response_type == "image":
            route = Route(method="GET", path="/eduro/1.8.1/img/guard.935c0604.png")
            route.endpoint = "https://rl6cz18qh.toastcdn.net"
            image_data = await self.state.http_session.request(route)
            image_byte = await image_data.read()
            return io.BytesIO(image_byte)

    @classmethod
    async def get_covid_self_test_guide(cls) -> str:
        """
        자가진단키트 사용법 유튜브 링크를 가져옵니다
        COVID-19 Self-Test
        """
        return covid_self_test_guide_youtubeURL

    async def logout(self) -> None:
        """자가진단에서 로그아웃합니다."""
        await self.state.logout(endpoint=self.school.endpoint, token=self.state_token)
        self.is_logout = True

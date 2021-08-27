from typing import Any, List, Optional, Dict

from .errors import AlreadyAgreed
from .model import Board, Hospital, School
from .http import HTTPClient


class User:
    def __init__(
        self,
        data: Dict[str, Any],
        group_data: Dict[str, Any],
        info_data: Dict[str, Any],
        state: HTTPClient,
        token: str,
    ) -> None:
        self.state: HTTPClient = state
        self.state_token: str = token
        self.id: int = int(group_data.get("userPNo", 0))
        self.name: str = str(data.get("userName"))
        self.school: School = info_data.get("school", None)
        self.birthday: int = info_data.get("birthday", 0)
        self.password: int = info_data.get("password", 0)
        self.is_checked_survey: bool = (
            True if group_data.get("otherYn") == "N" else True
        )
        self._register_at: str = data.get("registerDtm", "")
        self.is_healthy: bool = data.get("isHealthy", True)
        self.wrong_password_count: int = data.get("wrongPassCnt", 0)
        self.unread_notice_count: int = data.get("newNoticeCount", 0)
        self.unchecked_survey_count: int = data.get("extSurveyCount", 0)
        self.agreement_required: bool = info_data.get("agreement_required", False)
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
        option1: bool = False,
        option2: bool = False,
        option3: bool = False,
        log_name: Optional[str] = None,
    ) -> None:
        """자가진단을 실행합니다.
        이 설문지는 코로나-19 감염예방을 위하여 학생의 건강 상태를 확인하는 내용입니다.
        설문에 성실하게 응답하여 주시기 바랍니다.
        코로나19가 의심되는 경우 진단검사를 받아주세요.

        Parameters
        ----------
        option1: bool
            학생 본인이 코로나19가 의심되는 아래의 임상증상이 있나요?
             (주요 임상증상) 발열 (37.5℃ 이상), 기침, 호흡곤란, 오한, 근육통, 두통, 인후통, 후각·미각 소실
             (단, 코로나19와 관계없이 평소의 기저질환으로 인한 증상인 경우는 ‘아니오’ 선택)
             기본값은 False(아니요) 입니다.
        option2: bool
            학생 본인 또는 동거인이 코로나19 진단검사를 받고 그 결과를 기다리고 있나요?
            ① 직업특성, 또는 ② 대회참여 등 선제적 예방 목적의 진단검사인 경우는 ‘아니오’ 선택
            기본값은 False(아니요) 입니다.
        option3: bool
            학생 본인 또는 동거인이 방역당국에 의해 현재 자가격리가 이루어지고 있나요?
            동거인이 자가격리중인 경우, ① 매 등교 희망일로부터 2일 이내 진단검사 결과가 음성인 경우 또는
            ② 격리 통지를 받은 ‘즉시’ 자가격리된 동거인과 접촉이 없었던 경우는 ‘아니오’ 선택
            기본값은 False(아니요) 입니다.
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
            option1=option1,
            option2=option2,
            option3=option3,
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
                map_url='https://www.mohw.go.kr/react/ncov_map_page.jsp'
                        f'?region={hospital["sido"]}&town={hospital["sigNm"]}&hospitalNm={hospital["hsptNm"]}',
            )
            for hospital in response
        ]

    async def logout(self) -> None:
        """자가진단에서 로그아웃합니다."""
        await self.state.logout(endpoint=self.school.endpoint, token=self.state_token)
        self.is_logout = True

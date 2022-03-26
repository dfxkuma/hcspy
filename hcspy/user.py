from typing import Any, Optional, Union, List

from .model import (
    BaseHCSModel,
    Organization,
    SurveyForm,
    Board,
    Hospital,
    Covid19Guideline,
)
from .utils import duplicate, duplicated
from .http import HTTPClient
from .errors import AlreadyAgreed


@duplicated
class User(BaseHCSModel):
    """
    로그인으로 유저 데이터를 가져왔을때 반환하는 인스턴스입니다.
    """

    def __init__(
        self, state: HTTPClient, organization: Organization, **response_data: Any
    ) -> None:
        super().__init__(**response_data)
        self.state = state
        self.organization_object = organization
        self._is_logout: bool = False

    def __repr__(self) -> str:
        return f"<User id={self.id} name={self.name} device_uuid={self.device_uuid} is_logout={self.is_logout}>"

    @property
    def id(self) -> Optional[str]:
        """
        유저 아이디를 반환합니다.
        """
        return self.data.get("userPNo")

    @property
    def name(self) -> Optional[str]:
        """
        유저 이름을 반환합니다.
        """
        return self.data.get("userName")

    @property
    def device_uuid(self) -> Optional[str]:
        """
        디바이스에 uuid를 반환합니다.
        """
        return self.data.get("deviceUuid")

    @property
    def organization(self) -> Organization:
        """
        유저가 속한 기관(학교, 대학교, 오피스)를 반환합니다.
        """
        return self.organization_object

    @property
    def is_healthy(self) -> bool:
        """
        자가진단 여부를 반환합니다.
        """
        if not self.data.get("isHealthy"):
            return False
        return True

    @property
    def wrong_password_count(self) -> Optional[int]:
        """
        비밀번호 재시도 가능 횟수를 반환합니다.
        """
        if not self.data.get("wrongPassCnt"):
            return
        return int(self.data.get("wrongPassCnt"))

    @property
    def unread_notice_count(self) -> Optional[int]:
        """
        읽지 않은 공지사항 갯수를 반환합니다.
        """
        if not self.data.get("newNoticeCount"):
            return
        return int(self.data.get("newNoticeCount"))

    @property
    def additional_survey_count(self) -> Optional[int]:
        """
        추가로 가능한 설문 조사 갯수를 반환합니다.
        """
        if not self.data.get("extSurveyCount"):
            return
        return int(self.data.get("extSurveyCount"))

    @property
    def unchecked_survey_count(self) -> Optional[int]:
        """
        완료하지 않은 설문 조사 갯수를 반환합니다.
        """
        if not self.data.get("extSurveyRemainCount"):
            return
        return int(self.data.get("extSurveyRemainCount"))

    @property
    def tos_agreement_required(self) -> Optional[bool]:
        """
        자가진단 이용약관 동의 여부를 반환합니다.
        """
        if not self.data.get("pInfAgrmYn"):
            return
        return {"Y": True, "N": False}[self.data.get("pInfAgrmYn")]

    @property
    def is_locked(self) -> Optional[bool]:
        """
        자가진단 계정의 정지 여부를 반환합니다.
        """
        if not self.data.get("lockYn"):
            return
        return {"Y": True, "N": False}[self.data.get("lockYn")]

    @property
    def token(self) -> Optional[str]:
        """
        자가진단 api에 사용되는 유저 토큰을 반환합니다.
        """
        return self.data.get("token")

    @property
    def is_logout(self) -> Optional[bool]:
        """
        자가진단 사이트에 유저 로그아웃 여부를 반환합니다.
        """
        return self._is_logout

    @property
    def is_student(self) -> Optional[bool]:
        """
        자가진단 사이트에 등록되어있는 유저의 학생 여부를 반환합니다.
        """
        if not self.data.get("stdntYn"):
            return
        return {"Y": True, "N": False}[self.data.get("stdntYn")]

    @property
    def survey_data(self) -> Optional[SurveyForm]:
        """
        자가진단 응답 내용을 <SurveyForm> 클래스로 반환합니다.
        """
        if not self.is_healthy:
            return
        return SurveyForm(**self.data)

    @property
    def covid_19_guideline(self) -> Covid19Guideline:
        """
        학교 방역수칙 안내를 <Covid19Guideline> 클래스로 반환합니다.
        """
        return Covid19Guideline(state=self.state)

    @duplicate("has_password")
    async def password_exist(self) -> bool:
        """
        자가진단에 초기 비밀번호를 설정했는지 확인합니다.
        """
        return await self.state.password_exist(
            endpoint=self.organization.endpoint, token=self.token
        )

    async def register_password(self, password: str) -> None:
        """
        자가진단을 진행하기 위해 비밀번호를 생성합니다.

        Parameters
        ----------
        password: str
            설정할 비밀번호 4자리를 입력합니다.
        """
        await self.state.register_password(
            endpoint=self.organization.endpoint, token=self.token, password=password
        )

    @duplicate("survey", "register_survey", "submit_survey")
    async def check(
        self,
        option1: bool = False,
        option2: Union[bool, None] = None,
        option3: bool = False,
        log_name: Optional[str] = None,
    ) -> None:
        """
        자가진단을 실행합니다.
        모든 데이터는 아니요로 체크됩니다 (2번 문항은 검사하지 않음)

        ※ 이 설문지는 코로나-19 감염예방을 위하여 학생의 건강 상태를 확인하는 내용입니다.
        ※ 설문에 성실하게 응답하여 주시기 바랍니다.
        ※ 코로나19가 의심되는 경우 진단검사를 받아주세요.

        Parameters
        ----------
        option1:
            1. 학생 본인이 코로나19 감염에 의심되는 아래의 임상증상*이 있나요?
            [ * 주요 임상증상 : 발열(37.5℃), 기침, 호흡곤란, 오한, 근육통, 두통, 인후통, 후각·미각소실 ]
            ※ 단 학교에서 선별진료소 검사결과(음성)를 확인 후 등교를 허용한 경우, 또는 선천성질환·만성질환(천식 등)으로 인한 증상인 경우 ‘아니오’를 선택하세요
        option2:
            2. 학생은 오늘(어제 저녁 포함) 신속항원검사(자가진단)를 실시했나요?
            [ 코로나19 완치자의 경우, 확진일로부터 45일간 신속항원검사(자가진단)는 실시하지 않음(“검사하지 않음”으로 선택) ]
        option3:
            3. 학생 본인이 PCR 등 검사를 받고 그 결과를 기다리고 있나요?
        log_name: Optional[str]
            자가진단 로그 이름을 지정합니다. 비워둘 경우 name 파라미터에서 이름을 가져옵니다.
        """
        if not log_name:
            log_name = self.name
        data: Any = await self.state.get_user(
            endpoint=self.organization.endpoint,
            code=self.organization.id,
            user_id=self.id,
            token=self.token,
        )
        await self.state.check_survey(
            endpoint=self.organization.endpoint,
            token=data.get("token"),
            option1=option1,
            option2=option2,
            option3=option3,
            log_name=log_name,
        )

    async def change_password(self, password: str, new_password: str) -> None:
        """
        자가진단 비밀번호를 변경합니다

        Parameters
        ----------
        password: str
            기존 비밀번호 4자리를 입력합니다.
        new_password: str
            새로운 비밀번호 4자리를 입력합니다.
        """
        await self.state.change_password(
            endpoint=self.organization.endpoint,
            token=self.token,
            password=self.password,
            new_password=password,
        )

    @duplicate("agree_tos")
    async def update_agreement(self) -> None:
        """
        자가진단 이용약관에 동의합니다.
        """
        if not self.tos_agreement_required:
            raise AlreadyAgreed("이미 약관에 동의했습니다.")
        await self.state.update_agreement(
            endpoint=self.organization.endpoint, token=self.token
        )

    async def get_notice_content(self, code: str) -> Optional[str]:
        """
        자가진단 공지사항 내용을 반환합니다.

        Parameters
        ----------
        code: str
            공지사항 고유 코드를 입력합니다.
        """
        response = await self.state.get_notice_content(
            endpoint=self.organization.endpoint,
            token=self.token,
            code=code,
        )
        return response

    @duplicate("get_announcement")
    async def get_notice(self, page: int = 0) -> List[Board]:
        """
        자가진단 공지사항을 반환합니다.

        Parameters
        ----------
        page: int
            페이지를 지정합니다. 기본값은 0입니다.
        """
        response = await self.state.get_notice_list(
            endpoint=self.organization.endpoint, token=self.token, page=page
        )
        return [
            Board(
                body_content=await self.get_notice_content(board_data["idxNtc"]),
                **board_data,
            )
            for board_data in response
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
            endpoint=self.organization.endpoint,
            token=self.token,
            location=location,
            name=name,
        )
        return [Hospital(**hospital_data) for hospital_data in response]

    async def logout(self) -> None:
        """
        자가진단에서 로그아웃합니다.
        """
        await self.state.logout(endpoint=self.organization.endpoint, token=self.token)
        self._is_logout = True

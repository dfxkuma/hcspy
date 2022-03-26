from typing import Any, Dict, Optional, Union

from .abc import HCSModelABC
from .http import HTTPClient, Route
from .data import covid_19_guidelines
from io import BytesIO
from json import dumps
from datetime import datetime


class BaseHCSModel(HCSModelABC):
    def __init__(self, **response_data: Any) -> None:
        self._response_data = response_data

    @property
    def data(self) -> Dict[str, Any]:
        return self._response_data

    @property
    def wrapped_data(self) -> str:
        return dumps(self._response_data)

    @property
    def is_error(self) -> bool:
        if self.data.get("isError"):
            return True
        return False


class Organization(BaseHCSModel):
    """
    기관의 정보를 가져왔을때 반환하는 인스턴스입니다.
    """

    def __init__(
        self, organization_type: str, access_key: str, **response_data: Any
    ) -> None:
        super().__init__(**response_data)
        self.organization_type = organization_type
        self.access_key = access_key

    def __repr__(self) -> str:
        return f"<{self.organization_type.capitalize()} id={self.id} name={self.name} address={self.address} endpoint={self.endpoint}>"

    @property
    def id(self) -> Optional[str]:
        """
        기관의 고유 코드를 반환합니다.
        """
        return self.data.get("orgCode")

    @property
    def name(self) -> Optional[str]:
        """
        기관의 한글 이름을 반환합니다.
        """
        return self.data.get("kraOrgNm")

    @property
    def name_en(self) -> Optional[str]:
        """
        기관의 영어 이름을 반환합니다.
        """
        return self.data.get("engOrgNm")

    @property
    def city(self) -> Optional[str]:
        """
        기관이 위치해있는 지역을 한글로 반환합니다.
        """
        return self.data.get("lctnScNm")

    @property
    def address(self) -> Optional[str]:
        """
        기관의 한글 도로명주소를 반환합니다.
        """
        return self.data.get("addres")

    @property
    def hcs_host(self) -> Optional[str]:
        """
        기관의 자가진단 호스트 서버 도메인을 반환합니다.
        """
        return self.data.get("atptOfcdcConctUrl")

    @property
    def endpoint(self) -> Optional[str]:
        """
        기관의 자가진단 호스트 서버 엔드포인트 URL을 반환합니다.
        """
        if not self.hcs_host:
            return
        return f"https://{self.hcs_host}"

    @property
    def sign_code(self) -> Optional[str]:
        """
        기관의 인증 숫자 코드를 반환합니다.
        """
        return self.data.get("sigCode")

    @property
    def type(self) -> str:
        """
        기관 유형을 반환합니다.

        - 기관 유형
          유치원, 초등학교, 중학교, 고등학교: school
          대학교: univ
          교육행정기관 등: office

        """
        return self.organization_type

    @property
    def key(self) -> str:
        """
        검색 키를 반환합니다.
        이 키는 로그인 기능 사용시에 요구될 수 있습니다.
        """
        return self.access_key


class BoardAuthor(BaseHCSModel):
    """
    자가진단 공지사항의 작성자를 가져왔을때 반환하는 인스턴스입니다.
    """

    def __init__(self, **response_data: Any) -> None:
        super().__init__(**response_data)

    def __repr__(self) -> str:
        return f"<BoardAuthor name={self.name} group_name={self.group_name} group_code={self.group_code}>"

    @property
    def name(self) -> Optional[str]:
        """
        공지사항 작성자의 닉네임을 반환합니다.
        """
        return self.data.get("updName")

    @property
    def group_name(self) -> Optional[str]:
        """
        공지사항 작성자가 속해 있는 그룹 이름을 반환합니다.
        """
        return self.data.get("kraOrgNm")

    @property
    def group_code(self) -> Optional[str]:
        """
        공지사항 작성자가 속해 있는 그룹 고유 코드를 반환합니다.
        """
        return self.data.get("orgCode")


class Board(BaseHCSModel):
    """
    자가진단 공지사항을 가져왔을때 반환하는 인스턴스입니다.
    """

    def __init__(self, body_content: str, **response_data: Any) -> None:
        super().__init__(**response_data)
        self.body_content = body_content

    def __repr__(self) -> str:
        return f"<Board id={self.id} title={self.title} author={self.author}>"

    @property
    def id(self) -> Optional[str]:
        """
        공지사항 글의 고유 아이디를 반환합니다.
        """
        return self.data.get("idxNtc")

    @property
    def title(self) -> Optional[str]:
        """
        공지사항 글의 제목을 반환합니다.
        """
        return self.data.get("titleNtc")

    @property
    def is_popup(self) -> Optional[bool]:
        """
        공지사항 글의 팝업 여부를 반환합니다.
        """
        if not self.data.get("popupYn"):
            return
        return {"Y": True, "N": False}[self.data.get("popupYn")]

    @property
    def created_at(self) -> Optional[datetime]:
        """
        공지사항 글의 작성 시간을 <datetime.datetime> 클래스로 반환합니다.
        """
        if not self.data.get("cretDtm"):
            return
        datetime_object = datetime.strptime(
            self.data.get("cretDtm"), "%Y-%m-%d %H:%M:%S.%f"
        )
        return datetime_object

    @property
    def author(self) -> Optional[BoardAuthor]:
        """
        공지사항 글의 작성자를 <BoardAuthor> 클래스로 반환합니다.
        """
        if not self.data.get("updName"):
            return
        return BoardAuthor(**self.data)

    @property
    def content(self) -> str:
        """
        공지사항 글의 내용을 텍스트 형식으로 반환합니다.
        """
        return self.body_content


class Hospital(BaseHCSModel):
    """
    보건소나 병원을 가져왔을때 반환하는 인스턴스입니다.
    """

    def __init__(self, **response_data: Any) -> None:
        super().__init__(**response_data)

    def __repr__(self) -> str:
        return f"<Hospital name={self.name} tell={self.tell} diagnosis_type={self.diagnosis_type} organization_type={self.organization_type}>"

    @property
    def name(self) -> Optional[str]:
        """
        기관 이름을 반환합니다.
        """
        return self.data.get("hsptNm")

    @property
    def state(self) -> Optional[str]:
        """
        기관 주소의 시/도를 한글로 반환합니다.
        """
        return self.data.get("sido")

    @property
    def city(self) -> Optional[str]:
        """
        기관 주소의 도시를 한글로 반환합니다.
        """
        return self.data.get("sigNm")

    @property
    def tell(self) -> Optional[str]:
        """
        기관의 전화번호를 반환합니다.
        """
        return self.data.get("ofcTelNo")

    @property
    def diagnosis_type(self) -> Optional[str]:
        """
        기관의 진료 타입을 반환합니다.
        예) 외래진료 및 입원
        """
        return self.data.get("fctTypeNm")

    @property
    def organization_type(self) -> Optional[str]:
        """
        기관 타입을 반환합니다.
        예) 국민 안심병원
        """
        if not self.data.get("hsptGubunCode"):
            return
        return {"A": "국민 안심병원", "B": "승차검진 선별진료소"}[self.data.get("hsptGubunCode")]

    @property
    def schedule_weekday(self) -> Optional[str]:
        """
        기관의 평일 운영 가능 시간을 반환합니다.
        """
        return self.data.get("weekdayBizHour")

    @property
    def schedule_saturday(self) -> Optional[str]:
        """
        기관의 토요일 운영 가능 시간을 반환합니다.
        """
        return self.data.get("satBizHour")

    @property
    def schedule_sunday(self) -> Optional[str]:
        """
        기관의 일요일 운영 가능 시간을 반환합니다.
        """
        return self.data.get("sunBizHour")

    @property
    def map_url(self) -> str:
        """
        기관의 지도 주소 URL을 반환합니다.
        """
        return (
            f"https://www.mohw.go.kr/react/ncov_map_page.jsp"
            f"?region={self.state}&town={self.city}&hospitalNm={self.name}"
        )


class SurveyForm(BaseHCSModel):
    """
    유저의 자가진단 폼 데이터를 가져왔을때 반환하는 인스턴스입니다.
    """

    def __init__(self, **response_data: Any) -> None:
        super().__init__(**response_data)

    def __repr__(self) -> str:
        return f"<SurveyForm checked_at={self.checked_at} option1={self.option1} option2={self.option2} option3={self.option3}>"

    @property
    def checked_at(self) -> Optional[datetime]:
        """
        자가진단 참여 시간을 <datetime.datetime> 클래스로 반환합니다.
        """
        if not self.data.get("registerDtm"):
            return
        datetime_object = datetime.strptime(
            self.data.get("registerDtm"), "%Y-%m-%d %H:%M:%S.%f"
        )
        return datetime_object

    @property
    def option1(self) -> Optional[bool]:
        """
        아래 설문의 응답을 반환합니다.

        1. 학생 본인이 코로나19 감염에 의심되는 아래의 임상증상*이 있나요?
        [ * 주요 임상증상 : 발열(37.5℃), 기침, 호흡곤란, 오한, 근육통, 두통, 인후통, 후각·미각소실 ]
        ※ 단 학교에서 선별진료소 검사결과(음성)를 확인 후 등교를 허용한 경우, 또는 선천성질환·만성질환(천식 등)으로 인한 증상인 경우 ‘아니오’를 선택하세요

        "예"라고 응답한 경우 True, "아니요"라고 응답한 경우 False를 반환합니다.
        """
        if not self.data.get("rspns01"):
            return
        return {"2": True, "1": False}[self.data.get("rspns01")]

    @property
    def option2(self) -> Union[bool, None]:
        """
        아래 설문의 응답을 반환합니다.

        2. 학생은 오늘(어제 저녁 포함) 신속항원검사(자가진단)를 실시했나요?
        [ 코로나19 완치자의 경우, 확진일로부터 45일간 신속항원검사(자가진단)는 실시하지 않음(“검사하지 않음”으로 선택) ]

        "양성"이라고 응답한 경우 True, "음성"이라고 응답한 경우 False, "검사하지 않음"이라고 응답한 경우는 None을 반환합니다.
        """
        if not self.data.get("rspns03"):
            return
        if self.data.get("rspns03") == "1":
            return None
        elif self.data.get("rspns03") == "0" and self.data.get("rspns07") == "0":
            return False
        elif self.data.get("rspns03") == "0" and self.data.get("rspns07") == "1":
            return True

    @property
    def option3(self) -> Optional[bool]:
        """
        아래 설문의 응답을 반환합니다.

        3. 학생 본인이 PCR 등 검사를 받고 그 결과를 기다리고 있나요?

        "예"라고 응답한 경우 True, "아니요"라고 응답한 경우 False를 반환합니다.
        """
        if not self.data.get("rspns02"):
            return
        return {"2": True, "1": False}[self.data.get("rspns02")]


class Covid19Guideline(BaseHCSModel):
    """
    학교 방역수칙 안내를 가져왔을때 반환하는 인스턴스입니다.
    """

    def __init__(self, state: HTTPClient) -> None:
        super().__init__(**{})
        self.state = state

    def __repr__(self) -> str:
        return f"<Covid19Guideline Requester>"

    async def get_text(self) -> str:
        """
        학교방역 수칙안내를 텍스트 형식으로 반환합니다.
        """
        return covid_19_guidelines

    async def get_image(self) -> Optional[BytesIO]:
        """
        학교방역 수칙안내를 이미지 형식으로 반환합니다.
        """
        route = Route(method="GET", path="/eduro/1.8.1/img/guard.935c0604.png")
        route.endpoint = "https://rl6cz18qh.toastcdn.net"
        response = await self.state.http_session.request(route)
        image = await response.read()
        return BytesIO(image)

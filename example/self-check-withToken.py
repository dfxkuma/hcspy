# 토큰 자가진단 예제
# <User>.state_token을 저장하고 추가적인 개인정보 입력 없이 로그인을 할 수 있음.

from asyncio import run

from hcspy import HCSClient


async def self_check() -> None:
    client = HCSClient()
    school = await client.search_school(
        search_type="school", name="학교 이름", level="학교 레벨/유형", area="지역"
    )
    user = await client.login(
        school=school[-1],  # 검색한 학교들 중 최상위에 있는 학교 가져오기
        name="사용자 이름",
        birthday="사용자 생년월일 6자리",
        password="4자리 비밀번호",
    )
    user1 = user[-1]  # 첫번째 유저 가져오기
    user_token = user1.state_token

    token_user = await client.token_login(
        school=school[-1], token=user_token, password="4자리 비밀번호"
    )
    token_user1 = token_user[-1]
    await token_user1.check()


run(self_check())

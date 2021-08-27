# 자가진단 예제

from asyncio import run

from hcspy import HCSClient


async def self_check() -> None:
    client = HCSClient()
    school = await client.search_school(name="학교 이름", level="학교 레벨/유형", area="지역")
    user = await client.login(
        school=school[-1],  # 검색한 학교들 중 최상위에 있는 학교 가져오기
        name="사용자 이름",
        birthday="사용자 생년월일 6자리",
        password="4자리 비밀번호",
    )
    user1 = user[-1]  # 첫번째 유저 가져오기
    await user1.check(option1=False, option2=False, option3=False)  # 자가진단 실행


run(self_check())

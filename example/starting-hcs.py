# 자가진단을 처음 하는 유저 가입 및 자가진단 실행 예제

from asyncio import run

from hcspy import HCSClient


async def self_check() -> None:
    client = HCSClient()
    school = await client.search_school(name="신일중학교", level="중학교", area="")
    user = await client.login(
        school=school[-1],  # 검색한 학교들 중 최상위에 있는 학교 가져오기
        name="사용자 이름",
        birthday="사용자 생년월일 6자리",
        password="4자리 비밀번호",
    )
    user1 = user[-1]  # 첫번째 유저 가져오기
    await user1.update_agreement()  # 약관동의
    if not await user1.password_exist():  # 비밀번호가 없는 경우
        await user1.register_password("비밀번호 4자리")  # 비밀번호 생성
    await user1.check(option1=False, option2=False, option3=False)  # 자가진단 실행


run(self_check())

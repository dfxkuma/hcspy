# 공지사항 가져오기 예제

from hcspy import HCSClient
from asyncio import run


async def get_notice():
    client = HCSClient()
    school = await client.search_school(name="학교 이름", level="학교 레벨/유형", area="지역")
    user = await client.login(
        school=school[-1],  # 검색한 학교들 중 최상위에 있는 학교 가져오기
        name="사용자 이름",
        birthday="사용자 생년월일 6자리",
        password="4자리 비밀번호",
    )
    user1 = user[-1]  # 첫번째 유저 가져오기
    notice_list = await user1.get_notice()  # 공지사항 가져오기
    for notice in notice_list:  # 정보 출력
        print(
            f"공지사항 | {notice.id} | {notice.title}\n작성자: {notice.group_name} 소속 {notice.author}\n{notice.content}\n\n"
        )


run(get_notice())

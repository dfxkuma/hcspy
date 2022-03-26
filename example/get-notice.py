# 공지사항 가져오기 예제

from asyncio import run

from hcspy import HCSClient


async def get_notice() -> None:
    client = HCSClient()
    organization = await client.search_organization(
        search_type="school", name="학교 이름", level="학교 레벨/유형", area="지역"
    )
    user = await client.login(
        organization=organization[-1],  # 검색한 학교들 중 최상위에 있는 학교 가져오기
        name="사용자 이름",
        birthday="사용자 생년월일 6자리",
        password="4자리 비밀번호",
    )
    user1 = user[-1]  # 첫번째 유저 가져오기
    notice_list = await user1.get_notice()  # 공지사항 가져오기
    for notice in notice_list:  # 정보 출력
        print(
            f"공지사항 | {notice.id} | {notice.title}\n작성자: {notice.author.group_name} 소속 {notice.author.name}\n{notice.content}\n\n "
        )


run(get_notice())

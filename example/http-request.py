# 자가진단 서버로 http 요청

from asyncio import run

from hcspy import HTTPClient
from hcspy.http import Route


async def http_request() -> None:
    http_client = HTTPClient()
    route = Route("요청 유형", "url")  # type: ignore # url은 https://hcs.eduro.go.kr/v2 제외 후 입력
    response = await http_client.request(route, json={})  # http 요청하기
    print(response)  # 결과값 출력


run(http_request())

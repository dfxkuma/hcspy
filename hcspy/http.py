import aiohttp
from typing import ClassVar, Any, Optional, Literal, Dict
from urllib.parse import quote as _uriquote

from .errors import HTTPException


async def content_type(response):
    if response.headers.get("Content-Type") == "application/json; charset=utf-8":
        return await response.json()
    return await response.text()


class Route:
    BASE: ClassVar[str] = "https://hcs.eduro.go.kr"

    def __init__(self, method: str, path: str, **parameters: Any) -> None:
        self.path: str = path
        self.method: str = method
        url = self.BASE + self.path
        if parameters:
            url = url.format_map(
                {
                    k: _uriquote(v) if isinstance(v, str) else v
                    for k, v in parameters.items()
                }
            )
        self.url: str = url


class HTTPRequest:
    def __init__(
        self,
        connector: Optional[aiohttp.BaseConnector] = None,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        self.connector = connector
        self.__session = session
        self._cookie_jar = aiohttp.CookieJar()

    @staticmethod
    def set_header(self, header: Dict[str, str]) -> Dict[str, str]:
        header["Accept"] = "application/json, text/plain, */*"
        header["Accept-Encoding"] = "gzip, deflate, br"
        header[
            "Accept-Language"
        ] = "en-GB,en;q=0.9,ko-KR;q=0.8,ko;q=0.7,ja-JP;q=0.6,ja;q=0.5,zh-TW;q=0.4,zh;q=0.3,en-US;q=0.2"
        header["Cache-Control"] = "no-cache"
        header["Connection"] = "keep-alive"
        header["Origin"] = "https://hcs.eduro.go.kr"
        header["Pragma"] = "no-cache"
        header["Referer"] = "https://hcs.eduro.go.kr/"
        header["Sec-Fetch-Dest"] = "empty"
        header["Sec-Fetch-Mode"] = "cors"
        header["Sec-Fetch-Site"] = "same-site"
        header[
            "User-Agent"
        ] = "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
        header["X-Requested-With"] = "XMLHttpRequest"

    async def request(
        self, route: Route, method: Literal["GET", "POST"], **kwargs: Any
    ) -> Any:
        method = route.method
        url = route.url
        headers = kwargs.get("headers", None)

        if not self.__session:
            self.__session = aiohttp.ClientSession(connector=self.connector)
        if not headers:
            headers: Dict[str, str] = {
                "User-Agent": self.user_agent,
            }
        headers = self.set_header(headers)

        if "json" in kwargs:
            ContentType: str = "x-www-form-urlencoded" if method is "GET" else "json"
            headers["Content-Type"] = f"application/{ContentType};charset=UTF-8"
        if self._cookie_jar:
            kwargs["cookie_jar"] = self._cookie_jar

        async with self.__session.request(method, url, **kwargs) as response:
            data = await content_type(response)

        if response.status != 200:
            raise HTTPException(response.stats, data)

        return data


class HTTPClient(HTTPRequest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

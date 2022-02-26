# HCSPY

[![Send mail](https://img.shields.io/badge/-decave27@gmail.com-63d863?style=flat-square&logo=gmail&logoColor=white&link=mailto:decave27@gmail.com)](mailto:decave27@gmail.com) [![Badge](https://img.shields.io/pypi/v/hcspy?label=Version&style=flat-square)](https://pypi.org/project/hcspy/) [![Send mail](https://img.shields.io/pypi/dm/hcspy?color=orange&label=Downloads&style=flat-square)](https://pypi.org/project/hcspy/) [![Licence](https://img.shields.io/pypi/l/hcspy?label=License&style=flat-square)](https://github.com/decave27/hcspy/blob/main/LICENSE) [![Badge](https://img.shields.io/pypi/status/hcspy?color=%230099ff&label=Status&style=flat-square)]() <br>

파이썬 코로나 자가잔단 라이브러리입니다.


## 📥다운로드

**이 모듈은 파이썬 3.8 ~ 3.10 까지의 동작을 보장합니다.
이외의 버전에서는 제대로 작동하지 않을 수 있습니다.**

윈도우나 리눅스의 터미널에서 다음과 같이 입력합니다.

```shell
pip install hcspy
```

오류가 나는 경우, `python -m pip install --upgrade pip` 로 pip를 업데이트 해주세요.

## 🤖사용법

이 라이브러리는 비동기만 지원합니다.

[문서 보기](https://decave27.gitbook.io/hcspy/)
[예제코드 보기](https://github.com/decave27/hcspy/blob/main/example/example.md)

## 🔒 기능

이 라이브러리는 자가진단 사이트에 대부분의 기능을 지원합니다

- 로그인
- 로그아웃
- 비밀번호 변경
- 이용약관 동의
- 학교 검색
- 비밀번호 설정
- 사용자 선택
- 보안키보드 입력
- 공지사항 불러오기
- 병원, 보건소 검색하기 (진료소 찾기)
- 대학 자가진단
- 코로나19 시도정보
- 학교수치 방역안내, 자가진단키드 사용법 가져오기
- 추가설문 확인하기
- 유저 토큰으로 로그인하기

### 추후지원
- 참여자 추가
- 교육행정기관 자가진단

## ⚠️ 주의사항

### 이 라이브러리를 사용하는 모든 책임은 사용자에게 있습니다.

- 다른 사용자나 서비스에게 개인정보를 제출하지 마세요.
- 이 라이브러리를 상업 목적으로 사용하지 마세요.
- 이 라이브러리는 언제든 수정되거나 삭제될 수 있습니다.

## 💡 TIP
- <HCSClient>.token_login을 이용해 기존에 발급한 토큰으로 로그인할 수 있어요!
- client에 session을 입력하면 기존 세션을 사용하여 요청할 수 있어요!
- <User>.check 에 log_name 파라미터로 수행자 이름을 커스텀할 수 있어요!

## 😆 기여 및 참고

⭐ [331leo/hcskr_python](https://github.com/331leo/hcskr_python)

⭐ [covid-hcs/transkey-py](https://github.com/covid-hcs/transkey-py)









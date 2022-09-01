# 파이썬 코로나 자가진단 라이브러리

[![Send mail](https://img.shields.io/badge/-monotaged@protonmail.com-63d863?style=flat-square&logo=gmail&logoColor=white&link=mailto:monotaged@protonmail.com)](mailto:inspiredlp0@gmail.com)

파이썬 코로나 자가잔단 라이브러리입니다. 대부분의 모든 자가진단 사이트에 기능을 지원합니다.

## ⚠️ 주의사항

### 이 라이브러리를 사용하는 모든 책임은 사용자에게 있습니다.
### 만약 건강상태에 문제가 있다면, 이 라이브러리를 이용한 매크로 사용 중지를 권장합니다.

#### 포크 3개, 스타 14개였지만 잠시 레포를 비공개로 돌리면서 다 없어졌습니다
![image](https://user-images.githubusercontent.com/67851900/187967171-9f004055-037c-46ad-bb4e-0646843b12bd.png)


## 📥다운로드

**이 모듈은 파이썬 3.8 ~ 3.10 까지의 동작을 보장합니다.
이외의 버전에서는 제대로 작동하지 않을 수 있습니다.**

윈도우나 리눅스의 터미널에서 다음과 같이 입력합니다.

```shell
pip install git+https://github.com/monotaged/hcspy.git
```

오류가 나는 경우, `python -m pip install --upgrade pip` 로 pip를 업데이트 해주세요.

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
- 교육행정기관 자가진단
- 자가진단 응답 내용 보기
- 학교 방역수칙 안내 가져오기
- 자가진단 클라이언트 버전 가져오기

### 추후지원
- 참여자 추가

## 💡 TIP
- <HCSClient>.token_login을 이용해 기존에 발급한 토큰으로 로그인할 수 있어요!
- client에 session을 입력하면 기존 세션을 사용하여 요청할 수 있어요!
- <User>.check 에 log_name 파라미터로 수행자 이름을 커스텀할 수 있어요!

## 😆 기여 및 참고

⭐ [331leo/hcskr_python](https://github.com/331leo/hcskr_python)
⭐ [covid-hcs/transkey-py](https://github.com/covid-hcs/transkey-py)









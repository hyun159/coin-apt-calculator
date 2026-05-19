# 코인 × 아파트 계산기

비트코인/이더리움/리플 실시간 시세 + 김해시 아파트 실거래가 비교 웹 앱

## 프로젝트 구조

```
coin-apt/
├── app.py              # Flask 백엔드 (API 호출 + 라우팅)
├── requirements.txt    # 파이썬 패키지
├── templates/
│   └── index.html      # 프론트엔드 (HTML/CSS/JS)
└── README.md
```

## 사용하는 API

- **업비트 Open API** (인증 불필요): 코인 실시간 시세
- **국토교통부 실거래가 API** (인증키 필요): 김해시 아파트 매매 실거래가
- **카카오맵 API** (선택, 앱키 필요): 지도에 거래 위치 표시

## 설정 방법

### 1. 공공데이터포털 API 키 설정

app.py 파일에서 `YOUR_API_KEY_HERE` 부분을 본인의 API 키로 변경:

```python
API_KEY = "여기에_본인_API_키_입력"
```

또는 환경변수로 설정:

```bash
export APT_API_KEY="여기에_본인_API_키_입력"
```

### 2. 카카오맵 API 키 설정 (선택)

지도 기능을 사용하려면:
1. https://developers.kakao.com 에서 앱 생성
2. JavaScript 키 복사
3. templates/index.html 에서 `KAKAO_MAP_KEY` 부분을 본인 키로 변경

> 카카오맵 키 없이도 앱은 정상 동작합니다 (지도만 안 보임)

### 3. 실행

```bash
pip install -r requirements.txt
python app.py
```

브라우저에서 `http://서버IP:5000` 접속


## 엔서블 자동화

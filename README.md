# 글담 (Geuldam) - AI 기반 이미지 스토리텔링 플랫폼

## 목차
1. [프로젝트 소개](#프로젝트-소개)
2. [주요 기능](#주요-기능)
3. [기술 스택](#기술-스택)
4. [시스템 아키텍처](#시스템-아키텍처)
5. [설치 방법](#설치-방법)
6. [사용 방법](#사용-방법)
7. [프로젝트 구조](#프로젝트-구조)
8. [API 문서](#api-문서)
9. [기여 방법](#기여-방법)
10. [라이선스](#라이선스)
11. [연락처](#연락처)

## 프로젝트 소개

글담(Geuldam)은 사용자의 이미지를 AI 기술을 활용하여 독특하고 창의적인 스토리로 변환하는 혁신적인 웹 플랫폼입니다. 이 프로젝트는 이미지 처리, 자연어 처리, 그리고 대화형 AI 기술을 결합하여 사용자의 사진에서 의미 있는 이야기를 만들어냅니다.

글담의 핵심 목표는 다음과 같습니다:
- 사용자의 이미지에서 풍부한 메타데이터를 추출하여 컨텍스트 이해
- AI를 활용한 창의적이고 개인화된 스토리 생성
- 다양한 글쓰기 스타일과 톤을 제공하여 사용자의 취향에 맞는 콘텐츠 생성
- 직관적이고 사용하기 쉬운 웹 인터페이스 제공

이 플랫폼은 개인 사용자부터 콘텐츠 크리에이터, 마케터까지 다양한 사용자층을 위해 설계되었습니다.

## 주요 기능

1. **이미지 업로드 및 분석**
   - 다중 이미지 업로드 지원
   - EXIF 데이터 추출 (날짜, 위치 등)
   - 이미지 캡션 자동 생성

2. **AI 기반 스토리 생성**
   - 이미지 메타데이터 기반 스토리텔링
   - 사용자 지정 컨텍스트 반영
   - 다양한 글쓰기 스타일 (일기, SNS 포스팅, 여행기 등)
   - 사용자 정의 글쓰기 톤 (존댓말, 반말, 은어 등)

3. **커스터마이징 옵션**
   - 글 길이 조절
   - 창의성 수준 (temperature) 설정
   - 사용자 정보 반영 (나이, 성별)

4. **결과 처리**
   - 생성된 스토리 표시
   - 관련 해시태그 자동 생성
   - 소셜 미디어 공유 기능

5. **사용자 친화적 UI/UX**
   - 반응형 웹 디자인
   - 직관적인 드래그 앤 드롭 이미지 업로드
   - 실시간 처리 상태 표시

## 기술 스택

- **백엔드**:
  - Python 3.8+
  - FastAPI
  - OpenAI GPT 모델 (gpt-4o-mini)
  - Pillow (이미지 처리)
  - geopy (위치 정보 처리)

- **프론트엔드**:
  - HTML5, CSS3, JavaScript

- **데이터베이스**:
  - 현재 구현되지 않음 (향후 확장 가능성)

- **인프라 및 배포**:
  - Uvicorn (ASGI 서버)

- **버전 관리**:
  - Git

- **API**:
  - RESTful API
  - OpenAI API

- **기타 라이브러리**:
  - python-dotenv (환경 변수 관리)
  - python-multipart (파일 업로드 처리)

## 시스템 아키텍처

```
[클라이언트]
    |
    | HTTP 요청
    V
[FastAPI 서버]
    |
    |--- [ImageProcessor]
    |       |--- [ImageMetadataProcessor] (EXIF 데이터 추출)
    |       |--- [ImageCaptionGenerator] (이미지 캡션 생성)
    |
    |--- [ContentGenerator] (OpenAI GPT 활용)
    |       |--- 스토리 생성
    |       |--- 해시태그 생성
    |
    |--- [UserInputManager] (사용자 입력 처리)
    |
    |--- [OpenAI API] (외부 AI 서비스)
    |
    |--- [Geopy] (위치 정보 처리)
    |
[정적 파일 서빙]
```

## 설치 방법

1. 저장소 클론:
   ```
   git clone https://github.com/your-username/geuldam.git
   cd geuldam
   ```

2. 가상 환경 생성 및 활성화:
   ```
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. 의존성 설치:
   ```
   pip install -r requirements.txt
   ```

4. 환경 변수 설정:
   `.env` 파일을 생성하고 다음 내용을 추가하세요:
   ```
   OPENAI_API_KEY=your_openai_api_key
   HOST=0.0.0.0
   PORT=8000
   ```

5. 애플리케이션 실행:
   ```
   python main.py
   ```

## 사용 방법

1. 웹 브라우저에서 `http://localhost:8000`에 접속합니다.

2. "이미지 업로드" 버튼을 클릭하거나 이미지를 드래그 앤 드롭하여 업로드합니다.

3. 글쓰기 옵션을 선택합니다:
   - 글쓰기 스타일 (일기, SNS 포스팅 등)
   - 글쓰기 톤 (존댓말, 반말 등)
   - 창의성 수준
   - 글 길이
   - 추가 정보 (선택사항)

4. "글 생성하기" 버튼을 클릭합니다.

5. 생성된 스토리와 해시태그를 확인합니다.

6. 필요에 따라 결과를 복사하거나 소셜 미디어에 공유합니다.

## 프로젝트 구조

```
geuldam/
│
├── main.py                 # FastAPI 애플리케이션 메인 파일
├── requirements.txt        # 프로젝트 의존성
├── .env                    # 환경 변수 (gitignore에 포함되어야 함)
│
├── ImageProcessor.py       # 이미지 처리 메인 클래스
├── ImageMetadataProcessor.py  # EXIF 데이터 추출 클래스
├── ImageCaptionGenerator.py   # 이미지 캡션 생성 클래스
├── ContentGenerator.py     # AI 기반 콘텐츠 생성 클래스
├── UserInputManager.py     # 사용자 입력 관리 클래스
│
├── writing_styles.py       # 글쓰기 스타일 정의
├── writing_tones.py        # 글쓰기 톤 정의
│
├── static/                 # 정적 파일 (CSS, JS, 이미지 등)
│   ├── css/
│   ├── js/
│   └── images/
│
└── templates/              # HTML 템플릿
    └── index.html
```

## API 문서

API 문서는 Swagger UI를 통해 자동으로 생성됩니다. 서버 실행 후 `http://localhost:8000/docs`에서 확인할 수 있습니다.

주요 엔드포인트:
- `POST /upload-images/`: 이미지 업로드 및 처리
- `POST /generate-content/`: 스토리 및 해시태그 생성
- `GET /writing-styles/`: 사용 가능한 글쓰기 스타일 목록
- `GET /writing-tones/`: 사용 가능한 글쓰기 톤 목록

## 기여 방법

1. 이 저장소를 포크합니다.
2. 새 브랜치를 생성합니다: `git checkout -b feature/AmazingFeature`
3. 변경사항을 커밋합니다: `git commit -m 'Add some AmazingFeature'`
4. 브랜치에 푸시합니다: `git push origin feature/AmazingFeature`
5. Pull Request를 생성합니다.

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 연락처

프로젝트 관리자 - gadi2003@naver.com

from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List
import uvicorn
from ImageProcessor import ImageProcessor
from ContentGenerator import ContentGenerator
import os
from dotenv import load_dotenv
import json
from writing_styles import STYLE_SPECIFIC_INSTRUCTIONS
from writing_tones import WRITING_TONES
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# .env 파일에서 환경 변수 로드
load_dotenv()

# FastAPI 인스턴스 생성
app = FastAPI()

# CORS 미들웨어 설정 (모든 오리진, 인증, 메서드 및 헤더 허용)
# 실제 배포 시에는 allow_origins 파라미터에 특정 오리진을 설정하는 것이 좋습니다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙 설정
# "/static" 경로로 요청이 들어오면 "static" 폴더에서 파일을 제공합니다.
app.mount("/static", StaticFiles(directory="static"), name="static")

# HTML 템플릿 설정 (Jinja2 사용)
# "." 디렉토리에서 템플릿 파일을 찾습니다.
templates = Jinja2Templates(directory=".")

# OpenAI API 키 로드
OPENAI_API_KEY = os.getenv("ENTER OPENAI API KEY")

# 이미지 처리기와 콘텐츠 생성기 초기화
image_processor = ImageProcessor(OPENAI_API_KEY)
content_generator = ContentGenerator(OPENAI_API_KEY)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    루트 경로로 접근 시 index.html 템플릿을 렌더링하여 반환합니다.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/writing-styles/")
async def get_writing_styles():
    """
    글쓰기 스타일 목록을 반환합니다.
    STYLE_SPECIFIC_INSTRUCTIONS에서 키 목록을 추출하여 반환합니다.
    """
    return {"styles": list(STYLE_SPECIFIC_INSTRUCTIONS.keys())}

@app.get("/writing-tones/")
async def get_writing_tones():
    """
    글쓰기 톤 목록을 반환합니다.
    WRITING_TONES에서 정의된 톤 목록을 반환합니다.
    """
    return {"tones": WRITING_TONES}

@app.post("/upload-images/")
async def upload_images(files: List[UploadFile] = File(...)):
    """
    이미지를 업로드하고 'image_upload' 폴더에 저장한 후 각 이미지에 대한 메타데이터와 캡션을 생성합니다.
    """
    image_data_list = []

    # 이미지 업로드 폴더 경로 설정
    upload_folder = "image_upload"
    os.makedirs(upload_folder, exist_ok=True)  # 폴더가 없으면 생성

    for file in files:
        contents = await file.read()  # 이미지 파일 내용 읽기
        file_path = os.path.join(upload_folder, file.filename)  # 저장할 파일 경로 설정

        with open(file_path, "wb") as f:
            f.write(contents)  # 이미지 파일을 'image_upload' 폴더에 저장

        try:
            # 이미지 처리
            result = image_processor.process_image(file_path)
            image_data_list.append(result)
            logging.info(f"Processed image data: {result}")
        except Exception as e:
            logging.error(f"이미지 {file.filename} 처리 중 오류 발생: {str(e)}")
            logging.exception(e)
            return {"error": f"이미지 {file.filename} 처리 중 오류 발생: {str(e)}"}

    return {"image_data": image_data_list}

@app.post("/generate-content/")
async def generate_content(
    image_data_list: str = Form(...),
    user_context: str = Form(default=""),
    writing_style: str = Form(...),
    writing_tone: str = Form(...),
    writing_length: int = Form(...),
    temperature: float = Form(...),
    user_info: str = Form(...)
):
    """
    이미지 데이터, 사용자 컨텍스트, 글쓰기 스타일, 글쓰기 톤, 글 길이, 생성 온도, 사용자 정보를 바탕으로 콘텐츠를 생성합니다.
    """
    try:
        logging.info(f"Content generation started with parameters: style={writing_style}, tone={writing_tone}, length={writing_length}, temperature={temperature}")
        
        # 이미지 데이터와 사용자 정보 파싱
        image_data_list = json.loads(image_data_list)
        user_info = json.loads(user_info)

        logging.info(f"Parsed image_data_list: {json.dumps(image_data_list, indent=2)}")
        logging.info(f"Parsed user_info: {json.dumps(user_info, indent=2)}")
        logging.info(f"User context: {user_context}")

        # 사용자 정보에 글쓰기 톤 정보 추가
        user_info['writing_tone'] = writing_tone
        user_info['writing_tone_description'] = WRITING_TONES.get(writing_tone, ['', '', ''])[2]

        # 스토리 및 해시태그 생성
        story, generated_tone = content_generator.create_story(
            image_data_list, user_context, writing_style, writing_length, temperature, user_info
        )
        hashtags = content_generator.create_hashtags(story)

        logging.info("Content generation completed successfully")
        return {
            "story": story,
            "writing_tone": generated_tone,
            "hashtags": hashtags
        }
    except Exception as e:
        logging.error(f"콘텐츠 생성 중 오류 발생: {str(e)}")
        logging.exception(e)
        logging.info(f"Raw image_data_list: {image_data_list}")
        logging.info(f"Raw user_info: {user_info}")
        logging.info(f"Writing tone: {writing_tone}")
        logging.info(f"Writing tone description: {WRITING_TONES.get(writing_tone, ['', '', ''])[2]}")
        return {"error": str(e)}

if __name__ == "__main__":
    # 환경 변수에서 호스트와 포트 정보를 가져와 uvicorn 서버 실행
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host=host, port=port)

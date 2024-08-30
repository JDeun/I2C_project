from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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

app = FastAPI()

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포 시에는 구체적인 오리진을 지정해야 합니다
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙 설정
app.mount("/static", StaticFiles(directory="."), name="static")

# OpenAI API 키 로드
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 이미지 처리기와 콘텐츠 생성기 초기화
image_processor = ImageProcessor(OPENAI_API_KEY)
content_generator = ContentGenerator(OPENAI_API_KEY)

@app.get("/writing-styles/")
async def get_writing_styles():
    """글쓰기 스타일 목록을 반환합니다."""
    return {"styles": list(STYLE_SPECIFIC_INSTRUCTIONS.keys())}

@app.get("/writing-tones/")
async def get_writing_tones():
    """글쓰기 톤 목록을 반환합니다."""
    return {"tones": {k: v[0] for k, v in WRITING_TONES.items()}}

@app.post("/upload-images/")
async def upload_images(files: List[UploadFile] = File(...)):
    """
    이미지를 업로드하고 처리합니다.
    각 이미지에 대한 메타데이터와 캡션을 생성합니다.
    """
    image_data_list = []
    for file in files:
        contents = await file.read()
        with open(file.filename, "wb") as f:
            f.write(contents)
        try:
            result = image_processor.process_image(file.filename)
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
    user_context: str = Form(default=""),  # default="" 추가
    writing_style: str = Form(...),
    writing_tone: str = Form(...),
    writing_length: int = Form(...),
    temperature: float = Form(...),
    user_info: str = Form(...)
):
    try:
        logging.info(f"Content generation started with parameters: style={writing_style}, tone={writing_tone}, length={writing_length}, temperature={temperature}")
        image_data_list = json.loads(image_data_list)
        user_info = json.loads(user_info)
        
        logging.info(f"Parsed image_data_list: {json.dumps(image_data_list, indent=2)}")
        logging.info(f"Parsed user_info: {json.dumps(user_info, indent=2)}")
        logging.info(f"User context: {user_context}")  # user_context 로깅 추가
        
        user_info['writing_tone'] = writing_tone
        user_info['writing_tone_description'] = WRITING_TONES.get(writing_tone, ['', '', ''])[2]
        
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
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host=host, port=port)
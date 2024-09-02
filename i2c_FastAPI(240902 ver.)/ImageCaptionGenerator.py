from PIL import Image
import io
import base64
from openai import OpenAI
import logging

class ImageCaptionGenerator:
    def __init__(self, openai_api_key):
        """
        ImageCaptionGenerator 클래스 초기화
        
        :param openai_api_key: OpenAI API 키
        """
        self.client = OpenAI(api_key=openai_api_key)
        self.logger = logging.getLogger(__name__)

    def generate_caption(self, image_path, metadata):
        """
        이미지에 대한 캡션을 생성합니다.
        
        :param image_path: 이미지 파일 경로
        :param metadata: 이미지 메타데이터
        :return: 생성된 캡션
        """
        try:
            base64_image = self._process_image(image_path)
            prompt = self._create_prompt(metadata)
            return self._get_caption_from_api(prompt, base64_image)
        except Exception as e:
            self.logger.error(f"캡션 생성 중 오류 발생: {e}")
            return "캡션을 생성할 수 없습니다."

    def _process_image(self, image_path):
        """
        이미지를 처리하여 base64 인코딩된 문자열로 변환합니다.
        
        :param image_path: 이미지 파일 경로
        :return: base64 인코딩된 이미지 문자열
        """
        with Image.open(image_path) as img:
            img = self._convert_to_rgb(img)
            img = self._resize_image(img)
            return self._image_to_base64(img)

    def _convert_to_rgb(self, img):
        """
        이미지를 RGB 모드로 변환합니다.
        
        :param img: PIL 이미지 객체
        :return: RGB 모드로 변환된 이미지 객체
        """
        if img.mode == 'RGBA':
            return img.convert('RGB')
        return img

    def _resize_image(self, img):
        """
        이미지 크기를 조정합니다.
        
        :param img: PIL 이미지 객체
        :return: 크기가 조정된 이미지 객체
        """
        max_size = (512, 512)  # OpenAI API 권장 최대 크기
        img.thumbnail(max_size, Image.LANCZOS)
        return img

    def _image_to_base64(self, img):
        """
        이미지를 base64 인코딩된 문자열로 변환합니다.
        
        :param img: PIL 이미지 객체
        :return: base64 인코딩된 이미지 문자열
        """
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    def _create_prompt(self, metadata):
        """
        캡션 생성을 위한 프롬프트를 생성합니다.
        
        :param metadata: 이미지 메타데이터
        :return: 생성된 프롬프트 문자열
        """
        return f"""이 이미지를 설명해주세요. 다음 메타데이터도 참고하세요:
        날짜/시간: {metadata['labeled_exif'].get('Date/Time', 'N/A')}
        위치: {metadata['location_info'].get('full_address', 'N/A')}
        """

    def _get_caption_from_api(self, prompt, base64_image):
        """
        OpenAI API를 사용하여 이미지 캡션을 생성합니다.
        
        :param prompt: 캡션 생성을 위한 프롬프트
        :param base64_image: base64 인코딩된 이미지 문자열
        :return: 생성된 캡션
        """
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ],
                }
            ],
            max_tokens=300
        )
        return response.choices[0].message.content
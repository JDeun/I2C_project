from ImageMetadataProcessor import ImageMetadataProcessor
from ImageCaptionGenerator import ImageCaptionGenerator
from typing import Dict, Any
import logging

class ImageProcessor:
    def __init__(self, openai_api_key):
        """
        ImageProcessor 클래스 초기화
        
        :param openai_api_key: OpenAI API 키
        """
        self.metadata_processor = ImageMetadataProcessor()
        self.caption_generator = ImageCaptionGenerator(openai_api_key)
        self.logger = logging.getLogger(__name__)

    def process_image(self, image_path: str) -> Dict[str, Any]:
        """
        이미지를 처리하고 메타데이터와 캡션을 생성합니다.
        
        :param image_path: 처리할 이미지의 경로
        :return: 이미지 경로, 메타데이터, 캡션을 포함한 딕셔너리
        """
        try:
            self.logger.info(f"이미지 처리 시작: {image_path}")
            metadata = self._process_metadata(image_path)
            caption = self._generate_caption(image_path, metadata)
            return {
                'image_path': image_path,
                'metadata': metadata,
                'caption': caption
            }
        except Exception as e:
            self.logger.error(f"이미지 {image_path} 처리 중 오류 발생: {str(e)}")
            self.logger.exception(e)
            raise

    def _process_metadata(self, image_path: str) -> Dict[str, Any]:
        """
        이미지의 메타데이터를 추출합니다.
        
        :param image_path: 메타데이터를 추출할 이미지의 경로
        :return: 추출된 메타데이터
        """
        self.logger.info(f"{image_path}에서 메타데이터 추출 중")
        return self.metadata_processor.process(image_path)

    def _generate_caption(self, image_path: str, metadata: Dict[str, Any]) -> str:
        """
        이미지에 대한 캡션을 생성합니다.
        
        :param image_path: 캡션을 생성할 이미지의 경로
        :param metadata: 이미지의 메타데이터
        :return: 생성된 캡션
        """
        self.logger.info(f"{image_path}에 대한 캡션 생성 중")
        return self.caption_generator.generate_caption(image_path, metadata)

    def _construct_result(self, image_path: str, metadata: Dict[str, Any], caption: str) -> Dict[str, Any]:
        """
        처리 결과를 구성합니다.
        
        :param image_path: 처리된 이미지의 경로
        :param metadata: 추출된 메타데이터
        :param caption: 생성된 캡션
        :return: 처리 결과를 포함한 딕셔너리
        """
        return {
            'image_path': image_path,
            'metadata': metadata,
            'caption': caption
        }
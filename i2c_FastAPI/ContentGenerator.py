import logging
from openai import OpenAI
from datetime import datetime
from writing_styles import STYLE_SPECIFIC_INSTRUCTIONS
from writing_tones import WRITING_TONES

class ContentGenerator:
    def __init__(self, openai_api_key):
        self.client = OpenAI(api_key=openai_api_key)
        self.logger = logging.getLogger(__name__)

    def create_story(self, image_data_list, user_context, writing_style, writing_length, temperature, user_info):
        self.logger.info(f"User info type: {type(user_info)}")
        self.logger.info(f"User info keys: {user_info.keys()}")
        self.logger.info(f"Creating story with parameters: style={writing_style}, length={writing_length}, temperature={temperature}")
        self.logger.info(f"Received image_data_list: {image_data_list}")
        self.logger.info(f"Received user_context: {user_context}")
        self.logger.info(f"Received user_info: {user_info}")
        
        # 이미지 데이터 정렬
        sorted_image_data = self._sort_image_data(image_data_list)
        self.logger.info(f"Sorted image data: {sorted_image_data}")
        
        # 프롬프트 생성
        prompt = self._create_story_prompt(sorted_image_data, user_context, writing_style, writing_length, user_info)
        self.logger.info(f"Generated prompt: {prompt}")

        # OpenAI API를 사용하여 스토리 생성
        try:
            response = self._generate_openai_response(prompt, writing_length, temperature)
            self.logger.info("OpenAI API response received successfully")
            return response.choices[0].message.content, user_info.get('writing_tone', 'default')
        except Exception as e:
            self.logger.error(f"스토리 생성 중 오류 발생: {e}")
            self.logger.exception(e)
            raise

    def create_hashtags(self, story):
        # 해시태그 생성을 위한 프롬프트 작성
        prompt = self._create_hashtag_prompt(story)

        try:
            response = self._generate_openai_response(prompt, 100, 0.2)
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"해시태그 생성 중 오류 발생: {e}")
            return "해시태그를 생성할 수 없습니다."

    def _sort_image_data(self, image_data_list):
        # 이미지 데이터를 날짜순으로 정렬
        self.logger.info(f"Sorting image data: {image_data_list}")
        sorted_data = sorted(image_data_list, key=lambda x: self._parse_date(
            x.get('metadata', {}).get('labeled_exif', {}).get('Date/Time', '1900-01-01 00:00:00')
        ))
        self.logger.info(f"Sorted image data: {sorted_data}")
        return sorted_data

    def _parse_date(self, date_string):
        # 날짜 문자열을 datetime 객체로 변환
        self.logger.info(f"Parsing date: {date_string}")
        try:
            # 여러 가능한 날짜 형식을 시도
            for fmt in ('%Y:%m:%d %H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y:%m:%d'):
                try:
                    return datetime.strptime(date_string, fmt)
                except ValueError:
                    continue
            # 모든 형식이 실패하면 기본값 반환
            self.logger.warning(f"Could not parse date: {date_string}. Using default.")
            return datetime.strptime('1900-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
        except Exception as e:
            self.logger.error(f"Error parsing date: {date_string}. Error: {str(e)}")
            return datetime.strptime('1900-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')

    def _create_story_prompt(self, sorted_image_data, user_context, writing_style, writing_length, user_info):
        context_prompt = f"사용자 제공 추가 정보: {user_context}" if user_context else "사용자가 제공한 추가 정보 없음"
        age = user_info.get('age', 'N/A')
        gender = user_info.get('gender', 'N/A')
        writing_tone = user_info.get('writing_tone', 'N/A')
        writing_tone_description = user_info.get('writing_tone_description', 'N/A')
        
        # writing_tone의 value 값 중 두 번째 값을 가져옵니다.
        tone_name = WRITING_TONES.get(writing_tone, ['', '', ''])[1]
        
        user_info_prompt = f"""저는 {age}세 {gender}입니다. 아래 지시사항에 따라 글을 작성하세요:
            1. [{tone_name}] 문체를 사용하세요.
            2. {writing_style} 형식으로 글을 작성하세요.
            3. 문체 특징: {writing_tone_description}
            이 특징들을 고려하여 자연스럽고 일관된 글을 작성해주세요."""

        prompt = f"""다음 정보를 바탕으로 {writing_style}을 작성해주세요:
            1. 컨텍스트: {context_prompt}
            2. 글 길이: 정확히 {writing_length}자 (±10자 오차 허용)
            3. 추가 정보: {user_context}
            4. 작성자 정보:
            {user_info_prompt}

            주요 지침:
            1. 제공된 이미지와 메타데이터를 기반으로 내용을 구성하세요.
            2. {tone_name} 문체를 일관되게 유지하며, 적절한 어휘와 표현을 사용하세요.
            3. 이미지와 메타데이터의 정보를 문체에 맞게 자연스럽게 표현하세요.
            4. 전체적으로 통일성 있는 하나의 글로 작성하세요.
            5. 반드시 지정된 글자 수({writing_length}자) 내에서 완결된 글을 작성하세요.
            6. 글자 수에 맞추기 위해 내용을 적절히 조절하고, 필요한 경우 덜 중요한 세부사항은 생략하세요.
            7. 글의 마지막 문장이 완전한 문장으로 끝나도록 하세요.
            8. 글자 수가 부족하거나 초과하지 않도록 주의깊게 관리하세요.

            이미지 정보:
            """

        for idx, image_data in enumerate(sorted_image_data, 1):
            prompt += self._create_image_prompt(idx, image_data)

        prompt += f"""{STYLE_SPECIFIC_INSTRUCTIONS[writing_style]}

        중요: 모든 이미지를 종합하여 하나의 연결된 글을 작성해주세요. 각 이미지의 주요 객체나 장면에 초점을 맞추되, 전체적인 맥락을 고려하여 글을 작성해주세요.
        마지막으로, 글자 수를 다시 한 번 확인하고 정확히 {writing_length}자(±10자)로 조정하세요. 필요하다면 내용을 약간 줄이거나 확장하여 글자 수를 맞추세요.
        """
        return prompt

    def _create_image_prompt(self, idx, image_data):
        # 개별 이미지에 대한 프롬프트 생성
        image_prompt = f"""
        이미지 {idx}:
        캡션: {image_data.get('caption', 'N/A')}
        메타데이터:
        """
        metadata = image_data.get('metadata', {})
        labeled_exif = metadata.get('labeled_exif', {})
        location_info = metadata.get('location_info', {})
        
        if 'Date/Time' in labeled_exif:
            date_time = self._parse_date(labeled_exif['Date/Time'])
            image_prompt += f"""
            - 날짜/시간: {date_time.strftime('%Y-%m-%d %H:%M:%S')}
            - 위치: {location_info.get('full_address', 'N/A')}
            - 국가: {location_info.get('country', 'N/A')}
            - 도시: {location_info.get('city', 'N/A')}
            """
        else:
            image_prompt += "- 메타데이터 없음"
        return image_prompt

    def _create_hashtag_prompt(self, story):
        # 해시태그 생성을 위한 프롬프트 작성
        return f"""
        다음 {len(story)}자 길이의 글을 바탕으로 5개의 관련 해시태그를 생성해주세요:

        {story[:100]}...  # 글의 처음 100자만 표시

        해시태그는 '#' 기호로 시작하고, 각각 쉼표로 구분해주세요.
        """

    def _generate_openai_response(self, prompt, max_tokens, temperature):
        # OpenAI API를 사용하여 응답 생성
        self.logger.info(f"Sending request to OpenAI API with max_tokens={max_tokens}, temperature={temperature}")
        return self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "당신은 여러 이미지의 정보를 종합하여 하나의 연결된 글을 작성하는 전문 작가입니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
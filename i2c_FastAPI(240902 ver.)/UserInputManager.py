from writing_styles import STYLE_SPECIFIC_INSTRUCTIONS
from writing_tones import WRITING_TONES
import os

class UserInputManager:
    @staticmethod
    def get_writing_style():
        """사용자로부터 글쓰기 스타일을 입력받습니다."""
        styles = list(STYLE_SPECIFIC_INSTRUCTIONS.keys())
        print("글쓰기 스타일을 선택해주세요:")
        for idx, style in enumerate(styles, 1):
            print(f"{idx}. {style}")
        
        return UserInputManager._get_valid_input(
            prompt=f"선택 (1-{len(STYLE_SPECIFIC_INSTRUCTIONS)}): ",
            validation_func=lambda x: x.isdigit() and 1 <= int(x) <= len(STYLE_SPECIFIC_INSTRUCTIONS),
            error_message=f"잘못된 선택입니다. 1부터 {len(STYLE_SPECIFIC_INSTRUCTIONS)} 사이의 번호를 입력해주세요.",
            transform_func=lambda x: styles[int(x) - 1]
        )

    @staticmethod
    def get_writing_length():
        """사용자로부터 원하는 글의 길이를 입력받습니다."""
        return UserInputManager._get_valid_input(
            prompt="원하는 글의 길이를 100자 단위로 입력해주세요 (최대 5000자): ",
            validation_func=lambda x: x.isdigit() and 100 <= int(x) <= 5000 and int(x) % 100 == 0,
            error_message="100에서 5000 사이의 100의 배수를 입력해주세요.",
            transform_func=int
        )

    @staticmethod
    def get_user_context():
        """사용자로부터 추가 정보를 입력받습니다."""
        print("\n모든 이미지에 대한 추가 정보를 입력해주세요.")
        print("예: 인물의 이름, 특별한 상황, 이벤트 등")
        print("입력하지 않으려면 엔터를 눌러주세요.")
        return input("추가 정보: ").strip()

    @staticmethod
    def get_temperature():
        """사용자로부터 창의성 수준(temperature)을 입력받습니다."""
        return UserInputManager._get_valid_input(
            prompt="창의성 수준을 입력해주세요 (0 ~ 10, 0: 매우 일관된, 10: 매우 창의적): ",
            validation_func=lambda x: x.replace('.', '', 1).isdigit() and 0 <= float(x) <= 10,
            error_message="0에서 10 사이의 숫자를 입력해주세요.",
            transform_func=lambda x: float(x) / 10
        )

    @staticmethod
    def get_user_info():
        """사용자의 나이, 성별, 글쓰기 톤을 입력받습니다."""
        age = input("사용자의 나이를 입력해주세요: ")
        
        gender = UserInputManager._get_valid_input(
            prompt="사용자의 성별을 선택해주세요 (1: 남성, 2: 여성): ",
            validation_func=lambda x: x in ['1', '2'],
            error_message="잘못된 선택입니다. 1 또는 2를 입력해주세요.",
            transform_func=lambda x: "남성" if x == '1' else "여성"
        )
        
        print("\n문체를 선택해주세요:")
        for key, (style, description, _) in WRITING_TONES.items():
            print(f"{key}: {style} - {description}")
        
        writing_tone_choice = UserInputManager._get_valid_input(
            validation_func=lambda x: x.isdigit() and 1 <= int(x) <= len(WRITING_TONES),
            prompt="문체 번호를 선택해주세요(기본은 1번을 선택하세요): ",
            error_message=f"잘못된 선택입니다. 1부터 {len(WRITING_TONES)} 사이의 번호를 입력해주세요."
        )
        
        writing_tone, _, writing_tone_description = WRITING_TONES[writing_tone_choice]
        return age, gender, writing_tone, writing_tone_description

    @staticmethod
    def get_save_info():
        """파일 저장 정보를 입력받습니다."""
        while True:
            save_directory = input("결과를 저장할 디렉토리 경로를 입력하세요: ").strip()
            if not os.path.isdir(save_directory):
                print("유효하지 않은 디렉토리입니다. 다시 시도해주세요.")
                continue
            filename = input("저장할 파일 이름을 입력하세요 (확장자 제외): ").strip()
            if not filename:
                print("파일 이름을 입력해야 합니다.")
                continue
            return save_directory, filename

    @staticmethod
    def confirm_action(prompt):
        """사용자에게 작업 수행 여부를 확인합니다."""
        return UserInputManager._get_valid_input(
            prompt=f"{prompt} (y/n): ",
            validation_func=lambda x: x.lower() in ['y', 'n'],
            error_message="잘못된 입력입니다. y 또는 n을 입력하세요.",
            transform_func=lambda x: x.lower() == 'y'
        )

    @staticmethod
    def get_user_choice(prompt, options):
        """사용자에게 여러 옵션 중 하나를 선택하도록 합니다."""
        print(f"{prompt} ({'/'.join(options)}): ")
        return UserInputManager._get_valid_input(
            prompt="선택: ",
            validation_func=lambda x: x in options,
            error_message=f"잘못된 선택입니다. {', '.join(options)} 중 하나를 입력하세요."
        )

    @staticmethod
    def _get_valid_input(prompt, validation_func, error_message, transform_func=lambda x: x):
        """유효한 입력을 받을 때까지 사용자에게 입력을 요청합니다."""
        while True:
            user_input = input(prompt)
            if validation_func(user_input):
                return transform_func(user_input)
            print(error_message)
from typing import Dict

class Translator:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.translations: Dict[str, Dict[str, str]] = {
            'en': {
                'app_title': 'Engineer Management System',
                'basic_info': 'Basic Information',
                'qualifications': 'Qualifications',
                'education': 'Education',
                'experience': 'Experience',
                'training': 'Training',
                'add': 'Add',
                'edit': 'Edit',
                'delete': 'Delete',
                'save': 'Save',
                'cancel': 'Cancel',
                'confirm': 'Confirm',
                'error': 'Error',
                'warning': 'Warning',
                'success': 'Success',
                'name': 'Name',
                'birth_date': 'Birth Date',
                'address': 'Address',
                'company': 'Company',
                'technical_grade': 'Technical Grade',
                'required_fields': 'Name and Birth Date are required!',
                'select_edit': 'Please select an engineer to edit!',
                'select_delete': 'Please select an engineer to delete!',
                'confirm_delete': 'Are you sure you want to delete this engineer?',
                'engineer_list': 'Engineer List',
            },
            'ko': {
                'app_title': '기술자 관리 시스템',
                'basic_info': '기본정보',
                'qualifications': '자격증',
                'education': '학력',
                'experience': '경력',
                'training': '교육이수',
                'add': '추가',
                'edit': '수정',
                'delete': '삭제',
                'save': '저장',
                'cancel': '취소',
                'confirm': '확인',
                'error': '오류',
                'warning': '경고',
                'success': '성공',
                'name': '이름',
                'birth_date': '생년월일',
                'address': '주소',
                'company': '회사',
                'technical_grade': '기술등급',
                'required_fields': '이름과 생년월일은 필수 입력사항입니다!',
                'select_edit': '수정할 기술자를 선택해주세요!',
                'select_delete': '삭제할 기술자를 선택해주세요!',
                'confirm_delete': '정말로 이 기술자를 삭제하시겠습니까?',
                'engineer_list': '기술자 목록',
            }
        }
        self.current_language = 'ko'
    
    def translate(self, key: str) -> str:
        return self.translations[self.current_language].get(key, key)
    
    def set_language(self, language: str):
        if language in self.translations:
            self.current_language = language
    
    def get_available_languages(self) -> list:
        return list(self.translations.keys())

# Create a singleton instance
translator = Translator()

import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경변수 검증
def validate_api_key():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API 키가 설정되지 않았습니다.")
    return api_key

def validate_sheets_credentials():
    creds = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
    if not creds:
        raise ValueError("Google Sheets 인증 정보가 설정되지 않았습니다.")
    return creds

# 환경변수 (검증 추가)
try:
    OPENAI_API_KEY = validate_api_key()
    GOOGLE_SHEETS_CREDENTIALS = validate_sheets_credentials()
    SHEET_ID = os.getenv("SHEET_ID")
except ValueError as e:
    print(f"환경변수 오류: {e}")
    raise

# 감정 리스트 (필요한 경우 수정)
EMOTIONS = [
    "스트레스 해소",
    "좋은 기분",
    "피곤한 날",
    "날씨 관련",
    "간단한 식사"
]

# 구글 시트 칼럼 정의
SHEET_COLUMNS = {
    'category': '카테고리',
    'emotion1': '감정1',
    'emotion2': '감정2',
    'menu': '메뉴',
    'restaurant_name': '식당명',
    'address': '주소',
    'review': '한줄평',
    'pay': '식권대장'  # Y/N 또는 y/n
}

# 시트 범위 정의
SHEET_RANGE = '시트1!A:H'

# 구글 시트 칼럼 순서 (A부터 H까지)
SHEET_COLUMN_ORDER = [
    'category',
    'emotion1',
    'emotion2',
    'menu',
    'restaurant_name',
    'address',
    'review',
    'pay'
]
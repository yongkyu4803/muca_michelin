import pandas as pd
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from config.config import SHEET_ID, GOOGLE_SHEETS_CREDENTIALS, SHEET_COLUMNS

class SheetsService:
    def __init__(self):
        self.sheet_id = SHEET_ID
        # 서비스 계정 인증 정보 사용
        credentials_dict = json.loads(GOOGLE_SHEETS_CREDENTIALS)
        self.creds = Credentials.from_service_account_info(
            credentials_dict,
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        self.service = build('sheets', 'v4', credentials=self.creds)
        self.sheet = self.service.spreadsheets()

    def get_data(self, range_name='시트1!A:H'):
        """구글 시트에서 데이터를 가져옵니다."""
        try:
            result = self.sheet.values().get(
                spreadsheetId=self.sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return pd.DataFrame(columns=SHEET_COLUMNS.values())
                
            # 첫 번째 행을 헤더로 사용하여 데이터프레임 생성
            df = pd.DataFrame(values[1:], columns=values[0])
            return df
            
        except Exception as e:
            print(f"Error fetching data from sheets: {str(e)}")
            return pd.DataFrame(columns=SHEET_COLUMNS.values())

    def get_pay_service_restaurants(self):
        """식권대장 사용 가능한 식당 목록을 가져옵니다."""
        try:
            df = self.get_data()  # 'A1:H100' 대신 기본값 사용
            # pay 칼럼이 'Y'인 식당만 필터링
            pay_restaurants = df[df['식권대장'] == 'Y']['식당명'].tolist()
            return pay_restaurants
            
        except Exception as e:
            print(f"Error getting pay service restaurants: {str(e)}")
            return []

    def get_alternative_restaurant(self, category, pay_service_only=False):
        """대체 식당을 추천합니다."""
        try:
            df = self.get_data()  # 'A1:H100' 대신 기본값 사용
            
            # 기본 필터: 같은 카테고리
            mask = df['카테고리'] == category
            
            # 식권대장 사용 가능 여부 필터
            if pay_service_only:
                mask &= df['식권대장'] == 'Y'
            
            filtered_df = df[mask]
            
            if filtered_df.empty:
                return None
            
            # 랜덤하게 하나 선택
            selected = filtered_df.sample(n=1).iloc[0]
            
            return {
                'category': selected['카테고리'],
                'emotion1': selected['감정1'],
                'emotion2': selected['감정2'],
                'menu': selected['메뉴'],
                'restaurant_name': selected['식당명'],
                'address': selected['주소'],
                'review': selected['한줄평']
            }
            
        except Exception as e:
            print(f"Error getting alternative restaurant: {str(e)}")
            return None
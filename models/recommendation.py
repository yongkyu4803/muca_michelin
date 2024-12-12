import streamlit as st
from services.gpt_service import GPTService
from services.sheets_service import SheetsService

class RecommendationEngine:
    def __init__(self):
        self.gpt_service = GPTService()
        self.sheets_service = SheetsService()

    def get_recommendation(self, status, use_pay_service=False):
        """
        사용자의 상태를 기반으로 식당을 추천합니다.
        """
        try:
            # 먼저 식당 데이터를 가져옴
            restaurants_data = self.sheets_service.get_data('시트1!A1:H100')
            
            # 식권대장 필터링이 필요한 경우, 미리 필터링
            if use_pay_service:
                restaurants_data = restaurants_data[
                    restaurants_data['식권대장'].str.upper() == 'Y'
                ]
                if restaurants_data.empty:
                    return {
                        'restaurant_name': '추천 실패',
                        'menu': '추천 실패',
                        'address': '추천 실패',
                        'review': '식권대장 사용 가능한 식당이 없습니다.'
                    }
            
            # GPT로부터 추천 받기
            gpt_response = self.gpt_service.get_recommendation(status, restaurants_data)
            
            # GPT 응답 파싱
            recommendation = self._parse_gpt_response(gpt_response)
            
            if not recommendation:
                raise Exception("GPT 응답을 파싱할 수 없습니다.")
            
            return recommendation
            
        except Exception as e:
            return {
                'restaurant_name': '추천 실패',
                'menu': '추천 실패',
                'address': '추천 실패',
                'review': '죄송합니다. 추천 과정에서 오류가 발생했습니다.'
            }

    def _parse_gpt_response(self, response):
        """GPT 응답을 파싱하여 딕셔너리로 변환합니다."""
        try:
            if not isinstance(response, str):
                return None
                
            lines = response.strip().split('\n')
            result = {}
            
            # 필수 키 목록
            required_keys = {'카테고리', '메뉴', '식당명', '주소', '한줄평'}
            found_keys = set()
            
            for line in lines:
                line = line.strip()
                if not line or ':' not in line:
                    continue
                    
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                if key in required_keys:
                    found_keys.add(key)
                    
                # 키 이름 매핑
                key_mapping = {
                    '카테고리': 'category',
                    '감정1': 'emotion1',
                    '감정2': 'emotion2',
                    '메뉴': 'menu',
                    '식당명': 'restaurant_name',
                    '주소': 'address',
                    '한줄평': 'review'
                }
                
                if key in key_mapping:
                    result[key_mapping[key]] = value.strip('[]')
            
            # 모든 필수 키가 있는지 확인
            if not required_keys.issubset(found_keys):
                return None
                
            return result
            
        except Exception as e:
            return None

    def _filter_by_pay_service(self, recommendation):
        """식권대장 사용 가능한 식당만 필터링합니다."""
        try:
            if not recommendation or 'restaurant_name' not in recommendation:
                return None
                
            # 구글 시트에서 식권대장 사용 가능한 식당 목록 가져오기
            pay_service_restaurants = self.sheets_service.get_pay_service_restaurants()
            
            # 추천된 식당이 식권대장 사용 가능한 경우
            if recommendation['restaurant_name'] in pay_service_restaurants:
                return recommendation
                
            # 사용 불가능한 경우 다른 식당 추천
            category = recommendation.get('category')
            if category:
                return self.sheets_service.get_alternative_restaurant(
                    category,
                    pay_service_only=True
                )
            return None
            
        except Exception as e:
            return None
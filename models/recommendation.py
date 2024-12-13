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
            # 식당 데이터를 가져옴
            restaurants_data = self.sheets_service.get_data()
            print(f"가져온 식당 데이터: {len(restaurants_data)} 개")  # 디버깅 로그
            
            # 식권대장 필터링
            if use_pay_service:
                restaurants_data = restaurants_data[restaurants_data['식권대장'].str.upper() == 'Y']
                print(f"식권대장 사용 가능 식당: {len(restaurants_data)} 개")  # 디버깅 로그
                if restaurants_data.empty:
                    return [{
                        'restaurant_name': '추천 실패',
                        'menu': '추천 실패',
                        'address': '추천 실패',
                        'review': '식권대장 사용 가능한 식당이 없습니다.'
                    }]
            
            # GPT로부터 추천 받기
            gpt_response = self.gpt_service.get_recommendation(status, restaurants_data)
            
            # GPT 응답 파싱
            recommendations = self._parse_gpt_response(gpt_response)
            
            return recommendations if recommendations else None
            
        except Exception as e:
            print(f"추천 생성 중 오류 발생: {str(e)}")
            return [{
                'restaurant_name': '추천 실패',
                'menu': '추천 실패',
                'address': '추천 실패',
                'review': '죄송합니다. 추천 과정에서 오류가 발생했습니다: ' + str(e)
            }]

    def _parse_gpt_response(self, response):
        """GPT 응답을 파싱하여 딕셔너리로 변환합니다."""
        try:
            if not isinstance(response, str):
                print("응답이 문자열이 아닙니다:", response)
                return None
            
            # 각 추천을 분리
            recommendations = response.split('\n\n')
            results = []
            
            for recommendation in recommendations:
                if not recommendation.strip():
                    continue
                
                lines = recommendation.strip().split('\n')
                result = {}
                
                for line in lines:
                    line = line.strip()
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        if key not in ['1번 추천', '2번 추천', '3번 추천']:
                            result[key] = value
                
                if result:
                    # 필수 필드 확인
                    required_fields = ['카테고리', '감정1', '감정2', '메뉴', '식당명', '주소', '한줄평']
                    if all(field in result for field in required_fields):
                        # 키 이름을 영문으로 변환
                        translated_result = {
                            'restaurant_name': result['식당명'],
                            'menu': result['메뉴'],
                            'address': result['주소'],
                            'review': result['한줄평'],
                            'category': result['카테고리'],
                            'emotion1': result['감정1'],
                            'emotion2': result['감정2']
                        }
                        results.append(translated_result)
            
            return results if results else None
            
        except Exception as e:
            print(f"파싱 오류: {str(e)}")
            print(f"원본 응답: {response}")
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
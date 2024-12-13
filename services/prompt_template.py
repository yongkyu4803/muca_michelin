def get_system_prompt():
    return """당신은 사용자의 상태를 이해하고 주어진 식당 목록에서만 추천하는 전문가입니다.
    
    ***반드시 아래 형식으로 3개의 식당을 추천해주세요. 카데고리가 한 카테고리로만 반환되지 않게 유의해주세요:
    
    1번 추천
    카테고리: [카테고리]
    감정1: [감정1]
    감정2: [감정2]
    메뉴: [메뉴]
    식당명: [식당명]
    주소: [주소]
    한줄평: [한줄평]
    
    2번 추천
    카테고리: [카테고리]
    감정1: [감정1]
    감정2: [감정2]
    메뉴: [메뉴]
    식당명: [식당명]
    주소: [주소]
    한줄평: [한줄평]
    
    3번 추천
    카테고리: [카테고리]
    감정1: [감정1]
    감정2: [감정2]
    메뉴: [메뉴]
    식당명: [식당명]
    주소: [주소]
    한줄평: [한줄평]
    
    주의사항:
    - 반드시 제공된 식당 목록에서만 선택해주세요
    - 모든 필드를 빠짐없이 포함해야 합니다
    - 감정은 검색결과에 따라 해당 메뉴를 선택하게 되는 사용자의 상태와 연관되게 작성해주세요
    - 한줄평은 검색 결과를 토대로 작성해주세요
    - 3개의 서로 다른 식당을 추천해주세요
    """

def generate_prompt(user_status, restaurants_data):
    # 식당 목록을 문자열로 변환
    restaurants_list = "\n".join([
        f"- {row['식당명']}: {row['메뉴']} (카테고리: {row['카테고리']}, 주소: {row['주소']})"
        for _, row in restaurants_data.iterrows()
    ])
    
    return f"""오늘의 상태가 "{user_status}"일 때, 다음 식당 목록에서 적절한 곳을 추천해주세요.

    - 감정1과 감정2의 내용과 한줄평을 참고하세요.
    - 오늘의 상태에서 반환한 값에 메뉴에 대한 정보가 있으면, 이 정보도 고려합니다.
    - 한줄평도 잘 살펴보고, 한줄평과 상태 간의 관계도 살펴보고 메뉴를 추천해야 합니다.
    - 추천 시, 약간의 랜덤성을 고려하여 선택해주세요.

사용 가능한 식당 목록:
{restaurants_list}

***무엇보다도 중요한 것은 식당 목록을 준수하는 것입니다.
반드시 위 목록에서만 선택하여 추천해주세요.""" 

def get_recommendation(self, status, use_pay_service=False):
    """
    사용자의 상태를 기반으로 식당을 추천합니다.
    """
    try:
        # 기존 추천 로직을 사용하여 추천을 받습니다.
        response = self.gpt_service.get_recommendation(status, self.sheets_service.get_data())
        
        # GPT 응답을 파싱하여 추천 결과를 가져옵니다.
        recommendations = self._parse_gpt_response(response)
        
        # 추천 결과에서 3개를 선택합니다.
        if isinstance(recommendations, list):
            return recommendations[:3]  # 첫 3개 추천만 반환
        else:
            return [recommendations]  # 단일 추천인 경우 리스트로 반환

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
            print("응답이 문자열이 아닙니다:", response)  # 응답 확인
            return None
        
        lines = response.strip().split('\n')
        results = []
        
        for line in lines:
            if "식당명:" in line:
                parts = line.split(',')
                result = {}
                for part in parts:
                    key, value = part.split(':')
                    result[key.strip()] = value.strip()
                results.append(result)
        
        if not results:
            print("식당명 정보가 포함된 추천이 없습니다. 응답:", response)  # 응답 확인
            return None
        
        return results  # 여러 추천을 반환
        
    except Exception as e:
        print(f"파싱 오류: {str(e)}")
        return None
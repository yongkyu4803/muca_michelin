def get_system_prompt():
    return """당신은 사용자의 상태를 이해하고 주어진 식당 목록에서만 추천하는 전문가입니다.
    반드시 다음 형식으로 응답해주세요:
    카테고리: [카테고리]
    감정1: [감정1]
    감정2: [감정2]
    메뉴: [메뉴]
    식당명: [식당명]
    주소: [주소]
    한줄평: [한줄평]
    
    주의사항:
    - 반드시 제공된 식당 목록에서만 선택해주세요
    - 모든 필드를 반드시 포함해주세요
    - 각 필드는 콜론(:) 뒤에 한 줄로 작성해주세요
    - 대괄호([])는 제외하고 실제 내용만 작성해주세요"""

def generate_prompt(user_status, restaurants_data):
    # 식당 목록을 문자열로 변환
    restaurants_list = "\n".join([
        f"- {row['식당명']}: {row['메뉴']} (카테고리: {row['카테고리']}, 주소: {row['주소']})"
        for _, row in restaurants_data.iterrows()
    ])
    
    return f"""오늘의 상태가 "{user_status}"일 때, 다음 식당 목록에서 적절한 곳을 추천해주세요.

사용 가능한 식당 목록:
{restaurants_list}

위 목록에서만 선택하여 추천해주세요.""" 
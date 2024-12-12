from openai import OpenAI
from config.config import OPENAI_API_KEY
from services.prompt_template import generate_prompt, get_system_prompt

class GPTService:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        
    def get_recommendation(self, status, restaurants_data):
        """
        GPT를 사용하여 사용자의 상태에 맞는 추천을 받습니다.
        """
        try:
            # 프롬프트 생성
            user_prompt = generate_prompt(status, restaurants_data)
            system_prompt = get_system_prompt()
            
            # GPT API 호출
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # 응답 추출 및 검증
            recommendation = response.choices[0].message.content.strip()
            if not all(key in recommendation for key in ['카테고리:', '메뉴:', '식당명:', '주소:', '한줄평:']):
                raise ValueError("GPT 응답이 올바른 형식이 아닙니다.")
                
            return recommendation
            
        except Exception as e:
            print(f"Error in GPT service: {str(e)}")
            raise Exception(f"GPT 서비스 오류가 발생했습니다: {str(e)}")
import streamlit as st
from config.config import EMOTIONS
from services.sheets_service import SheetsService
from services.gpt_service import GPTService
from models.recommendation import RecommendationEngine

def set_page_config():
    st.set_page_config(
        page_title="뮤카슐랭",
        page_icon="🍽️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

def header():
    st.title("🍽️ 뮤카슐랭")
    st.markdown("##### 오늘 점심은 어디서 먹을까?")
    st.markdown("AI 추천이라 '딱 맞춤'이 아닐수도 있어요^^")
    st.markdown("---")

def user_input_section():
    col1, col2 = st.columns([3, 1])
    
    with col1:
        status = st.text_input(
            "상태 입력",
            placeholder="오늘의 기분이나 점심 메뉴 고민을 자유롭게 입력해주세요 (예: 따뜻한 국물이 생각나는 날)",
            label_visibility="collapsed"
        )
    
    with col2:
        use_pay_service = st.checkbox(
            "식권대장 사용 가능한 곳만 보기", 
            value=False
        )
    
    return status, use_pay_service

def show_recommendation(result, is_main=False):
    """추천 결과를 카드 형태로 보여줍니다."""
    try:
        # 카드 스타일 CSS
        st.markdown("""
        <style>
        .restaurant-card {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #eee;
            height: 100%;
        }
        .restaurant-card.main {
            background-color: #ffffff;
            border: 1px solid #1f77b4;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .restaurant-card.sub {
            transform: scale(0.8);
            opacity: 0.9;
        }
        .restaurant-header {
            color: #1f77b4;
            margin-bottom: 10px;
        }
        .restaurant-header.main h3 {
            color: #1f4068;
        }
        .restaurant-info {
            margin: 5px 0;
        }
        .restaurant-review {
            background-color: #e8f4f8;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
        }
        .restaurant-review.main {
            background-color: #e3f2fd;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # 카드 내용
        card_class = "main" if is_main else "sub"
        st.markdown(f"""
        <div class="restaurant-card {card_class}">
            <div class="restaurant-header {card_class}">
                <h3>🏪 {result.get('restaurant_name', '정보 없음')}</h3>
                <p><i>{result.get('category', '')}</i></p>
            </div>
            <div class="restaurant-info">
                <p>🍽️ {result.get('menu', '정보 없음')}</p>
                <p>📍 {result.get('address', '정보 없음')}</p>
            </div>
            <div class="restaurant-review {card_class}">
                💡 {result.get('review', '')}
            </div>
        </div>
        """, unsafe_allow_html=True)
                
    except Exception as e:
        st.error("추천 결과를 표시하는 중 오류가 발생했습니다.")

def footer():
    """푸터 섹션을 추가합니다."""
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #666; padding: 20px;">
            <p>Made with ❤️ by GQ_ykpark</p>
            <p style="font-size: 0.8em;">© 2024 뮤카슐랭. All rights reserved.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def main():
    set_page_config()
    header()
    
    # 사용자 입력 섹션
    status, use_pay_service = user_input_section()
    
    # 추천 버튼과 결과 표시
    if st.button("메뉴 추천받기", type="primary", use_container_width=True):
        if not status:
            st.warning("오늘의 상태를 입력해주세요!")
        else:
            with st.spinner("추천을 생성하는 중..."):
                recommendation_engine = RecommendationEngine()
                recommendations = recommendation_engine.get_recommendation(status, use_pay_service)
                
                # 3개의 카드를 한 줄에 표시
                cols = st.columns([4, 3, 3])  # 메인 카드는 더 넓게
                if recommendations:
                    # 메인 카드
                    with cols[0]:
                        show_recommendation(recommendations[0], is_main=True)
                    
                    # 서브 카드들
                    if len(recommendations) > 1:
                        for idx, recommendation in enumerate(recommendations[1:3], 1):
                            with cols[idx]:
                                show_recommendation(recommendation, is_main=False)
    
    # 하단 정보
    st.markdown("---")
    
    with st.expander("ℹ️ 서비스 소개"):
        st.write("""
        뮤카슐랭은 당신의 기분과 상태를 이해하고, 
        그에 맞는 최적의 메뉴와 식당을 추천해드립니다.
        AI가 당신의 상태를 분석하여 맞춤형 추천을 제공합니다.
        """)
    
    with st.expander("📝 식당을 추천해주세요"):
        st.write("""
        새로운 식당을 추가하거나 기존 정보를 수정하려면 
        아래 구글 시트를 이용해주세요.
        """)
        sheet_url = "https://docs.google.com/spreadsheets/d/1exK2EmIYXRsY06sCVix2WyLNSYneY6erjjStMvmqTiY/edit?gid=0"
        st.markdown(f"[📝 식당 정보 시트 열기]({sheet_url})")
        
        st.markdown("---")
        st.markdown("##### 구글 시트에 새로운 식당을 추가할 때는 다음 형식을 따라주세요:")
        st.markdown("""
        - **카테고리**: 한식, 중식, 일식 등
        - **감정1, 감정2**: 이 식당에 어울리는 감정/상황 (예: 피곤한 날, 스트레스 받는 날)
        - **메뉴**: 대표 메뉴 (여러 개인 경우 쉼표로 구분)
        - **식당명**: 식당 이름
        - **주소**: 식당 위치
        - **한줄평**: 식당 특징이나 추천 이유
        - **식권대장**: Y 또는 N (대소문자 구분 없음)
        
        💡 입력한 정보는 실시간으로 반영됩니다.
        """)
    
    # 푸터 추가
    footer()

if __name__ == "__main__":
    main()
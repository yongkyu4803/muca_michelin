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

def show_recommendation(result):
    """추천 결과를 보여줍니다."""
    try:
        if not isinstance(result, dict):
            st.error("추천 결과를 생성할 수 없습니다.")
            return
            
        # 3개의 칼럼으로 정보 표시
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("🏪 추천 식당")
            st.markdown(f"#### {result.get('restaurant_name', '정보 없음')}")
            
        with col2:
            st.markdown("🍽️ 추천 메뉴")
            st.markdown(f"#### {result.get('menu', '정보 없음')}")
            
        with col3:
            st.markdown("📍 주소")
            st.markdown(f"#### {result.get('address', '정보 없음')}")
        
        # 추천 이유 (이모지를 텍스트 앞에 추가)
        if result.get('review'):
            st.info(f"💡 {result['review']}")
                
    except Exception as e:
        st.error("추천 결과를 표시하는 중 오류가 발생했습니다.")

def main():
    set_page_config()
    header()
    
    # 사용자 입력 섹션
    status, use_pay_service = user_input_section()
    
    # 추천 버튼
    if st.button("메뉴 추천받기", type="primary", use_container_width=True):
        if not status:
            st.warning("오늘의 상태를 입력해주세요!")
            return
            
        with st.spinner("맛있는 메뉴를 추천하고 있습니다..."):
            try:
                recommendation_engine = RecommendationEngine()
                result = recommendation_engine.get_recommendation(status, use_pay_service)
                show_recommendation(result)
                    
            except Exception as e:
                st.error("추천을 생성하는 중 오류가 발생했습니다.")
    
    # 하단 정보
    st.markdown("---")
    with st.expander("ℹ️ 서비스 소개"):
        st.write("""
        뮤카슐랭은 당신의 기분과 상태를 이해하고, 
        그에 맞는 최적의 메뉴와 식당을 추천해드립니다.
        AI가 당신의 상태를 분석하여 맞춤형 추천을 제공합니다.
        """)

if __name__ == "__main__":
    main()
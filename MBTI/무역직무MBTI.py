import streamlit as st
import streamlit.components.v1 as components
import time

st.set_page_config(page_title="글로벌 비즈니스(무역+경영) MBTI", page_icon="🌍", layout="centered")

# 세션 상태 초기화
if 'page' not in st.session_state:
    st.session_state.page = 0  # 0: 인트로 화면, 1~25: 질문 화면, 26: 결과 화면
if 'scores' not in st.session_state:
    st.session_state.scores = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}

# 📝 25가지 무역 & 경영 상황 질문 리스트
questions = [
    {"text": "Q1. 해외 전시회나 글로벌 컨퍼런스에 참석했다. 나의 행동은?", "choices": [("여기저기 부스를 돌며 새로운 사람들과 적극적으로 명함을 교환한다.", "E"), ("미리 타겟팅한 주요 기업 부스에 방문해 심도 있는 대화를 나눈다.", "I")]},
    {"text": "Q2. 새로운 경영 전략 프로젝트 팀의 리더가 되었다.", "choices": [("팀원들과 잦은 브레인스토밍 회의를 열어 의견을 주고받으며 아이디어를 발전시킨다.", "E"), ("먼저 혼자서 뼈대를 탄탄하게 기획한 뒤, 팀원들에게 공유하고 각자 업무를 배분한다.", "I")]},
    {"text": "Q3. 중요한 바이어/투자자와의 미팅 전날, 에너지를 충전하는 방법은?", "choices": [("동료들과 가볍게 저녁을 먹으며 미팅에 대한 기대감을 나눈다.", "E"), ("집에서 조용히 휴식을 취하며 내일 있을 시나리오를 혼자 그려본다.", "I")]},
    {"text": "Q4. 회사 휴게실에서 타 부서 사람을 만났을 때?", "choices": [("최근 업계 동향이나 가벼운 스몰톡을 먼저 자연스럽게 건넨다.", "E"), ("가볍게 눈인사만 하고 내 생각이나 하던 일에 집중한다.", "I")]},
    {"text": "Q5. 업무 중 스트레스를 받을 때 나는?", "choices": [("동료나 지인에게 상황을 이야기하며 풀거나 조언을 구한다.", "E"), ("혼자만의 시간을 가지며 문제를 객관적으로 정리해 본다.", "I")]},
    {"text": "Q6. 성공적인 수출 계약 체결 후, 축하 방식은?", "choices": [("팀 전체가 모여 왁자지껄한 회식을 하며 기쁨을 나눈다.", "E"), ("핵심 팀원들과 조촐하게 식사하거나, 개인적으로 성취감을 만끽한다.", "I")]},
    {"text": "Q7. 오픈형 오피스(칸막이 없음) vs 독립형 오피스 중 선호하는 환경은?", "choices": [("언제든 소통하고 협업하기 쉬운 활기찬 오픈형 오피스", "E"), ("내 업무에 깊이 몰입할 수 있는 조용한 독립형 오피스", "I")]},
    {"text": "Q8. 신규 해외 시장을 개척할 때 먼저 분석하는 자료는?", "choices": [("관세율, 물류비용, 과거 수출입 통계 등 구체적인 데이터", "S"), ("해당 국가의 향후 5년 소비 트렌드와 거시적인 경제 성장 가능성", "N")]},
    {"text": "Q9. 경영진에게 신사업 기획안을 보고할 때 중점을 두는 부분은?", "choices": [("실현 가능성, 예산, 예상 수익률 등 현실적인 팩트와 수치", "S"), ("사업이 가져올 혁신적인 가치와 회사의 장기적인 비전", "N")]},
    {"text": "Q10. 영문 계약서를 검토할 때 나의 스타일은?", "choices": [("조항 하나하나의 디테일과 숨겨진 리스크를 꼼꼼하게 체크한다.", "S"), ("전체적인 계약의 흐름과 양측의 핵심 이익이 잘 맞는지 큰 틀에서 본다.", "N")]},
    {"text": "Q11. 문제 상황(예: 매출 하락)을 해결하는 접근 방식은?", "choices": [("과거의 유사 사례와 검증된 매뉴얼을 참고하여 안정적인 해결책을 찾는다.", "S"), ("기존의 틀을 깨는 완전히 새로운 마케팅 방식이나 아이디어를 도입한다.", "N")]},
    {"text": "Q12. 다른 기업의 성공 사례를 볼 때 드는 생각은?", "choices": [("'저 회사는 마진율을 어떻게 저렇게 높였지?' (구체적 방법론)", "S"), ("'저 회사의 다음 스텝은 저런 방향이겠구나!' (미래 예측)", "N")]},
    {"text": "Q13. 회사에서 선호하는 업무 지시 형태는?", "choices": [("업무의 기한, 양식, 목표가 명확하고 구체적으로 떨어지는 지시", "S"), ("방향성만 주어지고 내 재량껏 크리에이티브하게 일할 수 있는 지시", "N")]},
    {"text": "Q14. 바이어와 단가 협상을 할 때 더 중요하게 생각하는 것은?", "choices": [("정확한 마진율 계산과 자사에 유리한 논리적인 계약 조건", "T"), ("당장의 이익보다는 장기적인 파트너십과 상호 간의 신뢰 구축", "F")]},
    {"text": "Q15. 팀원이 업무 실수를 해서 물류 비용이 추가로 발생했다. 나의 피드백은?", "choices": [("실수 원인을 명확히 분석하고 재발 방지 대책을 객관적으로 지시한다.", "T"), ("많이 당황했을 팀원을 먼저 다독인 후, 함께 해결책을 찾아본다.", "F")]},
    {"text": "Q16. 해외 파트너사를 최종 선정할 때 결정적인 기준은?", "choices": [("회사의 재무 건전성, 기술력, 객관적인 실적 데이터", "T"), ("담당자의 소통 능력, 열정, 우리 회사와의 가치관 핏(Fit)", "F")]},
    {"text": "Q17. 인사 고과 평가 기간이다. 내가 지향하는 평가 방식은?", "choices": [("오로지 실적과 KPI 달성률에 기반한 철저한 성과주의", "T"), ("실적도 중요하지만 팀워크 기여도와 개인의 노력 과정도 반영", "F")]},
    {"text": "Q18. 회사에서 구조조정이나 부서 통폐합 등 껄끄러운 결정을 내려야 한다면?", "choices": [("조직의 효율성과 생존을 위해 감정을 배제하고 빠르게 결단한다.", "T"), ("구성원들이 받을 상처와 사기 저하를 최소화할 방법을 깊이 고민한다.", "F")]},
    {"text": "Q19. '경영을 잘한다'의 진정한 의미는?", "choices": [("이윤을 극대화하고 시장 점유율을 압도적으로 차지하는 것", "T"), ("직원들이 행복하게 일하고 사회적으로 좋은 영향력을 미치는 것", "F")]},
    {"text": "Q20. 선적 지연이나 통관 보류 등 돌발 상황이 발생했을 때 나는?", "choices": [("미리 세워둔 위기관리 매뉴얼과 플랜 B, 플랜 C에 따라 체계적으로 대응한다.", "J"), ("상황에 맞춰 즉각적인 융통성을 발휘해 그 자리에서 최선의 해결책을 찾아낸다.", "P")]},
    {"text": "Q21. 연간 사업 계획(Business Plan)을 짤 때 나의 스타일은?", "choices": [("월별, 분기별 마일스톤과 예산을 아주 세밀하게 계획하고 그대로 실천한다.", "J"), ("큰 목표만 정해두고, 시장 상황 변화에 따라 유연하게 전략을 수정해 나간다.", "P")]},
    {"text": "Q22. 나의 책상(또는 PC 바탕화면) 상태는?", "choices": [("서류나 폴더가 주제별, 날짜별로 깔끔하게 정리되어 있어야 마음이 편하다.", "J"), ("조금 너저분해 보일 수 있지만, 나름의 질서가 있고 찾고자 하는 건 금방 찾는다.", "P")]},
    {"text": "Q23. 해외 출장 일정을 잡을 때?", "choices": [("미팅, 이동 시간, 식사 장소까지 분 단위로 철저하게 스케줄링한다.", "J"), ("필수 미팅 시간만 픽스해 두고, 나머지는 현지 상황에 따라 자유롭게 움직인다.", "P")]},
    {"text": "Q24. 오늘 해야 할 일이 산더미처럼 쌓여있다. 업무 시작 방식은?", "choices": [("To-Do 리스트를 작성하고 우선순위를 정해 순차적으로 하나씩 지워나간다.", "J"), ("가장 끌리거나 생각나는 일부터 시작하며 흐름에 몸을 맡긴다.", "P")]},
    {"text": "Q25. 경영자로서 선호하는 조직 문화는?", "choices": [("체계적인 보고 체계와 명확한 규율이 있는 안정적인 문화", "J"), ("형식에 얽매이지 않고 자유롭게 변화를 수용하는 애자일(Agile) 문화", "P")]}
]

# ---------------------------------------------------------
# 0. 인트로(시작) 화면 - 귀여운 애니메이션과 인사말
# ---------------------------------------------------------
if st.session_state.page == 0:
    st.markdown("""
    <div style="text-align: center; margin-top: 50px; padding: 30px; background-color: #f0f8ff; border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
        <img src="https://api.dicebear.com/7.x/fun-emoji/png?seed=happy&backgroundColor=ffdfba" style="width: 150px; border-radius: 50%; border: 5px solid white; box-shadow: 0 4px 10px rgba(0,0,0,0.1); animation: bounce 1.5s infinite;">
        <h2 style="color: #4a90e2; font-weight: 800; margin-top: 20px; font-size: 28px; line-height: 1.4;">
            안녕! 👋<br>우리 같이 무역직무 관련 MBTI를 알아보자! ✨
        </h2>
        <p style="color: #666; font-size: 16px; margin-top: 10px;">총 25개의 질문이 준비되어 있어. (문제당 30초 제한!)</p>
        <style>
            @keyframes bounce {
                0%, 100% {transform: translateY(0);}
                50% {transform: translateY(-15px);}
            }
        </style>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    st.write("")
    
    if st.button("🚀 테스트 시작하기", use_container_width=True):
        st.session_state.page = 1
        st.rerun()

# ---------------------------------------------------------
# 1. 메인 화면 & 질문 진행 (페이지 1 ~ 25)
# ---------------------------------------------------------
elif 1 <= st.session_state.page <= len(questions):
    st.title("💼 글로벌 비즈니스 MBTI")
    st.write("⏱️ **제한 시간 30초!** (선택하지 않으면 자동으로 넘어갑니다)")
    
    # 인덱스 조정을 위해 page - 1 처리
    current_q_idx = st.session_state.page - 1
    progress = (current_q_idx) / len(questions)
    st.progress(progress)
    st.caption(f"진행 상황: {st.session_state.page} / {len(questions)}")
    st.divider()
    
    q = questions[current_q_idx]
    st.subheader(q["text"])
    st.write("") 
    
    for choice_text, mbti_type in q["choices"]:
        if st.button(choice_text, use_container_width=True):
            st.session_state.scores[mbti_type] += 1
            st.session_state.page += 1
            st.rerun()

    if st.button("⏳ 30초 경과 (자동 넘김)", key="timeout_btn", use_container_width=True):
        st.session_state.page += 1
        st.rerun()
        
    components.html(
        """
        <script>
        setTimeout(function() {
            var buttons = window.parent.document.querySelectorAll('.stButton > button');
            for (var i = 0; i < buttons.length; i++) {
                if (buttons[i].innerText.includes('30초 경과')) {
                    buttons[i].click();
                    break;
                }
            }
        }, 30000);
        </script>
        """,
        height=0, width=0
    )

# ---------------------------------------------------------
# 2. 결과 계산 및 출력 화면
# ---------------------------------------------------------
else:
    with st.spinner('당신의 비즈니스 성향을 분석 중입니다...'):
        time.sleep(1.5) 
        
    score_E = st.session_state.scores["E"]
    score_I = st.session_state.scores["I"]
    score_S = st.session_state.scores["S"]
    score_N = st.session_state.scores["N"]
    score_T = st.session_state.scores["T"]
    score_F = st.session_state.scores["F"]
    score_J = st.session_state.scores["J"]
    score_P = st.session_state.scores["P"]

    res_mbti = ""
    res_mbti += "E" if score_E > score_I else "I"
    res_mbti += "S" if score_S >= score_N else "N"
    res_mbti += "T" if score_T >= score_F else "F"
    res_mbti += "J" if score_J >= score_P else "P"
    
    def calc_percent(a, b):
        total = a + b
        return int((a / total) * 100) if total > 0 else 50

    pct_E, pct_I = calc_percent(score_E, score_I), 100 - calc_percent(score_E, score_I)
    pct_S, pct_N = calc_percent(score_S, score_N), 100 - calc_percent(score_S, score_N)
    pct_T, pct_F = calc_percent(score_T, score_F), 100 - calc_percent(score_T, score_F)
    pct_J, pct_P = calc_percent(score_J, score_P), 100 - calc_percent(score_J, score_P)

    cartoon_url = f"https://api.dicebear.com/7.x/fun-emoji/png?seed={res_mbti}&backgroundColor=b6e3f4"
    
    results = {
        "ESTJ": {"title": "철두철미한 시스템 경영자", "desc": "팩폭을 잘함. 데이터와 규율을 바탕으로 조직을 이끄는 완벽주의자입니다. 무역 실무부터 재무 상태까지 꼼꼼하게 통제하며 성장을 이끌어냅니다.", "good": "ISTP (실용주의 달인)", "bad": "INFP (가치 중심 기획자)"},
        "ENTJ": {"title": "야심 찬 글로벌 전략가", "desc": "비전과 목표가 뚜렷하며 통솔력이 뛰어납니다. 새로운 해외 시장 개척과 굵직한 M&A 등 과감한 결정을 내리는 타고난 리더입니다.", "good": "INTP (논리적 분석가)", "bad": "ISFJ (신뢰의 아이콘)"},
        "ESFJ": {"title": "글로벌 네트워킹 마스터", "desc": "뛰어난 친화력으로 바이어와의 관계를 돈독하게 유지합니다. 고객 관리와 팀워크 융화에 탁월한 무역의 윤활유 같은 존재입니다.", "good": "ISFP (유연한 마법사)", "bad": "INTP (논리적 분석가)"},
        "ENFJ": {"title": "카리스마 리더", "desc": "팀원들에게 동기를 부여하고 긍정적인 문화를 주도합니다. 사람을 통해 성과를 창출하고 글로벌 파트너들의 마음을 사로잡습니다.", "good": "INFP (가치 중심 기획자)", "bad": "ISTP (실용주의 달인)"},
        "ESTP": {"title": "위기 탈출 무역 해결사", "desc": "빠른 판단력과 행동력으로 협상 테이블을 주도합니다. 선적 지연이나 클레임 같은 돌발 상황에서도 순발력 있게 문제를 해결합니다.", "good": "ISFJ (신뢰의 아이콘)", "bad": "INFJ (통찰력 있는 조율자)"},
        "ENTP": {"title": "틀을 깨는 비즈니스 혁신가", "desc": "기존 방식을 뛰어넘어 새로운 비즈니스 모델을 제안합니다. 논리적인 언변과 협상력으로 어려운 바이어를 설득하는 데 능합니다.", "good": "INFJ (통찰력 있는 조율자)", "bad": "ISFJ (신뢰의 아이콘)"},
        "ESFP": {"title": "에너제틱 세일즈맨", "desc": "특유의 활기와 긍정 에너지로 어디서든 빠르게 적응합니다. 뛰어난 쇼맨십으로 해외 전시회나 세일즈 피칭에서 가장 빛을 발합니다.", "good": "ISTJ (안정형 관리자)", "bad": "INTJ (마스터마인드)"},
        "ENFP": {"title": "혁신 창업가", "desc": "열정적이고 창의적이며 네트워킹에 능합니다. 기존에 없던 새로운 아이템을 발굴하고, 글로벌 파트너들을 비전에 동참시킵니다.", "good": "INTJ (마스터마인드)", "bad": "ISTJ (안정형 관리자)"},
        "ISTJ": {"title": "리스크 제로! 안정형 관리자", "desc": "정확성과 책임감이 뛰어납니다. 복잡한 무역 서류, 관세 법규 등을 오차 없이 관리하여 회사의 든든한 방패 역할을 합니다.", "good": "ESFP (에너제틱 세일즈맨)", "bad": "ENFP (혁신 창업가)"},
        "INTJ": {"title": "마스터마인드", "desc": "거시적인 안목으로 장기적인 전략을 세웁니다. 치밀한 데이터 분석을 통해 시장을 예측하고 최적의 비즈니스 루트를 설계합니다.", "good": "ENFP (혁신 창업가)", "bad": "ESFJ (네트워킹 마스터)"},
        "ISFJ": {"title": "신뢰의 아이콘", "desc": "안정적인 지원과 세심함으로 바이어가 가장 믿고 맡기는 타입입니다. 디테일한 고객 관리와 실무 처리에 엄청난 강점이 있습니다.", "good": "ESTP (무역 해결사)", "bad": "ENTP (비즈니스 혁신가)"},
        "INFJ": {"title": "통찰력 있는 조율자", "desc": "뛰어난 직관력으로 시장의 숨겨진 니즈를 파악합니다. 파트너사와의 깊이 있고 장기적인 신뢰 관계 구축에 뛰어난 역량을 발휘합니다.", "good": "ENTP (비즈니스 혁신가)", "bad": "ESTP (무역 해결사)"},
        "ISTP": {"title": "실용주의 팩트 체크 달인", "desc": "냉철한 분석력으로 군더더기 없는 프로세스를 만듭니다. 가장 효율적인 물류망을 설계하고 불필요한 비용을 절감하는 데 탁월합니다.", "good": "ESTJ (시스템 경영자)", "bad": "ENFJ (카리스마 리더)"},
        "INTP": {"title": "논리적인 무역 분석가", "desc": "데이터를 깊이 파고들어 글로벌 시장의 구조적 문제를 파악합니다. 남들이 보지 못하는 비즈니스의 맹점을 짚어내는 뛰어난 전략가입니다.", "good": "ENTJ (글로벌 전략가)", "bad": "ESFJ (네트워킹 마스터)"},
        "ISFP": {"title": "유연한 조율의 마법사", "desc": "조용하지만 상황에 맞게 유연한 융통성을 발휘합니다. 부드러운 소통 능력으로 거래처와의 갈등이나 부서 간의 이견을 매끄럽게 조율합니다.", "good": "ESFJ (네트워킹 마스터)", "bad": "ENTJ (글로벌 전략가)"},
        "INFP": {"title": "가치 중심의 기획자", "desc": "단순한 이윤을 넘어 지속 가능성과 윤리적인 비즈니스를 추구합니다. 브랜드의 진정성 있는 스토리를 시장에 알리는 데 탁월합니다.", "good": "ENFJ (카리스마 리더)", "bad": "ESTJ (시스템 경영자)"}
    }

    recommend_jobs = {
        "ESTJ": ["수출입 실무", "통관 관리", "무역 경영지원"],
        "ENTJ": ["해외사업 기획", "경영전략", "SCM 관리"],
        "ESFJ": ["해외영업", "무역 사무", "바이어 CS"],
        "ENFJ": ["글로벌 HR", "해외영업기획", "조직문화 기획"],
        "ESTP": ["현장 물류 관리", "포워딩 영업", "무역 소싱"],
        "ENTP": ["신사업 개발", "B2B 영업", "해외 영업기획"],
        "ESFP": ["글로벌 마케팅", "해외영업", "무역 벤더"],
        "ENFP": ["글로벌 브랜드 마케팅", "해외 마케팅 기획", "신사업 발굴"],
        "ISTJ": ["수출입 통관", "관세 사무", "무역 컴플라이언스"],
        "INTJ": ["물류 네트워크 기획", "데이터 분석", "경영기획"],
        "ISFJ": ["무역 사무지원", "오퍼레이션", "고객 지원(CS)"],
        "INFJ": ["파트너십 기획", "지속가능경영(ESG)", "전략 기획"],
        "ISTP": ["공급망 관리(SCM)", "포워딩 운영", "재고 관리"],
        "INTP": ["시장 조사/분석", "해외투자 기획", "물류 데이터 분석"],
        "ISFP": ["무역 백오피스", "디자인/브랜드 관리", "영업 지원"],
        "INFP": ["글로벌 CSR", "콘텐츠 마케팅", "해외 파트너십 관리"]
    }

    job_descriptions = {
        "수출입 실무": "수출입 계약부터 선적, 결제까지 무역 거래의 전반적인 프로세스를 담당합니다.",
        "통관 관리": "수출입 물품의 세관 신고, 관세 납부 등 통관 절차가 법규에 맞게 처리되도록 관리합니다.",
        "무역 경영지원": "무역 회사의 인사, 총무, 회계 등 조직 운영에 필요한 전반적인 지원 업무를 수행합니다.",
        "해외사업 기획": "해외 시장 진출 전략을 수립하고 신규 사업 타당성을 검토하여 방향을 기획합니다.",
        "경영전략": "기업의 장기적인 비전과 목표를 달성하기 위한 전사적 핵심 전략을 세우고 실행합니다.",
        "SCM 관리": "원자재 조달부터 제품이 고객에게 전달되기까지의 전체 공급망을 효율적으로 관리합니다.",
        "해외영업": "해외 바이어를 발굴해 제품을 수출하고, 기존 거래처와의 관계 및 매출을 관리합니다.",
        "무역 사무": "수출입에 필요한 선적 서류(B/L, 인보이스 등) 작성 및 데이터 입력 등 행정 업무를 지원합니다.",
        "바이어 CS": "해외 고객의 문의, 클레임, A/S 요청 등을 응대하고 서비스 만족도를 높입니다.",
        "글로벌 HR": "해외 지사 인력 관리, 글로벌 인재 채용 및 평가 등 국제적인 인사 제도를 기획합니다.",
        "해외영업기획": "해외 영업 부서의 목표 달성을 위해 실적을 분석하고 영업 전략과 프로모션을 짭니다.",
        "조직문화 기획": "기업의 핵심 가치를 내재화하고 구성원들의 업무 효율과 만족도를 높이는 문화를 만듭니다.",
        "현장 물류 관리": "창고 내 화물의 입출고, 보관, 포장 등 물류 현장의 실질적인 흐름과 작업자들을 관리합니다.",
        "포워딩 영업": "화주(고객)를 대상으로 최적의 국제 운송 루트와 운임을 제안하고 서비스를 판매합니다.",
        "무역 소싱": "해외에서 경쟁력 있는 원자재나 상품을 발굴하고, 좋은 조건으로 수입해 오는 역할을 합니다.",
        "신사업 개발": "회사의 미래 성장 동력이 될 새로운 비즈니스 모델이나 아이템을 기획하고 시장에 론칭합니다.",
        "B2B 영업": "기업 고객을 대상으로 자사의 제품이나 서비스를 제안하고 장기적인 공급 계약을 체결합니다.",
        "글로벌 마케팅": "해외 시장의 특성에 맞춘 마케팅 전략을 수립하여 글로벌 브랜드 인지도를 높입니다.",
        "무역 벤더": "제조사와 바이어 사이에서 제품 기획, 생산 관리, 납기 등을 조율하며 거래를 성사시킵니다.",
        "글로벌 브랜드 마케팅": "전 세계 소비자를 대상으로 일관된 브랜드 메시지를 전달하고 가치를 향상시킵니다.",
        "해외 마케팅 기획": "타겟 국가의 트렌드와 경쟁사를 분석하여 효과적인 현지화 마케팅 캠페인을 기획합니다.",
        "신사업 발굴": "새로운 시장 트렌드를 분석하여 기업이 새롭게 진출할 만한 유망 사업 아이템을 찾습니다.",
        "수출입 통관": "수출입 물품이 세관을 무사히 통과할 수 있도록 관련 법령을 검토하고 서류를 처리합니다.",
        "관세 사무": "관세사무소 등에서 수출입 업체의 통관 대행, 관세 환급, 품목 분류 등의 업무를 수행합니다.",
        "무역 컴플라이언스": "무역 거래 시 발생할 수 있는 법적 리스크를 예방하고 국제 무역 규범을 준수하도록 관리합니다.",
        "물류 네트워크 기획": "가장 빠르고 비용이 절감되는 최적의 글로벌 운송 경로와 거점(허브)을 설계합니다.",
        "데이터 분석": "비즈니스 데이터를 수집 및 가공하여 경영진이 객관적인 의사결정을 내릴 수 있도록 돕습니다.",
        "경영기획": "회사의 연간 사업 계획을 수립하고 예산을 편성하며, 각 부서의 실적을 관리합니다.",
        "무역 사무지원": "영업 담당자가 실무에 집중할 수 있도록 서류 작성, 일정 등 각종 백오피스 업무를 돕습니다.",
        "오퍼레이션": "수주부터 납품까지의 실무 프로세스가 차질 없이 원활하게 돌아가도록 운영하고 통제합니다.",
        "고객 지원(CS)": "고객의 문의 사항이나 불만을 신속하게 해결하여 기업의 서비스 품질을 튼튼히 유지합니다.",
        "파트너십 기획": "타 기업이나 기관과의 전략적 제휴를 기획하여 상호 이익을 창출하는 모델을 만듭니다.",
        "지속가능경영(ESG)": "환경(E), 사회(S), 지배구조(G) 측면에서 기업의 장기적이고 윤리적인 성장 전략을 세웁니다.",
        "전략 기획": "경쟁사 분석 및 시장 조사를 통해 회사가 나아가야 할 중장기적인 비즈니스 전략을 짭니다.",
        "공급망 관리(SCM)": "제품 생산부터 소비자에 이르는 물류 및 정보의 흐름을 최적화하여 효율을 극대화합니다.",
        "포워딩 운영": "고객의 화물이 출발지에서 도착지까지 안전하게 운송되도록 선사/항공사와 스케줄을 조율합니다.",
        "재고 관리": "적정 재고량을 유지하여 품절이나 과잉 재고가 발생하지 않도록 입출고 데이터를 관리합니다.",
        "시장 조사/분석": "해외 타겟 시장의 소비자 동향, 경쟁사, 규제 등을 조사하여 인사이트를 도출합니다.",
        "해외투자 기획": "해외 기업 인수합병(M&A)이나 지사 설립 등 글로벌 자본 투자 전략의 타당성을 검토합니다.",
        "물류 데이터 분석": "운송 비용, 배송 시간 등의 물류 데이터를 분석하여 병목 현상을 찾고 효율을 개선합니다.",
        "무역 백오피스": "영업 일선에서 벗어나 정산, 계약 관리, 실적 통계 등 보이지 않는 곳에서 무역 실무를 지원합니다.",
        "디자인/브랜드 관리": "글로벌 시장에 어울리는 패키지나 시각적 결과물을 기획하고 브랜드 정체성을 유지합니다.",
        "영업 지원": "영업팀의 원활한 활동을 위해 제안서 작성, 샘플 발송, 거래처 데이터 관리 등을 돕습니다.",
        "글로벌 CSR": "해외 지역 사회에 공헌할 수 있는 기업의 사회적 책임 활동을 기획하고 실행합니다.",
        "콘텐츠 마케팅": "해외 소비자들의 공감을 이끌어낼 수 있는 매력적인 콘텐츠를 제작하여 브랜드를 홍보합니다.",
        "해외 파트너십 관리": "해외 대리점, 딜러, 조인트벤처 등 주요 글로벌 파트너들과의 관계를 돈독하게 관리합니다."
    }
    
    final_result = results.get(res_mbti)
    my_jobs = recommend_jobs.get(res_mbti, ["무역", "경영"])
    
    st.title("🎉 당신의 비즈니스 포지션은?")
    
    card_html = f"""
    <div style="background-color: #f8f9fa; border-radius: 20px; padding: 25px; display: flex; align-items: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 20px; flex-wrap: wrap;">
        <div style="flex-shrink: 0; margin-right: 25px; text-align: center;">
            <img src="{cartoon_url}" style="width: 140px; height: 140px; border-radius: 50%; border: 5px solid white; box-shadow: 0 2px 6px rgba(0,0,0,0.15); background-color: #fff;">
        </div>
        <div style="flex: 1; min-width: 200px;">
            <h2 style="color: #9b59b6; font-weight: 800; margin-top: 0; margin-bottom: 12px; font-size: 24px; text-shadow: 1px 1px 2px rgba(0,0,0,0.05);">
                #{final_result['title']} - {res_mbti}
            </h2>
            <p style="font-size: 16px; color: #333; line-height: 1.6; margin: 0; font-weight: 500;">
                {final_result['desc']}
            </p>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style="background-color: #e8f8f5; padding: 15px; border-radius: 12px; text-align: center; border: 1px solid #d1f2eb; height: 100%;">
            <h4 style="margin-top: 0; color: #117a65;">🤝 찰떡궁합 동료</h4>
            <span style="font-weight: bold; font-size: 18px; color: #148f77;">{final_result['good']}</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background-color: #fdedec; padding: 15px; border-radius: 12px; text-align: center; border: 1px solid #fadbd8; height: 100%;">
            <h4 style="margin-top: 0; color: #a93226;">🙅 상극 파트너</h4>
            <span style="font-weight: bold; font-size: 18px; color: #cb4335;">{final_result['bad']}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("") 
    
    st.markdown("### 📊 나의 상세 성향 분석")
    graph_html = f"""
    <div style="background-color: #ffffff; border-radius: 15px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-bottom: 30px;">
        <div style="margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-weight: 700; color: #555;">
                <span style="color: {'#e74c3c' if pct_E >= 50 else '#95a5a6'};">E (외향) {pct_E}%</span>
                <span style="color: {'#3498db' if pct_I > 50 else '#95a5a6'};">I (내향) {pct_I}%</span>
            </div>
            <div style="width: 100%; background-color: #d6eaf8; border-radius: 10px; height: 12px; display: flex; overflow: hidden;">
                <div style="width: {pct_E}%; background-color: #e74c3c; height: 100%;"></div>
                <div style="width: {pct_I}%; background-color: #3498db; height: 100%;"></div>
            </div>
        </div>
        <div style="margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-weight: 700; color: #555;">
                <span style="color: {'#f39c12' if pct_S >= 50 else '#95a5a6'};">S (현실) {pct_S}%</span>
                <span style="color: {'#2ecc71' if pct_N > 50 else '#95a5a6'};">N (직관) {pct_N}%</span>
            </div>
            <div style="width: 100%; background-color: #d5f5e3; border-radius: 10px; height: 12px; display: flex; overflow: hidden;">
                <div style="width: {pct_S}%; background-color: #f39c12; height: 100%;"></div>
                <div style="width: {pct_N}%; background-color: #2ecc71; height: 100%;"></div>
            </div>
        </div>
        <div style="margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-weight: 700; color: #555;">
                <span style="color: {'#8e44ad' if pct_T >= 50 else '#95a5a6'};">T (이성) {pct_T}%</span>
                <span style="color: {'#e67e22' if pct_F > 50 else '#95a5a6'};">F (감성) {pct_F}%</span>
            </div>
            <div style="width: 100%; background-color: #fdebd0; border-radius: 10px; height: 12px; display: flex; overflow: hidden;">
                <div style="width: {pct_T}%; background-color: #8e44ad; height: 100%;"></div>
                <div style="width: {pct_F}%; background-color: #e67e22; height: 100%;"></div>
            </div>
        </div>
        <div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-weight: 700; color: #555;">
                <span style="color: {'#16a085' if pct_J >= 50 else '#95a5a6'};">J (계획) {pct_J}%</span>
                <span style="color: {'#c0392b' if pct_P > 50 else '#95a5a6'};">P (유연) {pct_P}%</span>
            </div>
            <div style="width: 100%; background-color: #f2d7d5; border-radius: 10px; height: 12px; display: flex; overflow: hidden;">
                <div style="width: {pct_J}%; background-color: #16a085; height: 100%;"></div>
                <div style="width: {pct_P}%; background-color: #c0392b; height: 100%;"></div>
            </div>
        </div>
    </div>
    """
    st.markdown(graph_html, unsafe_allow_html=True)

    st.markdown("### 💼 나에게 딱 맞는 무역/경영 직무는?")
    
    for job in my_jobs:
        desc = job_descriptions.get(job, "무역/경영 분야의 핵심 직무입니다.")
        saramin_url = f"https://www.saramin.co.kr/zf_user/search?searchword={job}"
        
        st.markdown(f"""
        <div style="background-color: #fcfcfc; border-left: 5px solid #4a90e2; padding: 15px; margin-bottom: 15px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
            <h4 style="margin-top: 0; color: #333;">📌 {job}</h4>
            <p style="color: #666; font-size: 15px; line-height: 1.5; margin-bottom: 15px;">{desc}</p>
            <a href="{saramin_url}" target="_blank" style="text-decoration: none;">
                <div style="background-color: #eaf3ff; color: #4a90e2; padding: 10px; border-radius: 6px; text-align: center; font-weight: bold; font-size: 14px; border: 1px solid #cce0ff;">
                    '{job}' 채용공고 보러가기 🔍
                </div>
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    if st.button("🔄 테스트 다시하기", use_container_width=True):
        st.session_state.page = 0
        st.session_state.scores = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}
        st.rerun()
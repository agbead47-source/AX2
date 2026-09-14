# 위치: AX2/day08/091402.py
# 설치: python -m pip install -U streamlit requests python-dotenv Babel
# 실행: python -m streamlit run 091402.py
# 검증 시 실제 API 키가 없어 외부 서비스의 실시간 응답은 모의 응답으로 점검했습니다.

import html
import json
import math
import os
import re
import hashlib
import uuid
from urllib.parse import urlencode, urlsplit
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from string import Template

import requests
import streamlit as st
import streamlit.components.v1 as components
from babel.numbers import get_currency_name, get_territory_currencies
from dotenv import load_dotenv


class APIError(Exception):
    pass


def request_json(method, url, service, **kwargs):
    try:
        with requests.request(method, url, timeout=(5, 30), **kwargs) as response:
            if response.status_code in (401, 403):
                raise APIError(f"{service}: API 키와 서비스 이용 권한을 확인해 주세요.")
            if response.status_code == 429:
                raise APIError(f"{service}: 요청 한도를 초과했습니다. 잠시 후 다시 시도해 주세요.")
            response.raise_for_status()
            return response.json()
    except requests.Timeout:
        raise APIError(f"{service}: 응답 시간이 초과되었습니다.") from None
    except requests.RequestException:
        raise APIError(f"{service}: 서버에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요.") from None
    except ValueError:
        raise APIError(f"{service}: 올바른 JSON 응답이 아닙니다.") from None


def coordinates(lat, lon):
    try:
        lat, lon = float(lat), float(lon)
        if math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180:
            return lat, lon
    except (TypeError, ValueError):
        pass
    return None


@st.cache_data(ttl=86400, max_entries=128, show_spinner=False)
def search_locations(query, api_key):
    data = request_json("GET", "https://api.openweathermap.org/geo/1.0/direct", "지역 검색",
                        params={"q": query, "limit": 5, "appid": api_key})
    if not isinstance(data, list):
        raise APIError("지역 검색: 검색 결과 형식이 올바르지 않습니다.")
    results = []
    for item in data:
        if not isinstance(item, dict):
            continue
        point = coordinates(item.get("lat"), item.get("lon"))
        if point is None:
            continue
        names = item.get("local_names") or {}
        name = names.get("ko") or item.get("name") or query
        country = str(item.get("country") or "").upper()
        label = " · ".join(str(v) for v in (name, item.get("state"), country) if v)
        results.append({"lat": point[0], "lon": point[1], "country": country, "label": label})
    return results


@st.cache_data(ttl=600, max_entries=128, show_spinner=False)
def get_weather(lat, lon, api_key):
    data = request_json("GET", "https://api.openweathermap.org/data/2.5/weather", "날씨",
                        params={"lat": lat, "lon": lon, "appid": api_key, "units": "metric", "lang": "kr"})
    try:
        if str(data.get("cod", 200)) != "200":
            raise ValueError
        main = data["main"]
        temp, feels = float(main["temp"]), float(main["feels_like"])
        if not all(math.isfinite(v) for v in (temp, feels)):
            raise ValueError
        local_time = datetime.fromtimestamp(int(data["dt"]), timezone.utc)
        local_time += timedelta(seconds=int(data.get("timezone", 0)))
        return {"temp": temp, "feels": feels, "humidity": main["humidity"],
                "description": data["weather"][0]["description"],
                "time": local_time.strftime("%m.%d %H:%M")}
    except (KeyError, IndexError, TypeError, ValueError, AttributeError, OverflowError, OSError):
        raise APIError("날씨: 기온 또는 관측 정보를 읽을 수 없습니다.") from None


def country_currencies(country):
    return list(dict.fromkeys(get_territory_currencies(country, start_date=date.today(), tender=True)))


@st.cache_data(ttl=3600, max_entries=128, show_spinner=False)
def get_exchange(currency, api_key):
    if currency == "KRW":
        return 1.0, "KRW → KRW · 동일 통화"
    data = request_json("GET", f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{currency}", "환율")
    if not isinstance(data, dict):
        raise APIError("환율: 응답 형식이 올바르지 않습니다.")
    if data.get("result") != "success":
        messages = {"unsupported-code": "지원하지 않는 통화입니다.",
                    "invalid-key": "API 키를 확인해 주세요.",
                    "inactive-account": "계정 이메일 인증을 완료해 주세요.",
                    "quota-reached": "요청 한도를 초과했습니다."}
        raise APIError("환율: " + messages.get(data.get("error-type"), "환율을 가져오지 못했습니다."))
    try:
        rate = float(data["conversion_rates"]["KRW"])
        if data.get("base_code") != currency or not math.isfinite(rate) or rate <= 0:
            raise ValueError
        updated = datetime.fromtimestamp(int(data["time_last_update_unix"]), timezone.utc)
        return rate, updated.strftime("%Y.%m.%d %H:%M UTC")
    except (KeyError, TypeError, ValueError, OverflowError, OSError):
        raise APIError("환율: KRW 환율 또는 갱신 정보를 읽을 수 없습니다.") from None


def distance_km(lat1, lon1, lat2, lon2):
    a, b = math.radians(lat1), math.radians(lat2)
    dlat, dlon = b - a, math.radians(lon2 - lon1)
    h = math.sin(dlat / 2) ** 2 + math.cos(a) * math.cos(b) * math.sin(dlon / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(min(1.0, max(0.0, h))))


CATEGORIES = {"stationery": "문구점", "craft": "공예용품", "art": "미술품점",
              "restaurant": "음식점", "cafe": "카페"}


@st.cache_data(ttl=1800, max_entries=128, show_spinner=False)
def search_places(lat, lon, radius, mode):
    if mode == "stationery":
        selector = '["shop"~"^(stationery|craft|art)$"]'
    elif mode == "food":
        selector = '["amenity"~"^(restaurant|cafe)$"]'
    else:
        raise APIError("장소 검색 종류가 올바르지 않습니다.")
    query = f"[out:json][timeout:20];nwr(around:{int(radius)},{float(lat)},{float(lon)}){selector};out center tags;"
    endpoints = ("https://overpass.private.coffee/api/interpreter",
                 "https://overpass-api.de/api/interpreter")
    data = None
    for endpoint in endpoints:
        try:
            candidate = request_json("POST", endpoint, "장소 검색", data={"data": query},
                                     headers={"User-Agent": "StationeryTravelNote/1.0"})
            # HTTP 200이어도 remark가 있으면 시간초과 등으로 일부 결과만 반환됐을 수 있습니다.
            if not isinstance(candidate, dict) or candidate.get("remark") or not isinstance(candidate.get("elements"), list):
                raise APIError("장소 검색 응답이 불완전합니다.")
            data = candidate
            break
        except APIError:
            continue
    if data is None:
        raise APIError("장소 검색 서버가 모두 응답하지 않았습니다. 반경을 줄이거나 잠시 후 다시 눌러 주세요.")
    places, seen = [], set()
    for item in data["elements"]:
        if not isinstance(item, dict):
            continue
        tags = item.get("tags") or {}
        center = item.get("center") or {}
        point = coordinates(item.get("lat", center.get("lat")), item.get("lon", center.get("lon")))
        kind, oid = item.get("type"), item.get("id")
        if point is None or kind not in ("node", "way", "relation") or not isinstance(oid, int):
            continue
        identity = (kind, oid)
        if identity in seen:
            continue
        seen.add(identity)
        distance = distance_km(lat, lon, *point)
        # way/relation 중심점도 선택한 검색 반경 안에 있는 경우만 표시합니다.
        if distance > radius / 1000:
            continue
        category = CATEGORIES.get(tags.get("shop") or tags.get("amenity"), "장소")
        address = tags.get("addr:full") or " ".join(str(tags[k]) for k in
                  ("addr:city", "addr:street", "addr:housenumber") if tags.get(k))
        places.append({"lat": point[0], "lon": point[1], "distance": distance,
                       "name": str(tags.get("name:ko") or tags.get("name") or tags.get("name:en") or f"이름 없는 {category}"),
                       "category": category, "address": address or "주소 미등록",
                       "hours": str(tags.get("opening_hours") or "영업시간 미등록"),
                       "url": f"https://www.openstreetmap.org/{kind}/{oid}"})
    places.sort(key=lambda p: p["distance"])
    return places[:50], len(places)


def render_html(source):
    # HTML 블록 내부의 빈 줄/들여쓰기가 Markdown 코드 블록으로 해석되지 않게 합니다.
    st.markdown("\n".join(line.strip() for line in source.splitlines() if line.strip()), unsafe_allow_html=True)


def card(label, title, detail):
    render_html('<div class="paper-card"><div class="paper-label">' + html.escape(label)
                + '</div><div class="paper-main">' + html.escape(title)
                + '</div><div class="paper-small">' + html.escape(detail) + '</div></div>')


def safe_link(value):
    value = str(value or "").strip()
    try:
        parts = urlsplit(value)
        return value if parts.scheme in ("https", "http") and parts.hostname and not parts.username else ""
    except ValueError:
        return ""


def init_planner():
    defaults = {"travel_title": "나의 문구 여행", "travel_memo": "", "travel_day": 1,
                "travel_mode": "walking", "bookmarks": [], "itinerary": [], "planner_notice": ""}
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def add_bookmark(place):
    ss = st.session_state
    name = str(place.get("name") or "").strip()
    if not name:
        ss.planner_notice = "장소 이름을 입력해 주세요."
        return
    url = safe_link(place.get("url"))
    city = str(place.get("city") or "")
    bid = hashlib.sha256((url or name + "|" + city).encode()).hexdigest()[:20]
    if any(p["id"] == bid for p in ss.bookmarks):
        ss.planner_notice = "이미 북마크에 있는 장소예요."
        return
    point = coordinates(place.get("lat"), place.get("lon"))
    ss.bookmarks.append({"id": bid, "name": name[:200], "city": city[:200], "url": url,
                         "lat": point[0] if point else None, "lon": point[1] if point else None})
    ss.planner_notice = "북마크에 저장했어요. 사이드바에서 여행 경로에 넣어보세요."


def add_stop(bid):
    ss = st.session_state
    if any(s["bookmark_id"] == bid and s["day"] == ss.travel_day for s in ss.itinerary):
        ss.planner_notice = "이 날짜의 경로에 이미 들어 있어요."
        return
    ss.itinerary.append({"id": uuid.uuid4().hex, "bookmark_id": bid, "day": ss.travel_day})


def change_stop(sid, action):
    ss = st.session_state
    position = next((i for i, s in enumerate(ss.itinerary) if s["id"] == sid), None)
    if position is None:
        return
    if action == "remove":
        ss.itinerary.pop(position)
        return
    day = ss.itinerary[position]["day"]
    positions = [i for i, s in enumerate(ss.itinerary) if s["day"] == day]
    current = positions.index(position)
    target = current + (-1 if action == "up" else 1)
    if 0 <= target < len(positions):
        other = positions[target]
        ss.itinerary[position], ss.itinerary[other] = ss.itinerary[other], ss.itinerary[position]


def remove_bookmark(bid):
    ss = st.session_state
    ss.bookmarks = [p for p in ss.bookmarks if p["id"] != bid]
    ss.itinerary = [s for s in ss.itinerary if s["bookmark_id"] != bid]


def planner_data():
    ss = st.session_state
    return {"version": 1, "title": ss.travel_title, "memo": ss.travel_memo,
            "bookmarks": ss.bookmarks, "itinerary": ss.itinerary}


def validate_plan(raw):
    if len(raw) > 1_000_000:
        raise ValueError("여행 노트 파일은 1MB 이하여야 합니다.")
    data = json.loads(raw)
    if not isinstance(data, dict) or data.get("version") != 1:
        raise ValueError("이 앱에서 내려받은 여행 노트 파일을 선택해 주세요.")
    if not isinstance(data.get("title"), str) or not isinstance(data.get("memo"), str):
        raise ValueError("제목 또는 메모 형식이 올바르지 않습니다.")
    if len(data["title"]) > 200 or len(data["memo"]) > 20000:
        raise ValueError("제목 또는 메모가 너무 깁니다.")
    books, stops = data.get("bookmarks"), data.get("itinerary")
    if not isinstance(books, list) or not isinstance(stops, list) or len(books) > 500 or len(stops) > 1000:
        raise ValueError("북마크 또는 경로 형식이 올바르지 않습니다.")
    ids, clean_books, clean_stops = set(), [], []
    for p in books:
        if not isinstance(p, dict) or not all(isinstance(p.get(k), str) for k in ("id", "name", "city", "url")):
            raise ValueError("북마크 형식이 올바르지 않습니다.")
        if not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", p["id"]) or p["id"] in ids or not p["name"].strip():
            raise ValueError("중복되거나 올바르지 않은 북마크입니다.")
        point = coordinates(p.get("lat"), p.get("lon"))
        ids.add(p["id"])
        clean_books.append({"id": p["id"], "name": p["name"][:200], "city": p["city"][:200],
                            "url": safe_link(p["url"]), "lat": point[0] if point else None,
                            "lon": point[1] if point else None})
    seen, scheduled = set(), set()
    for s in stops:
        if not isinstance(s, dict) or not isinstance(s.get("id"), str) or not isinstance(s.get("bookmark_id"), str):
            raise ValueError("경로 형식이 올바르지 않습니다.")
        if (not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", s["id"]) or s["id"] in seen
                or s["bookmark_id"] not in ids or type(s.get("day")) is not int or not 1 <= s["day"] <= 30
                or (s["day"], s["bookmark_id"]) in scheduled):
            raise ValueError("경로의 날짜나 장소 연결이 올바르지 않습니다.")
        seen.add(s["id"])
        scheduled.add((s["day"], s["bookmark_id"]))
        clean_stops.append({k: s[k] for k in ("id", "bookmark_id", "day")})
    return dict(data, bookmarks=clean_books, itinerary=clean_stops)


def import_plan():
    ss = st.session_state
    uploaded = ss.get("plan_upload")
    if uploaded is None:
        ss.planner_notice = "불러올 파일을 먼저 선택해 주세요."
        return
    try:
        data = validate_plan(uploaded.getvalue())
    except (ValueError, UnicodeError, RecursionError):
        ss.planner_notice = "파일을 읽지 못했어요. 이 앱에서 내려받은 여행 노트 JSON 파일인지 확인해 주세요."
        return
    ss.travel_title, ss.travel_memo = data["title"], data["memo"]
    ss.bookmarks, ss.itinerary = data["bookmarks"], data["itinerary"]
    ss.travel_day = 1
    ss.planner_notice = "여행 노트를 불러왔어요."


def directions_url(origin, destination, mode):
    def address(p):
        point = coordinates(p.get("lat"), p.get("lon"))
        return f"{point[0]},{point[1]}" if point else f"{p['name']} {p['city']}"
    return "https://www.google.com/maps/dir/?" + urlencode(
        {"api": 1, "origin": address(origin), "destination": address(destination), "travelmode": mode})


def render_planner():
    ss = st.session_state
    with st.sidebar:
        st.subheader("📓 나의 여행 수첩")
        st.text_input("여행 제목", key="travel_title", max_chars=200)
        st.text_area("여행 메모", key="travel_memo", height=170, max_chars=20000,
                     placeholder="사고 싶은 문구, 예산, 꼭 들를 곳을 적어두세요.")
        st.caption("메모는 입력 후 바깥을 누르면 반영돼요. 새로고침·종료 전에 아래에서 파일로 저장해 주세요.")
        if ss.planner_notice:
            st.info(ss.planner_notice)
            ss.planner_notice = ""
        st.number_input("여행 날짜 (DAY)", min_value=1, max_value=30, step=1, key="travel_day")
        st.markdown("**🔖 장소 북마크**")
        if not ss.bookmarks:
            st.caption("검색 결과나 대표 문구점 카드의 ‘북마크’ 버튼을 눌러보세요.")
        for p in list(ss.bookmarks):
            with st.expander(p["name"]):
                st.text(p["city"])
                if p["url"]:
                    st.link_button("매장 정보 열기", p["url"])
                x, y = st.columns(2)
                x.button("경로에 추가", key="plan_add_" + p["id"], on_click=add_stop, args=(p["id"],))
                y.button("북마크 삭제", key="plan_del_" + p["id"], on_click=remove_bookmark, args=(p["id"],),
                         help="여행 경로에 넣은 같은 장소도 함께 삭제됩니다.")
        with st.expander("＋ 장소 직접 추가"):
            with st.form("manual_bookmark", clear_on_submit=True):
                name = st.text_input("장소 이름", max_chars=200)
                city = st.text_input("도시·국가 또는 주소", max_chars=200)
                url = st.text_input("매장 링크 (선택)")
                if st.form_submit_button("북마크 저장"):
                    add_bookmark({"name": name, "city": city, "url": url})
                    st.rerun()
        st.markdown(f"**🧭 DAY {ss.travel_day} · 방문 순서**")
        books = {p["id"]: p for p in ss.bookmarks}
        today = [s for s in ss.itinerary if s["day"] == ss.travel_day]
        for i, stop in enumerate(today):
            p = books[stop["bookmark_id"]]
            st.text(f"{i + 1}. {p['name']}")
            a, b, c = st.columns(3)
            a.button("↑ 위로", key="up_" + stop["id"], disabled=i == 0,
                     on_click=change_stop, args=(stop["id"], "up"))
            b.button("↓ 아래로", key="down_" + stop["id"], disabled=i == len(today) - 1,
                     on_click=change_stop, args=(stop["id"], "down"))
            c.button("제외", key="remove_" + stop["id"], on_click=change_stop, args=(stop["id"], "remove"))
        if not today:
            st.caption("북마크를 열고 ‘경로에 추가’를 누르면 이 날짜에 들어갑니다.")
        if len(today) >= 2:
            modes = {"walking": "도보", "transit": "대중교통", "driving": "자동차"}
            st.selectbox("이동 방법", list(modes), format_func=modes.get, key="travel_mode")
            with st.expander("구간별 길찾기"):
                for i in range(len(today) - 1):
                    start, end = books[today[i]["bookmark_id"]], books[today[i + 1]["bookmark_id"]]
                    st.link_button(f"{i + 1} → {i + 2} · {end['name']}", directions_url(start, end, ss.travel_mode))
                st.caption("Google 지도에서 실제 경로를 확인합니다. 이름으로 찾는 장소는 도착지를 확인해 주세요.")
        st.divider()
        st.download_button("💾 여행 노트 내려받기", json.dumps(planner_data(), ensure_ascii=False, indent=2),
                           file_name="stationery-travel-note.json", mime="application/json")
        with st.expander("저장한 여행 노트 불러오기"):
            st.file_uploader("여행 노트 JSON", type=["json"], key="plan_upload")
            st.caption("불러오면 현재 제목·메모·북마크·경로가 파일 내용으로 바뀝니다.")
            st.button("파일 내용으로 불러오기", on_click=import_plan)


# 공식 매장 안내 확인: 2026-09-14. 각 국가의 추천은 정확히 세 곳입니다.
# 항목: 매장명, 도시/지역, 쇼핑 포인트, 공식 안내 URL.
SHOP_COUNTRIES = {"KR": "한국", "JP": "일본", "TW": "대만",
                  "US": "미국", "GB": "영국", "FR": "프랑스"}
SHOP_PICKS = {
    "KR": [
        ("포인트오브뷰 성수", "서울 · 성수", "노트와 필기 도구, 책상 위에 둘 작은 오브제를 둘러보세요.",
         "https://pointofview.kr/pointofview/about.html"),
        ("오브젝트 서교점", "서울 · 서교", "작가 문구와 스티커, 기록장에 더할 작은 소품을 찾아보세요.",
         "https://insideobject.com/"),
        ("교보문고·핫트랙스 광화문", "서울 · 광화문", "필기구와 노트 등 일상 문구를 폭넓게 비교하기 좋은 코스입니다.",
         "https://store.kyobobook.co.kr/store-info"),
    ],
    "JP": [
        ("TRAVELER’S FACTORY 나카메구로", "도쿄 · 나카메구로", "트래블러스노트와 리필, 노트를 꾸밀 부속품을 살펴보세요.",
         "https://www.travelers-company.com/about"),
        ("긴자 이토야 본점", "도쿄 · 긴자", "다양한 종이와 필기 도구를 비교하며 여행 기록용 문구를 골라보세요.",
         "https://www.ito-ya.co.jp/ext/store/ginza/ginza/index.html"),
        ("카키모리", "도쿄 · 구라마에", "맞춤 노트와 잉크를 둘러보세요. 잉크 제작 체험은 예약 안내를 확인하세요.",
         "https://kakimori.com/en/pages/stores"),
    ],
    "TW": [
        ("타이리 문구 · Tylee", "타이베이 · 다안", "만년필과 잉크를 중심으로 필기 취향에 맞는 도구를 찾아보세요.",
         "https://www.tylee.tw/index.php?information_id=26&route=information%2Finformation"),
        ("Plain 문구 · 중샤오신성", "타이베이 · 중정", "스탬프와 자체 제작 노트를 둘러보세요. 2026년 9월 7~15일 휴무 공지가 있습니다.",
         "https://www.plain.tw/"),
        ("청핀 생활 송옌 · 문구관", "타이베이 · 송산문화창의공원", "2층 문구관에서 노트, 필기구와 선물용 디자인 문구를 살펴보세요.",
         "https://meet.eslite.com/tw/tc/store/20180220034"),
    ],
    "US": [
        ("Yoseka Stationery", "뉴욕 · 브루클린", "노트와 펜, 스티커를 직접 살펴보며 나에게 맞는 문구를 찾아보세요.",
         "https://yosekastationery.com/pages/visit-yoseka"),
        ("Goods for the Study · Nolita", "뉴욕 · 놀리타", "저널과 메모패드, 필기구를 고르며 책상 위 문구를 채워보세요.",
         "https://goodsforthestudy.com/"),
        ("Boston General Store · Brookline", "매사추세츠 · 브루클라인", "생활 도구와 함께 문구 매장을 둘러보는 코스로 추천합니다.",
         "https://www.bostongeneralstore.com/pages/hours-locations"),
    ],
    "GB": [
        ("Choosing Keeping", "런던 · 코벤트가든", "노트와 필기구, 종이 문구를 천천히 고르는 쇼핑 코스입니다.",
         "https://choosingkeeping.com/pages/frontpage"),
        ("Present & Correct", "런던 · 블룸즈버리", "문구와 사무용품을 둘러보며 취향에 맞는 기록 도구를 골라보세요.",
         "https://www.presentandcorrect.com/pages/contact"),
        ("London Graphic Centre", "런던 · 코벤트가든", "드로잉 도구와 스케치북, 다양한 필기구를 비교해 보세요.",
         "https://www.londongraphics.co.uk/our-store"),
    ],
    "FR": [
        ("Mélodies Graphiques", "파리", "종이 문구와 글쓰기 도구를 찾아보는 여행 코스입니다.",
         "https://melodies-graphiques.com/"),
        ("L’Écritoire", "파리 · 파사주 몰리에르", "필기와 캘리그래피 도구를 살펴보며 손글씨용 문구를 골라보세요.",
         "https://www.lecritoireparis.com/fr/l-ecritoire-papeterie-originale-et-creative-depuis-1975.html"),
        ("Papier Tigre · Marais", "파리 · 마레", "색감 있는 노트와 플래너, 펜을 여행 기념 문구로 살펴보세요.",
         "https://www.papiertigre.fr/fr/"),
    ],
}


def render_shop_picks(country=""):
    st.subheader("나라별 문구 쇼핑 · PICK 3")
    ss = st.session_state
    # 여행지 국가가 바뀔 때만 자동 선택. 사용자가 고른 나라는 일반 재실행에서 유지합니다.
    if ss.get("picks_location_country") != country:
        ss.picks_location_country = country
        ss.picks_country = country if country in SHOP_PICKS else "JP"
    if "picks_country" not in ss:
        ss.picks_country = "JP"
    chosen = st.selectbox("추천을 보고 싶은 나라", list(SHOP_COUNTRIES),
                          format_func=SHOP_COUNTRIES.get, key="picks_country")
    st.caption("한국·일본·대만·미국·영국·프랑스의 문구 쇼핑 코스입니다. 국가 단위 추천이며, 카드의 도시를 확인해 주세요.")
    if country and country not in SHOP_PICKS:
        st.caption("검색한 국가의 추천은 아직 준비 중입니다. 위에서 다른 나라의 추천을 둘러볼 수 있어요.")
    for i, (column, spot) in enumerate(zip(st.columns(3), SHOP_PICKS[chosen]), 1):
        name, city, tip, url = spot
        with column:
            render_html(f'''<div class="paper-card shop-pick">
            <div class="paper-label">PICK {i:02d} / {html.escape(SHOP_COUNTRIES[chosen])}</div>
            <strong>{html.escape(name)}</strong>
            <div class="paper-small">📍 {html.escape(city)}<br>{html.escape(tip)}</div>
            <div class="paper-small"><a href="{html.escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">공식 매장 안내 ↗</a></div>
            </div>''')
            spot = {"name": name, "city": city + " · " + SHOP_COUNTRIES[chosen], "url": url}
            bid = hashlib.sha256(url.encode()).hexdigest()[:20]
            saved = any(p["id"] == bid for p in ss.bookmarks)
            st.button("✓ 북마크됨" if saved else "🔖 북마크", key="pick_save_" + bid,
                      disabled=saved, on_click=add_bookmark, args=(spot,), use_container_width=True)
    st.caption("공식 안내 확인: 2026.09.14 · 방문일의 영업시간과 재고는 각 매장 링크에서 확인해 주세요.")


MAP_TEMPLATE = Template(r'''<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&family=Noto+Sans+KR:wght@400;500;600&display=swap">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>
body{margin:0;background:#f6efdf;color:#402d21;font:14px 'Noto Sans KR','Malgun Gothic',sans-serif}
#map{height:500px;border:1px solid #bca68a;border-radius:4px}
#status{padding:8px;font-size:12px;min-height:18px}
.pin{background:#704a35;color:#fff4de;border:2px solid #fff4de;border-radius:50%;text-align:center;line-height:27px;font:bold 13px/27px sans-serif;box-shadow:0 2px 5px #6548}
.leaflet-popup-content{line-height:1.7;overflow-wrap:anywhere;font-family:'Noto Sans KR','Malgun Gothic',sans-serif}
.leaflet-popup-content strong{font-family:'Gowun Batang',Batang,Georgia,serif}
.leaflet-popup-content-wrapper{background:#fff7e8;color:#402d21}
a{color:#904b36}
</style></head><body>
<div id="map" aria-label="여행지와 주변 장소 지도"></div><div id="status"></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const data = $DATA;
const status = document.getElementById('status');
if (typeof L === 'undefined') {
  status.textContent = '지도 라이브러리를 불러오지 못했습니다. 인터넷 연결을 확인해 주세요.';
} else {
  const map = L.map('map').setView([data.lat, data.lon], 13);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors'
  }).on('tileerror', function () {
    status.textContent = '일부 지도 타일을 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.';
  }).addTo(map);
  const label = document.createElement('strong');
  label.textContent = data.label;
  L.circleMarker([data.lat, data.lon], {radius:8,color:'#425b50',fillOpacity:1})
    .addTo(map).bindPopup(label);
  const circle = L.circle([data.lat, data.lon], {
    radius:data.radius,color:'#87674c',weight:1,fillOpacity:0.04,dashArray:'5 6'
  }).addTo(map);
  map.fitBounds(circle.getBounds(), {padding:[15,15],maxZoom:15});
  data.places.forEach(function(p, i) {
    const popup = document.createElement('div');
    const title = document.createElement('strong');
    title.textContent = (i + 1) + '. ' + p.name;
    popup.appendChild(title);
    [p.category + ' · ' + p.distance.toFixed(2) + ' km', p.address, p.hours].forEach(function(text) {
      const row = document.createElement('div');
      row.textContent = text;
      popup.appendChild(row);
    });
    const link = document.createElement('a');
    link.href = p.url; link.target = '_blank'; link.rel = 'noopener noreferrer';
    link.textContent = 'OpenStreetMap에서 보기'; popup.appendChild(link);
    L.marker([p.lat,p.lon], {icon:L.divIcon({
      className:'pin',html:String(i+1),iconSize:[30,30],iconAnchor:[15,15]
    })}).addTo(map).bindPopup(popup);
  });
  (data.route || []).forEach(function(p, i) {
    if (!Number.isFinite(p.lat) || !Number.isFinite(p.lon)) return;
    const note = document.createElement('strong');
    note.textContent = 'DAY ' + data.day + ' · ' + (i+1) + '. ' + p.name;
    L.circleMarker([p.lat,p.lon], {radius:12,color:'#aa5b3e',weight:3,fillOpacity:0.15})
      .addTo(map).bindPopup(note);
    const previous = data.route[i-1];
    if (previous && Number.isFinite(previous.lat) && Number.isFinite(previous.lon)) {
      L.polyline([[previous.lat,previous.lon],[p.lat,p.lon]], {
        color:'#aa5b3e',weight:3,dashArray:'5 8'
      }).addTo(map);
    }
  });
  L.control.scale({imperial:false}).addTo(map);
  setTimeout(function(){map.invalidateSize();}, 100);
}
</script></body></html>''')


def map_html(location, radius, places, route=None, day=1):
    data = dict(location, radius=radius, places=places, route=route or [], day=day)
    # 외부 장소명에 </script> 등이 있어도 HTML/JavaScript로 실행되지 않습니다.
    payload = json.dumps(data, ensure_ascii=True, allow_nan=False)
    payload = payload.replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
    return MAP_TEMPLATE.substitute(DATA=payload)


def main():
    st.set_page_config(page_title="문구 여행 노트", page_icon="📓", layout="wide", initial_sidebar_state="expanded")
    init_planner()
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(env_path, override=True)
    weather_key = (os.getenv("OPENWEATHER_API_KEY") or "").strip()
    exchange_key = (os.getenv("EXCHANGE_API_KEY") or "").strip()

    render_html('''<style>
    .stApp{background:repeating-linear-gradient(0deg,#eae1d1 0px,#eae1d1 27px,#e3d9c8 28px);color:#402d21}
    .block-container{max-width:1200px;padding-top:2rem;padding-bottom:3rem}
    h1,h2,h3{font-family:Georgia,serif!important;color:#483122!important}
    .travel-cover{position:relative;background:linear-gradient(115deg,#493024,#694530,#422b21);color:#f5e8cf;padding:34px 150px 34px 36px;border:1px solid #352218;outline:1px dashed #a78862;outline-offset:-10px;border-radius:6px;box-shadow:3px 10px 20px #49302533;margin-bottom:25px}
    .travel-small{font:11px monospace;letter-spacing:2px;color:#dac19e}
    .travel-title{font:bold 38px Georgia,serif;margin:12px 0}
    .travel-subtitle{font-size:14px;color:#e3d0b3;line-height:1.7}
    .travel-stamp{position:absolute;right:30px;top:36px;border:3px double #d58a6d;padding:12px;color:#e3a080;font:bold 16px monospace;transform:rotate(-9deg)}
    .paper-card{background:#fcf5e7;border:1px solid #cdbb9f;border-radius:3px;padding:20px;min-height:155px;box-shadow:3px 4px 0 #c8b59655;margin:8px 0 16px;overflow-wrap:anywhere}
    .paper-label{font:11px monospace;letter-spacing:1px;color:#82694e;border-bottom:1px dashed #c6b18e;padding-bottom:8px;margin-bottom:12px}
    .paper-main{font:bold 25px Georgia,serif;color:#493021}
    .paper-small{font-size:13px;color:#80674f;line-height:1.7;margin-top:10px}
    .place-card{background:#fcf5e7;border:1px solid #d1c0a6;border-left:5px solid #805b40;padding:15px 19px;margin:9px 0;box-shadow:2px 3px 6px #50382112;overflow-wrap:anywhere}
    .place-card a{color:#87422e}
    .stButton>button,[data-testid="stFormSubmitButton"] button{background:#65432f!important;color:#fff1da!important;border:1px solid #49301f!important;border-radius:3px;box-shadow:2px 3px 0 #bfa583}
    [data-testid="stTextInput"] input,[data-testid="stNumberInput"] input{background:#fff7e8;color:#402d21}
    [data-baseweb="select"]>div{background:#fff7e8;color:#402d21}
    [data-testid="stWidgetLabel"] p,[data-testid="stCaptionContainer"] p{color:#654c37!important}
    @media(max-width:600px){.travel-cover{padding:30px 24px}.travel-title{font-size:30px}.travel-stamp{position:static;display:inline-block;margin-top:15px}}
    </style>''')
    render_html('''<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&family=Noto+Sans+KR:wght@400;500;600&display=swap">
    <style>
    .stApp{font-family:'Noto Sans KR','Malgun Gothic',sans-serif;line-height:1.75}
    .stApp p,.stApp label,.stApp input,.stApp textarea,.stApp button,[data-baseweb="select"],
    [data-testid="stMarkdownContainer"],.paper-small{font-family:'Noto Sans KR','Malgun Gothic',sans-serif}
    .stApp h1,.stApp h2,.stApp h3,.travel-title,.paper-main,.place-card strong,.shop-pick strong{
    font-family:'Gowun Batang',Batang,Georgia,serif!important;letter-spacing:-0.025em;line-height:1.5}
    .travel-title{font-size:40px}.travel-subtitle{font-family:'Gowun Batang',Batang,serif;font-size:17px}
    .paper-main{font-size:25px}.shop-pick strong{font-size:19px}
    .travel-small,.paper-label,.travel-stamp{font-family:'Courier New',monospace}
    [data-testid="stSidebar"]{background:#f5eddc;border-right:1px solid #c6b394}
    [data-testid="stSidebar"] h3{font-size:23px;color:#5c402d!important}
    [data-testid="stSidebar"] input,[data-testid="stSidebar"] textarea{
    background:#fff9ed;color:#463324;border-radius:3px}
    [data-testid="stSidebar"] textarea{line-height:1.85;background:repeating-linear-gradient(#fff9ed 0px,#fff9ed 28px,#e8ddc8 29px)}
    [data-testid="stSidebar"] [data-testid="stExpander"]{background:#fbf5e9;border-color:#d1bea0}
    .stApp a{color:#875236}.stApp button{font-size:14px}
    [data-testid="stSidebar"] button{box-shadow:none!important}
    @media(max-width:600px){.travel-title{font-size:30px}}
    </style>''')
    render_planner()
    render_html(f'''<div class="travel-cover">
    <div class="travel-small">STATIONERY TRAVEL LOG / {date.today():%Y.%m.%d}</div>
    <div class="travel-title">문구 여행 노트</div>
    <div class="travel-subtitle">좋은 문구점과 맛있는 한 끼를 수집하는 작은 여행 수첩</div>
    <div class="travel-stamp">TRAVEL<br>NOTE</div>
    </div>''')

    defaults = {"geo_results": [], "geo_index": 0, "places": [], "place_total": 0,
                "place_mode": None, "place_error": "", "search_context": None}
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    ss = st.session_state
    if not weather_key:
        render_shop_picks()
        st.error("상위 폴더 .env에 OPENWEATHER_API_KEY를 입력해 주세요.")
        st.code(str(env_path), language=None)
        st.stop()

    st.subheader("01. 여행지 찾기")
    with st.form("destination_search"):
        query = st.text_input("전세계 도시·지역 이름", placeholder="서울 / Tokyo,JP / Paris,FR / New York,US")
        submitted = st.form_submit_button("✈️ 여행지 검색", use_container_width=True)
    if submitted:
        if not query.strip():
            st.warning("검색할 지역 이름을 입력해 주세요.")
        else:
            try:
                with st.spinner("여행지를 찾고 있어요..."):
                    ss.geo_results = search_locations(query.strip(), weather_key)
                ss.geo_index = 0
                ss.search_context = None
                if not ss.geo_results:
                    st.info("검색 결과가 없습니다. 영문 지역명 또는 도시명,국가코드로 다시 검색해 주세요.")
            except APIError as exc:
                st.error(str(exc))
    if not ss.geo_results:
        render_shop_picks()
        st.info("여행지를 검색하면 날씨·환율·주변 장소를 확인할 수 있어요.")
        st.stop()
    results = ss.geo_results
    index = st.selectbox("검색된 여행지", range(len(results)), key="geo_index",
                         format_func=lambda i: results[i]["label"] + f" ({results[i]['lat']:.3f}, {results[i]['lon']:.3f})")
    location = ss.geo_results[index]
    lat, lon = location["lat"], location["lon"]
    radius = st.select_slider("주변 검색 반경", options=[500, 1000, 2000, 3000, 5000], value=2000,
                              format_func=lambda n: f"{n / 1000:g} km")
    context = (lat, lon, location["country"], radius)
    if ss.search_context != context:
        ss.search_context = context
        ss.places, ss.place_total, ss.place_mode, ss.place_error = [], 0, None, ""

    currencies = country_currencies(location["country"])
    with st.expander("현지 통화 설정", expanded=not bool(currencies)):
        if currencies:
            currency = st.selectbox("국가별 통화", currencies, key="currency_" + location["country"],
                                    format_func=lambda c: f"{c} · {get_currency_name(c, locale='ko')}")
        else:
            currency = ""
            st.info("자동 식별한 통화가 없습니다. 아래에 통화 코드를 입력해 주세요.")
        manual = st.text_input("통화 직접 지정 (선택)", placeholder="JPY / USD / EUR",
                               key="manual_" + location["country"]).strip().upper()
        st.caption("여러 법정통화가 있으면 사용할 통화를 선택하세요. 통화 변경이 반영되지 않았다면 직접 지정할 수 있어요.")
        if manual:
            currency = manual

    left, right = st.columns(2)
    with left:
        try:
            weather = get_weather(lat, lon, weather_key)
            card("WEATHER / 오늘의 공기", f"{weather['temp']:.1f} °C · {weather['description']}",
                 f"체감 {weather['feels']:.1f} °C · 습도 {weather['humidity']}% · 현지 관측 {weather['time']}")
        except APIError as exc:
            st.warning(str(exc))
    with right:
        if not re.fullmatch(r"[A-Z]{3}", currency):
            st.info("환율을 보려면 영문 3자리 통화 코드를 지정해 주세요.")
        elif currency != "KRW" and not exchange_key:
            st.warning("상위 폴더 .env에 EXCHANGE_API_KEY를 입력해 주세요.")
        else:
            try:
                rate, updated = get_exchange(currency, exchange_key)
                card("EXCHANGE / 여행 예산", f"1 {currency} = {rate:,.4f} KRW", f"갱신: {updated}")
                amount = st.number_input(f"환산할 금액 ({currency})", min_value=0.0, max_value=1e12, value=100.0, step=10.0)
                st.caption(f"{amount:,.2f} {currency} ≈ {amount * rate:,.2f}원 · 참고 환율, 수수료 제외")
            except APIError as exc:
                st.warning(str(exc))

    st.subheader("02. 오늘 수집할 장소")
    a, b = st.columns(2)
    requested = None
    if a.button("✏️ 문구점", use_container_width=True):
        requested = "stationery"
    if b.button("🍽️ 맛집", use_container_width=True):
        requested = "food"
    st.caption("문구점은 문구·공예용품·미술품점, 맛집은 음식점·카페를 거리순으로 찾습니다. 평점 기반 추천은 아니며 OSM 등록 범위에 따라 누락될 수 있어요.")
    if requested:
        ss.places, ss.place_total, ss.place_error, ss.place_mode = [], 0, "", requested
        try:
            with st.spinner("주변 장소를 수집하고 있어요. 서버가 혼잡하면 대체 서버를 확인합니다..."):
                ss.places, ss.place_total = search_places(lat, lon, radius, requested)
        except APIError as exc:
            ss.place_error = str(exc)
    if ss.place_error:
        st.warning(ss.place_error)
    elif ss.place_mode:
        name = "문구점" if ss.place_mode == "stationery" else "맛집"
        st.caption(f"{name} · 반경 {radius / 1000:g} km · {ss.place_total}곳 중 가까운 {len(ss.places)}곳 표시")
        if not ss.places:
            st.info("등록된 장소를 찾지 못했습니다. 반경을 넓힌 뒤 버튼을 다시 눌러 주세요.")
    else:
        st.info("문구점 또는 맛집 버튼을 눌러 주변 장소를 찾아보세요.")
    books = {p["id"]: p for p in ss.bookmarks}
    route = [books[s["bookmark_id"]] for s in ss.itinerary if s["day"] == ss.travel_day]
    document = map_html(location, radius, ss.places, route, ss.travel_day)
    if hasattr(st, "iframe"):
        st.iframe(document, height=550)
    else:
        components.html(document, height=550, scrolling=False)
    if route:
        st.caption(f"DAY {ss.travel_day} · 지도에는 좌표가 있는 경로 장소를 표시합니다. 점선은 방문 순서이며 실제 도로 경로가 아닙니다. 실제 이동은 사이드바의 구간별 길찾기를 이용하세요.")
    for i, place in enumerate(ss.places, 1):
        render_html(f'''<div class="place-card">
        <strong>{i:02d}. {html.escape(place['name'])}</strong>
        <div class="paper-small">{html.escape(place['category'])} · 직선거리 {place['distance']:.2f} km<br>
        {html.escape(place['address'])}<br>{html.escape(place['hours'])}</div>
        <a href="{html.escape(place['url'], quote=True)}" target="_blank" rel="noopener noreferrer">지도에서 자세히 보기 ↗</a>
        </div>''')
        bid = hashlib.sha256(place["url"].encode()).hexdigest()[:20]
        saved = any(p["id"] == bid for p in ss.bookmarks)
        st.button("✓ 북마크됨" if saved else "🔖 북마크", key="osm_save_" + bid,
                  disabled=saved, on_click=add_bookmark, args=(dict(place, city=location["label"]),))
    render_shop_picks(location["country"])
    st.caption("WEATHER · OpenWeather / EXCHANGE · ExchangeRate-API / PLACES · OpenStreetMap & Overpass")


if __name__ == "__main__":
    main()

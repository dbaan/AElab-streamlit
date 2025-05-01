import streamlit as st
from streamlit_autorefresh import st_autorefresh
import matplotlib.pyplot as plt
import requests
from matplotlib.patches import Rectangle
import matplotlib.image as mpimg
import matplotlib.font_manager as fm
import datetime

# 30초마다 페이지 자동 새로고침 (30,000 밀리초)
st_autorefresh(interval=30000, key="datarefresh")

# --- 한글 폰트 자동 적용 ---
font_list = [f.name for f in fm.fontManager.ttflist if 'Nanum' in f.name]
if font_list:
    plt.rc('font', family=font_list[0])
else:
    plt.rc('font', family='Malgun Gothic')

# --- 배경 이미지 설정 ---
background_img = mpimg.imread('C:/Windows/AElab.png')

# --- 좌석 위치 및 이름 설정 ---
seat_positions = {
    'seat1': (100, 320),  # 주상
    'seat2': (150, 380),  # 예은
    'seat3': (200, 440),  # 동준
    'seat4': (240, 250),  # 석원
    'seat5': (350, 360),  # 유빈
    'seat6': (350, 200),  # 시현
    'seat7': (420, 180),  # 민영
    'seat8': (470, 220),  # 동현
    'seat9': (610, 320),  # 봉훈
    'seat10': (510, 120),  # 단비
    'seat11': (570, 160),  # 현석
    'seat12': (630, 200),  # 성혁 (API 없음)
    'seat13': (690, 240)   # 하성
}
seat_names = {
    'seat1': '주상',
    'seat2': '예은',
    'seat3': '동준',
    'seat4': '석원',
    'seat5': '유빈',
    'seat6': '시현',
    'seat7': '민영',
    'seat8': '동현',
    'seat9': '봉훈',
    'seat10': '단비',
    'seat11': '현석',
    'seat13': '하성'
}

# --- API URL 매핑 (성혁(seat12)는 API 없음) ---
api_urls = {
    'seat1': "https://api.thingspeak.com/channels/2767274/feeds.json?api_key=JRWF32TAAI4ZLLR0&results=2",
    'seat2': "https://api.thingspeak.com/channels/2843813/feeds.json?api_key=B2EZ1G09YMWSJKJB&results=2",
    'seat3': "https://api.thingspeak.com/channels/2843815/feeds.json?api_key=TKVRW5N66IGH6XE9&results=2",
    'seat4': "https://api.thingspeak.com/channels/2843812/feeds.json?api_key=6GNMUNCXW9LU4NA3&results=2",
    'seat5': "https://api.thingspeak.com/channels/2843819/feeds.json?api_key=HKP06RR3JXY59P4T&results=2",
    'seat6': "https://api.thingspeak.com/channels/2830357/feeds.json?api_key=6EVZS133AFU2GS4G&results=2",
    'seat7': "https://api.thingspeak.com/channels/2758005/feeds.json?api_key=QR1N5A71M9BKLH3V&results=2",
    'seat8': "https://api.thingspeak.com/channels/2752923/feeds.json?api_key=T73XSVU6T6HP6NDB&results=2",
    'seat9': "https://api.thingspeak.com/channels/2843795/feeds.json?api_key=LHKXM0XFKI2YCQ07&results=2",
    'seat10': "https://api.thingspeak.com/channels/2843811/feeds.json?api_key=CV2NOMWJPS0OQKLO&results=2",
    'seat11': "https://api.thingspeak.com/channels/2843806/feeds.json?api_key=RQTBGT7ZBCWF9GUV&results=2",
    'seat13': "https://api.thingspeak.com/channels/2843847/feeds.json?api_key=5S4S10QEPETST0JU&results=2"
}

# 임계값 설정
CO2_thresholds = (1000, 1500)
PM25_thresholds = (35, 75)

def get_color(value, thresholds):
    if value is None:
        return 'gray'
    if value <= thresholds[0]:
        return 'green'
    elif value <= thresholds[1]:
        return 'orange'
    else:
        return 'red'

# 주어진 URL의 피드에서 지정한 범위 내(valid) 데이터 중 가장 최신의 데이터를 반환하는 함수
def get_valid_sensor_data(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            st.write("API 호출 실패:", response.status_code)
            return None, None
        data = response.json()
        feeds = data.get('feeds', [])
        valid_pm_co2 = None
        valid_occ = None
        # 피드를 뒤에서 앞으로 순회하며 valid한 데이터를 찾음
        for feed in reversed(feeds):
            try:
                ts = feed.get('created_at', '')
                dt_feed = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
                sec = dt_feed.second
                # PM2.5, CO2 valid 조건: 초가 58~59, 0~1, 또는 28~31
                if valid_pm_co2 is None and ((58 <= sec <= 59) or (0 <= sec <= 1) or (28 <= sec <= 31)):
                    valid_pm_co2 = {
                        'PM25': float(feed.get('field3', 0)),
                        'CO2': float(feed.get('field4', 0)),
                        'time': ts
                    }
                # OCC valid 조건: 초가 2~5 또는 32~35
                if valid_occ is None and ((2 <= sec <= 5) or (32 <= sec <= 35)):
                    valid_occ = {
                        'occupancy': int(feed.get('field8', 0)),
                        'time': ts
                    }
                if valid_pm_co2 is not None and valid_occ is not None:
                    break
            except Exception:
                continue
        return valid_pm_co2, valid_occ
    except Exception as e:
        st.write("API 예외:", e)
        return None, None

def create_figure():
    fig, ax = plt.subplots()
    ax.imshow(background_img)

    rect_width = 70
    rect_height = 30
    for seat, (x, y) in seat_positions.items():
        lower_left = (x - rect_width / 2, y - rect_height / 2)
        outline_rect = Rectangle(lower_left, rect_width, rect_height,
                                 facecolor='none', edgecolor='black', alpha=1)
        ax.add_patch(outline_rect)
        ax.text(x, lower_left[1] - 30, seat_names.get(seat, seat),
                fontsize=7, ha='center', va='top',
                color='white', bbox=dict(facecolor='black', alpha=0.3, edgecolor='none'))
        cell_w = rect_width / 3
        left_x = lower_left[0]
        mid_x = lower_left[0] + cell_w
        right_x = lower_left[0] + 2 * cell_w

        if seat in api_urls:
            valid_pm_co2, valid_occ = get_valid_sensor_data(api_urls[seat])
            # valid 데이터가 있으면 session_state 업데이트, 없으면 기존 값을 유지
            if valid_pm_co2 is not None:
                st.session_state[f"{seat}_pm25"] = valid_pm_co2['PM25']
                st.session_state[f"{seat}_co2"] = valid_pm_co2['CO2']
                st.session_state[f"{seat}_pm_co2_time"] = valid_pm_co2['time']
            if valid_occ is not None:
                st.session_state[f"{seat}_occ"] = valid_occ['occupancy']
                st.session_state[f"{seat}_occ_time"] = valid_occ['time']

            pm25 = st.session_state.get(f"{seat}_pm25", None)
            co2 = st.session_state.get(f"{seat}_co2", None)
            occ = st.session_state.get(f"{seat}_occ", None)
        else:
            pm25, co2, occ = None, None, None

        pm25_text = str(int(pm25)) if pm25 is not None else "N/A"
        co2_text = str(int(co2)) if co2 is not None else "N/A"
        occ_text = "O" if (occ is not None and occ == 1) else ("X" if occ is not None else "N/A")
        pm25_color = get_color(pm25, PM25_thresholds)
        co2_color = get_color(co2, CO2_thresholds)
        occ_color = 'green' if (occ is not None and occ == 1) else ('red' if occ is not None else 'gray')

        left_rect = Rectangle((left_x, lower_left[1]), cell_w, rect_height,
                              facecolor=pm25_color, edgecolor='none', alpha=0.8)
        ax.add_patch(left_rect)
        mid_rect = Rectangle((mid_x, lower_left[1]), cell_w, rect_height,
                             facecolor=co2_color, edgecolor='none', alpha=0.8)
        ax.add_patch(mid_rect)
        right_rect = Rectangle((right_x, lower_left[1]), cell_w, rect_height,
                               facecolor=occ_color, edgecolor='none', alpha=0.8)
        ax.add_patch(right_rect)

        left_center = (left_x + cell_w / 2, lower_left[1] + rect_height / 2)
        mid_center = (mid_x + cell_w / 2, lower_left[1] + rect_height / 2)
        right_center = (right_x + cell_w / 2, lower_left[1] + rect_height / 2)
        ax.text(left_center[0], left_center[1], pm25_text,
                fontsize=5, ha='center', va='center', color='black')
        ax.text(mid_center[0], mid_center[1], co2_text,
                fontsize=5, ha='center', va='center', color='black')
        ax.text(right_center[0], right_center[1], occ_text,
                fontsize=5, ha='center', va='center', color='black')

    # 상단 제목 및 데이터 수신 시간 (대표 좌석: seat1 기준)
    common_seat = list(api_urls.keys())[0]
    common_pm_co2_time = st.session_state.get(f"{common_seat}_pm_co2_time", "N/A")
    common_occ_time = st.session_state.get(f"{common_seat}_occ_time", "N/A")
    ax.text(0.5, 1.05, "실시간 센서 데이터", transform=ax.transAxes,
            ha='center', fontsize=14, clip_on=False)
    ax.text(0.5, 1.00, f"PM2.5, CO2 수신 시간: {common_pm_co2_time}", transform=ax.transAxes,
            ha='center', fontsize=12, color='black', clip_on=False)
    ax.text(0.5, 0.95, f"OCC 수신 시간: {common_occ_time}", transform=ax.transAxes,
            ha='center', fontsize=12, color='black', clip_on=False)

    # 범례 추가 (오른쪽 하단)
    legend_ax = fig.add_axes([0.60, 0.02, 0.3, 0.12])
    legend_ax.axis('off')
    lw = 0.9
    lh = 0.3
    cellw = lw / 3
    left_leg = Rectangle((0, 0.4), cellw, lh, facecolor='white', edgecolor='black')
    legend_ax.add_patch(left_leg)
    mid_leg = Rectangle((cellw, 0.4), cellw, lh, facecolor='white', edgecolor='black')
    legend_ax.add_patch(mid_leg)
    right_leg = Rectangle((2*cellw, 0.4), cellw, lh, facecolor='white', edgecolor='black')
    legend_ax.add_patch(right_leg)
    legend_ax.text(cellw/2, 0.15, "PM2.5", ha='center', va='center', fontsize=8)
    legend_ax.text(cellw+cellw/2, 0.15, "CO2", ha='center', va='center', fontsize=8)
    legend_ax.text(2*cellw+cellw/2, 0.15, "OCC", ha='center', va='center', fontsize=8)

    ax.axis('off')
    return fig

st.title("실시간 센서 데이터 모니터링")
fig = create_figure()
st.pyplot(fig)


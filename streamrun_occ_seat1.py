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
background_img = mpimg.imread('AElab.png')

# --- 좌석 위치 및 이름 설정 ---
seat_positions = {
    'seat1': (100, 320),  # 주상
    'seat2': (150, 380),  # 정은
    'seat3': (200, 440),  # 예은
    'seat4': (240, 250),  # 석원
    'seat5': (350, 360),  # 유빈
    'seat6': (350, 200),  # 시현
    'seat7': (420, 180),  # 민영
    'seat8': (470, 220),  # 동현
    'seat9': (610, 320),  # 봉훈
    'seat10': (510, 120),  # 단비
    'seat11': (570, 160),  # 다연
    'seat12': (630, 200),  # 성혁 (API 없음)
    'seat13': (690, 240)  # 동준
}
seat_names = {
    'seat1': '주상',
    'seat2': '정은',
    'seat3': '예은',
    'seat4': '석원',
    'seat5': '유빈',
    'seat6': '시현',
    'seat7': '민영',
    'seat8': '동현',
    'seat9': '봉훈',
    'seat10': '단비',
    'seat11': '다연',
    'seat13': '동준'
}

# --- API URL 매핑 (성혁(seat12)는 API 없음) ---
api_urls = {
    'seat1': "https://api.thingspeak.com/channels/2767274/feeds.json?api_key=JRWF32TAAI4ZLLR0&results=10",
    'seat2': "https://api.thingspeak.com/channels/2843847/feeds.json?api_key=5S4S10QEPETST0JU&results=10",
    'seat3': "https://api.thingspeak.com/channels/2843813/feeds.json?api_key=B2EZ1G09YMWSJKJB&results=10",
    'seat4': "https://api.thingspeak.com/channels/2843812/feeds.json?api_key=6GNMUNCXW9LU4NA3&results=10",
    'seat5': "https://api.thingspeak.com/channels/2843819/feeds.json?api_key=HKP06RR3JXY59P4T&results=10",
    'seat6': "https://api.thingspeak.com/channels/2830357/feeds.json?api_key=6EVZS133AFU2GS4G&results=10",
    'seat7': "https://api.thingspeak.com/channels/2758005/feeds.json?api_key=QR1N5A71M9BKLH3V&results=10",
    'seat8': "https://api.thingspeak.com/channels/2752923/feeds.json?api_key=T73XSVU6T6HP6NDB&results=10",
    'seat9': "https://api.thingspeak.com/channels/2843795/feeds.json?api_key=LHKXM0XFKI2YCQ07&results=10",
    'seat10': "https://api.thingspeak.com/channels/2843811/feeds.json?api_key=CV2NOMWJPS0OQKLO&results=10",
    'seat11': "https://api.thingspeak.com/channels/2843806/feeds.json?api_key=RQTBGT7ZBCWF9GUV&results=10",
    'seat13': "https://api.thingspeak.com/channels/2843815/feeds.json?api_key=TKVRW5N66IGH6XE9&results=10"
}

# 임계값 설정 (색상 결정용)
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


# PM2.5, CO2 데이터는 기존 valid 조건에 따라 처리
def get_valid_pm_co2(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            st.write("API 호출 실패:", response.status_code)
            return None
        data = response.json()
        feeds = data.get('feeds', [])
        latest_valid = None
        for feed in feeds:
            try:
                ts = feed.get('created_at', '')
                dt_feed = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
                sec = dt_feed.second
                # valid 조건: 직전 분 58~59초, 현재 분 0~2초, 또는 해당 분 28~32초
                if (sec >= 58 or sec <= 2) or (28 <= sec <= 32):
                    if latest_valid is None or dt_feed > latest_valid['dt']:
                        latest_valid = {
                            'PM25': float(feed.get('field3', 0)),
                            'CO2': float(feed.get('field4', 0)),
                            'time': ts,
                            'dt': dt_feed
                        }
            except Exception:
                continue
        if latest_valid is not None:
            latest_valid.pop('dt', None)
        return latest_valid
    except Exception as e:
        st.write("API 예외:", e)
        return None


# OCC 데이터 처리 (field6). 만약 feed의 field6가 None이면 0으로 취급
def get_valid_occ(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            st.write("API 호출 실패 (OCC):", response.status_code)
            return None
        data = response.json()
        feeds = data.get('feeds', [])
        latest_valid = None
        for feed in feeds:
            try:
                ts = feed.get('created_at', '')
                dt_feed = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
                sec = dt_feed.second
                # valid 조건: 직전 분 58~59초, 현재 분 0~2초, 또는 해당 분 28~32초
                if (sec >= 58 or sec <= 2) or (28 <= sec <= 32):
                    occ_raw = feed.get('field6')
                    # 만약 occ_raw가 None이라면 0으로 설정
                    occ_val = int(occ_raw) if occ_raw is not None else 0
                    if latest_valid is None or dt_feed > latest_valid['dt']:
                        latest_valid = {
                            'occupancy': occ_val,
                            'time': ts,
                            'dt': dt_feed
                        }
            except Exception as ex:
                st.write("OCC 처리 중 오류:", ex)
                continue
        if latest_valid is not None:
            latest_valid.pop('dt', None)
        return latest_valid
    except Exception as e:
        st.write("API OCC 예외:", e)
        return None


def create_figure():
    fig, ax = plt.subplots()
    ax.imshow(background_img)

    rect_width = 70
    rect_height = 30
    for seat, (x, y) in seat_positions.items():
        lower_left = (x - rect_width / 2, y - rect_height / 2)
        # 좌석 윤곽 사각형 추가
        outline_rect = Rectangle(lower_left, rect_width, rect_height, facecolor='none', edgecolor='black', alpha=1)
        ax.add_patch(outline_rect)
        ax.text(x, lower_left[1] - 30, seat_names.get(seat, seat), fontsize=7, ha='center', va='top',
                color='white', bbox=dict(facecolor='black', alpha=0.3, edgecolor='none'))
        cell_w = rect_width / 3
        left_x = lower_left[0]
        mid_x = lower_left[0] + cell_w
        right_x = lower_left[0] + 2 * cell_w

        # API URL이 존재하는 경우에만 센서 데이터를 업데이트
        if seat in api_urls:
            valid_pm_co2 = get_valid_pm_co2(api_urls[seat])
            if valid_pm_co2 is not None:
                st.session_state[f"{seat}_pm25"] = valid_pm_co2['PM25']
                st.session_state[f"{seat}_co2"] = valid_pm_co2['CO2']
                st.session_state[f"{seat}_pm_co2_time"] = valid_pm_co2['time']
            valid_occ = get_valid_occ(api_urls[seat])
            if valid_occ is not None:
                st.session_state[f"{seat}_occ"] = valid_occ['occupancy']
                st.session_state[f"{seat}_occ_time"] = valid_occ['time']

            pm25 = st.session_state.get(f"{seat}_pm25", None)
            co2 = st.session_state.get(f"{seat}_co2", None)
            occ_value = st.session_state.get(f"{seat}_occ", None)
        else:
            pm25, co2, occ_value = None, None, None

        pm25_text = str(int(pm25)) if pm25 is not None else "N/A"
        co2_text = str(int(co2)) if co2 is not None else "N/A"
        # field6 값이 1이면 O (재실), 0이면 X (비재실), 그 외는 N/A
        occ_text = "O" if occ_value == 1 else ("X" if occ_value == 0 else "N/A")

        pm25_color = get_color(pm25, PM25_thresholds)
        co2_color = get_color(co2, CO2_thresholds)
        occ_color = 'green' if occ_value == 1 else ('red' if occ_value == 0 else 'gray')

        left_rect = Rectangle((left_x, lower_left[1]), cell_w, rect_height, facecolor=pm25_color, edgecolor='none',
                              alpha=0.8)
        ax.add_patch(left_rect)
        mid_rect = Rectangle((mid_x, lower_left[1]), cell_w, rect_height, facecolor=co2_color, edgecolor='none',
                             alpha=0.8)
        ax.add_patch(mid_rect)
        right_rect = Rectangle((right_x, lower_left[1]), cell_w, rect_height, facecolor=occ_color, edgecolor='none',
                               alpha=0.8)
        ax.add_patch(right_rect)

        left_center = (left_x + cell_w / 2, lower_left[1] + rect_height / 2)
        mid_center = (mid_x + cell_w / 2, lower_left[1] + rect_height / 2)
        right_center = (right_x + cell_w / 2, lower_left[1] + rect_height / 2)
        ax.text(left_center[0], left_center[1], pm25_text, fontsize=5, ha='center', va='center', color='black')
        ax.text(mid_center[0], mid_center[1], co2_text, fontsize=5, ha='center', va='center', color='black')
        ax.text(right_center[0], right_center[1], occ_text, fontsize=5, ha='center', va='center', color='black')

    # 상단 제목 및 데이터 수신 시간 (대표 좌석: seat1 기준)
    common_seat = list(api_urls.keys())[0]
    common_pm_co2_time = st.session_state.get(f"{common_seat}_pm_co2_time", "N/A")
    common_occ_time = st.session_state.get(f"{common_seat}_occ_time", "N/A")
    ax.text(0.5, 1.05, "실시간 센서 데이터", transform=ax.transAxes, ha='center', fontsize=14, clip_on=False)
    ax.text(0.5, 1.00, f"PM2.5, CO2 수신 시간: {common_pm_co2_time}", transform=ax.transAxes, ha='center', fontsize=12,
            color='black', clip_on=False)
    ax.text(0.5, 0.95, f"OCC 수신 시간: {common_occ_time}", transform=ax.transAxes, ha='center', fontsize=12, color='black',
            clip_on=False)

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
    right_leg = Rectangle((2 * cellw, 0.4), cellw, lh, facecolor='white', edgecolor='black')
    legend_ax.add_patch(right_leg)
    legend_ax.text(cellw / 2, 0.15, "PM2.5", ha='center', va='center', fontsize=8)
    legend_ax.text(cellw + cellw / 2, 0.15, "CO2", ha='center', va='center', fontsize=8)
    legend_ax.text(2 * cellw + cellw / 2, 0.15, "OCC", ha='center', va='center', fontsize=8)

    ax.axis('off')
    return fig


st.title("실시간 센서 데이터 모니터링")
fig = create_figure()
st.pyplot(fig)

import matplotlib.pyplot as plt
import requests
from matplotlib.animation import FuncAnimation
import matplotlib.image as mpimg
import matplotlib.font_manager as fm
from matplotlib.patches import Rectangle

# --- 한글 폰트 자동 적용 ---
font_list = [f.name for f in fm.fontManager.ttflist if 'Nanum' in f.name]
if font_list:
    plt.rc('font', family=font_list[0])
else:
    plt.rc('font', family='Malgun Gothic')
print("현재 적용된 폰트:", plt.rcParams['font.family'])

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
    'seat12': (630, 200),  # 성혁
    'seat13': (690, 240)  # 하성
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
    'seat12': '성혁',
    'seat13': '하성'
}

# --- API URL 매핑 (성혁(seat12) 제외) ---
api_urls = {
    'seat1': "https://api.thingspeak.com/channels/2767274/feeds.json?api_key=JRWF32TAAI4ZLLR0&results=2",  # 주상
    'seat2': "https://api.thingspeak.com/channels/2843813/feeds.json?api_key=B2EZ1G09YMWSJKJB&results=2",  # 예은
    'seat3': "https://api.thingspeak.com/channels/2843815/feeds.json?api_key=TKVRW5N66IGH6XE9&results=2",  # 동준
    'seat4': "https://api.thingspeak.com/channels/2843812/feeds.json?api_key=6GNMUNCXW9LU4NA3&results=2",  # 석원
    'seat5': "https://api.thingspeak.com/channels/2843819/feeds.json?api_key=HKP06RR3JXY59P4T&results=2",  # 유빈
    'seat6': "https://api.thingspeak.com/channels/2830357/feeds.json?api_key=6EVZS133AFU2GS4G&results=2",  # 시현
    'seat7': "https://api.thingspeak.com/channels/2758005/feeds.json?api_key=QR1N5A71M9BKLH3V&results=2",  # 민영
    'seat8': "https://api.thingspeak.com/channels/2752923/feeds.json?api_key=T73XSVU6T6HP6NDB&results=2",  # 동현
    'seat9': "https://api.thingspeak.com/channels/2843795/feeds.json?api_key=LHKXM0XFKI2YCQ07&results=2",  # 봉훈
    'seat10': "https://api.thingspeak.com/channels/2843811/feeds.json?api_key=CV2NOMWJPS0OQKLO&results=2",  # 단비
    'seat11': "https://api.thingspeak.com/channels/2843806/feeds.json?api_key=RQTBGT7ZBCWF9GUV&results=2",  # 현석
    'seat13': "https://api.thingspeak.com/channels/2843847/feeds.json?api_key=5S4S10QEPETST0JU&results=2"  # 하성
}

# 임계값 설정
CO2_thresholds = (1000, 1500)
PM25_thresholds = (35, 75)


# 센서 값에 따른 색상 결정 함수
def get_color(value, thresholds):
    if value is None:
        return 'gray'
    if value <= thresholds[0]:
        return 'green'
    elif value <= thresholds[1]:
        return 'orange'
    else:
        return 'red'


# API 호출 및 데이터 파싱
def get_sensor_data(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            feeds = data.get('feeds', [])
            if feeds:
                latest_data = feeds[-1]
                try:
                    pm25 = float(latest_data.get('field3', 0))
                except:
                    pm25 = 0.0
                try:
                    co2 = float(latest_data.get('field4', 0))
                except:
                    co2 = 0.0
                try:
                    occupancy = int(latest_data.get('field8', 0))
                except:
                    occupancy = 0
                timestamp = latest_data.get('created_at', '')
                return {'PM25': pm25, 'CO2': co2, 'occupancy': occupancy, 'time': timestamp}
            else:
                return None
        else:
            print("API 호출 실패:", response.status_code)
            return None
    except Exception as e:
        print("API 예외:", e)
        return None


fig, ax = plt.subplots()


def update(frame):
    print("update 호출됨")
    ax.clear()
    ax.imshow(background_img)

    # 각 좌석 표시 (70×30 사각형, 3등분)
    rect_width = 70
    rect_height = 30
    for seat, (x, y) in seat_positions.items():
        # 사각형 outline
        lower_left = (x - rect_width / 2, y - rect_height / 2)
        outline_rect = Rectangle(lower_left, rect_width, rect_height,
                                 facecolor='none', edgecolor='black', alpha=1)
        ax.add_patch(outline_rect)

        # 좌석 이름 (사각형 하단 10픽셀 아래)
        ax.text(x, lower_left[1] - 30, seat_names.get(seat, seat),
                fontsize=7, ha='center', va='top',
                color='white', bbox=dict(facecolor='black', alpha=0.3, edgecolor='none'))

        # 3등분 셀 (왼: PM2.5, 중간: CO2, 오른쪽: occ)
        cell_w = rect_width / 3  # 20픽셀
        # 각 셀 좌표
        left_x = lower_left[0]
        mid_x = lower_left[0] + cell_w
        right_x = lower_left[0] + 2 * cell_w

        # API 데이터 있으면 표시, 없으면 None
        if seat in api_urls:
            sensor_data = get_sensor_data(api_urls[seat])
            if sensor_data:
                pm25 = sensor_data['PM25']
                co2 = sensor_data['CO2']
                occ = sensor_data['occupancy']
            else:
                pm25 = None;
                co2 = None;
                occ = None
        else:
            # 성혁(seat12) 등 API가 없는 경우
            pm25 = None;
            co2 = None;
            occ = None

        # 각 값 텍스트
        pm25_text = str(int(pm25)) if pm25 is not None else "N/A"
        co2_text = str(int(co2)) if co2 is not None else "N/A"
        occ_text = "O" if (occ is not None and occ == 1) else ("X" if occ is not None else "N/A")

        # 각 셀 색상
        pm25_color = get_color(pm25, PM25_thresholds)
        co2_color = get_color(co2, CO2_thresholds)
        occ_color = 'green' if (occ is not None and occ == 1) else ('red' if occ is not None else 'gray')

        # 왼쪽 셀
        left_rect = Rectangle((left_x, lower_left[1]), cell_w, rect_height,
                              facecolor=pm25_color, edgecolor='none', alpha=0.8)
        ax.add_patch(left_rect)
        # 중앙 셀
        mid_rect = Rectangle((mid_x, lower_left[1]), cell_w, rect_height,
                             facecolor=co2_color, edgecolor='none', alpha=0.8)
        ax.add_patch(mid_rect)
        # 오른쪽 셀
        right_rect = Rectangle((right_x, lower_left[1]), cell_w, rect_height,
                               facecolor=occ_color, edgecolor='none', alpha=0.8)
        ax.add_patch(right_rect)

        # 각 셀 중앙에 텍스트 (폰트 5)
        left_center = (left_x + cell_w / 2, lower_left[1] + rect_height / 2)
        mid_center = (mid_x + cell_w / 2, lower_left[1] + rect_height / 2)
        right_center = (right_x + cell_w / 2, lower_left[1] + rect_height / 2)

        ax.text(left_center[0], left_center[1], pm25_text,
                fontsize=5, ha='center', va='center', color='black')
        ax.text(mid_center[0], mid_center[1], co2_text,
                fontsize=5, ha='center', va='center', color='black')
        ax.text(right_center[0], right_center[1], occ_text,
                fontsize=5, ha='center', va='center', color='black')

    # 상단 제목 및 공통 데이터 수신 시간
    common_seat = list(api_urls.keys())[0]
    data = get_sensor_data(api_urls[common_seat])
    timestamp = data['time'] if data else ''
    ax.text(0.5, 1.05, "실시간 센서 데이터", transform=ax.transAxes,
            ha='center', fontsize=14, clip_on=False)
    ax.text(0.5, 1.00, f"데이터 수신 시간: {timestamp}", transform=ax.transAxes,
            ha='center', fontsize=12, color='black', clip_on=False)

    # 범례 (오른쪽 하단)
    # 새 축을 추가해서, 하나의 사각형을 3등분한 형태로 그리고 아래에 "PM2.5", "CO2", "occ" 표시
    legend_ax = fig.add_axes([0.60, 0.02, 0.3, 0.12])  # [left, bottom, width, height]
    legend_ax.axis('off')
    # 범례용 사각형 크기
    lw = 0.9  # 가로 길이(정규화)
    lh = 0.3
    cellw = lw / 3
    # 왼쪽 셀
    left_rect = Rectangle((0, 0.4), cellw, lh, facecolor='white', edgecolor='black')
    legend_ax.add_patch(left_rect)
    # 중간 셀
    mid_rect = Rectangle((cellw, 0.4), cellw, lh, facecolor='white', edgecolor='black')
    legend_ax.add_patch(mid_rect)
    # 오른쪽 셀
    right_rect = Rectangle((2 * cellw, 0.4), cellw, lh, facecolor='white', edgecolor='black')
    legend_ax.add_patch(right_rect)
    # 텍스트
    legend_ax.text(cellw / 2, 0.15, "PM2.5", ha='center', va='center', fontsize=8)
    legend_ax.text(cellw + cellw / 2, 0.15, "CO2", ha='center', va='center', fontsize=8)
    legend_ax.text(2 * cellw + cellw / 2, 0.15, "OCC", ha='center', va='center', fontsize=8)

    ax.axis('off')


anim = FuncAnimation(fig, update, interval=30000, cache_frame_data=False)
plt.show()

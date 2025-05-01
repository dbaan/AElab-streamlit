import matplotlib.pyplot as plt  # 2D 그래프 및 이미지 출력을 위한 모듈
import requests
from matplotlib.animation import FuncAnimation  # 주기적으로 화면을 갱신하기 위한 모듈
import matplotlib.image as mpimg  # 이미지 파일 읽기를 위한 모듈
import matplotlib.font_manager as fm  # 폰트 관련 모듈

# --- 한글 폰트 자동 적용 ---
font_list = [f.name for f in fm.fontManager.ttflist if 'Nanum' in f.name]
if font_list:
    plt.rc('font', family=font_list[0])
else:
    plt.rc('font', family='Malgun Gothic')
print("현재 적용된 폰트:", plt.rcParams['font.family'])
# -------------------------------

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
    'seat12': (630, 200),  # 성혁 (제외)
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

# --- 임계값 설정 ---
CO2_thresholds = (1000, 1500)
PM25_thresholds = (35, 75)


# --- 센서 값에 따른 색상 결정 함수 ---
def get_color(value, thresholds):
    if value <= thresholds[0]:
        return 'green'
    elif value <= thresholds[1]:
        return 'orange'
    else:
        return 'red'


# --- API 호출 및 데이터 파싱 함수 ---
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
            print("API 호출 실패, 상태 코드:", response.status_code)
            return None
    except Exception as e:
        print("API 호출 중 예외 발생:", e)
        return None


# --- Figure와 Axes 생성 ---
fig, ax = plt.subplots()


def update(frame):
    print("update 호출됨")
    ax.clear()
    ax.imshow(background_img)
    # 모든 좌석 기본 표시 (성혁(seat12) 제외)
    for seat, (x, y) in seat_positions.items():
        if seat == 'seat12':
            continue
        ax.scatter(x, y, color='blue', s=200)
        ax.text(x, y, seat_names.get(seat, seat), color='white',
                fontsize=10, ha='center', va='center')
    # 상단 제목 및 공통 데이터 수신 시간 (첫 번째 API URL의 타임스탬프 사용)
    common_seat = list(api_urls.keys())[0]
    common_data = get_sensor_data(api_urls[common_seat])
    if common_data:
        common_timestamp = common_data['time']
    else:
        common_timestamp = ''
    ax.text(0.5, 1.05, "실시간 센서 데이터", transform=ax.transAxes,
            ha='center', fontsize=14, clip_on=False)
    ax.text(0.5, 1.00, f"데이터 수신 시간: {common_timestamp}", transform=ax.transAxes,
            ha='center', fontsize=12, color='black', clip_on=False)

    # 각 좌석별 센서 데이터 업데이트 (성혁 제외)
    for seat, url in api_urls.items():
        pos = seat_positions[seat]
        sensor_data = get_sensor_data(url)
        if sensor_data:
            pm25 = sensor_data['PM25']
            co2 = sensor_data['CO2']
            occupancy = sensor_data['occupancy']
        else:
            pm25 = None;
            co2 = None;
            occupancy = None
        # 센서 데이터 원들의 위치: PM2.5 좌측, CO2 중앙, occ 우측 (좌석 기준 x에서 각각 -140, 0, +140; y offset: -40)
        pos_pm = (pos[0] - 140, pos[1] - 40)
        pos_co2 = (pos[0], pos[1] - 40)
        pos_occ = (pos[0] + 140, pos[1] - 40)
        if pm25 is not None:
            circle_pm = plt.Circle(pos_pm, 20, color=get_color(pm25, PM25_thresholds), alpha=0.5)
            ax.add_patch(circle_pm)
            ax.text(pos_pm[0], pos_pm[1] - 30, f"PM2.5: {pm25}", fontsize=8, color='black',
                    ha='center', bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))
        if co2 is not None:
            circle_co2 = plt.Circle(pos_co2, 20, color=get_color(co2, CO2_thresholds), alpha=0.5)
            ax.add_patch(circle_co2)
            ax.text(pos_co2[0], pos_co2[1] - 30, f"CO2: {co2}", fontsize=8, color='black',
                    ha='center', bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))
        if occupancy is not None:
            occ_color = 'green' if occupancy == 1 else 'red'
            circle_occ = plt.Circle(pos_occ, 20, color=occ_color, alpha=0.5)
            ax.add_patch(circle_occ)
            occ_text = "O" if occupancy == 1 else "X"
            ax.text(pos_occ[0], pos_occ[1] - 30, f"재실: {occ_text}", fontsize=8, color='black',
                    ha='center', bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))

    ax.axis('off')


anim = FuncAnimation(fig, update, interval=30000, cache_frame_data=False)
plt.show()

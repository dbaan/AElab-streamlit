import matplotlib.pyplot as plt  # 2D 그래프 및 이미지 출력을 위한 모듈
import requests
from matplotlib.animation import FuncAnimation  # 주기적으로 화면을 갱신하기 위한 모듈
import matplotlib.image as mpimg  # 이미지 파일 읽기를 위한 모듈
import matplotlib.font_manager as fm  # 폰트 관련 모듈
# --- 한글 폰트 자동 적용 ---
# fontManager의 ttflist에서 'Nanum'이라는 이름이 포함된 폰트를 찾습니다.
font_list = [f.name for f in fm.fontManager.ttflist if 'Nanum' in f.name]
if font_list:
    plt.rc('font', family=font_list[0])  # 나눔고딕 폰트가 있으면 적용
else:
    plt.rc('font', family='Malgun Gothic')  # 없으면 맑은 고딕 사용
# 적용된 폰트 확인
print("현재 적용된 폰트:", plt.rcParams['font.family'])
# -------------------------------
# --- 배경 이미지 설정 ---
# 배경 이미지 파일 경로를 C:/Windows/AElab.png 로 변경
background_img = mpimg.imread('C:/Windows/AElab.png')
# --- 좌석 위치 및 이름 설정 ---
seat_positions = {
    'seat1': (100, 320),
    'seat2': (150, 380),
    'seat3': (200, 440),
    'seat4': (240, 250),
    'seat5': (350, 360),
    'seat6': (350, 200),
    'seat7': (420, 180),
    'seat8': (470, 220),
    'seat9': (610, 320),
    'seat10': (510, 120),  # 단비
    'seat11': (570, 160),
    'seat12': (630, 200),
    'seat13': (690, 240)
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
# --- API 주소 및 센서 필드 설정 ---
# field3: PM2.5, field4: CO2, field6: 재실여부
API_URL = "https://api.thingspeak.com/channels/2752923/feeds.json?api_key=T73XSVU6T6HP6NDB&results=2"
# --- 센서 값에 따른 색상 결정 함수 ---
def get_color(value, thresholds):
    if value <= thresholds[0]:
        return 'green'
    elif value <= thresholds[1]:
        return 'orange'
    else:
        return 'red'
CO2_thresholds = (1000, 1500)
PM25_thresholds = (35, 75)
# --- API 호출 및 데이터 파싱 함수 ---
def get_sensor_data():
    try:
        response = requests.get(API_URL)
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
# --- 인터랙티브 플롯 창을 위한 설정 ---
# 만약 외부 창에서 업데이트를 확인하고 싶다면 plt.ion()를 사용하는 것이 좋습니다.
plt.ion()
# --- Figure와 Axes 생성 ---
fig, ax = plt.subplots()
def update(frame):
    print("update 호출됨")  # 디버깅용: 콘솔에 주기적으로 출력되어야 함
    ax.clear()  # 이전 그림 지우기
    ax.imshow(background_img)  # 배경 이미지 표시
    # 단비(seat10) 제외 모든 좌석 표시
    for seat, (x, y) in seat_positions.items():
        if seat != 'seat8':
            ax.scatter(x, y, color='blue', s=200)
            ax.text(x, y, seat_names.get(seat, seat), color='white',
                    fontsize=10, ha='center', va='center')
    # 제목과 데이터 수신 시간 표시 (axes 좌표계 사용, 0~1 범위)
    ax.text(0.5, 1.05, "실시간 센서 데이터 (동현)", transform=ax.transAxes,
            ha='center', fontsize=14, clip_on=False)
    sensor_data = get_sensor_data()
    if sensor_data:
        pm25 = sensor_data['PM25']
        co2 = sensor_data['CO2']
        occupancy = sensor_data['occupancy']
        timestamp = sensor_data.get('time', '')
        ax.text(0.5, 1.00, f"데이터 수신 시간: {timestamp}", transform=ax.transAxes,
                ha='center', fontsize=12, color='black', clip_on=False)
        # 단비(seat10) 좌석의 센서 데이터 표시
        x, y = seat_positions['seat8']
        # 센서 데이터 원들의 위치: PM2.5는 좌측, CO2는 중앙, 재실은 우측(좌석 기준 x에서 각각 -140, 0, +140)
        pos_pm = (x - 140, y - 40)
        pos_co2 = (x, y - 40)
        pos_occ = (x + 140, y - 40)
        circle_pm = plt.Circle(pos_pm, 20, color=get_color(pm25, PM25_thresholds), alpha=0.5)
        ax.add_patch(circle_pm)
        circle_co2 = plt.Circle(pos_co2, 20, color=get_color(co2, CO2_thresholds), alpha=0.5)
        ax.add_patch(circle_co2)
        occ_color = 'green' if occupancy == 1 else 'red'
        circle_occ = plt.Circle(pos_occ, 20, color=occ_color, alpha=0.5)
        ax.add_patch(circle_occ)
        # 각 센서 데이터 원 아래 텍스트 표시 (폰트 크기 8, 하얀 배경)
        ax.text(pos_pm[0], pos_pm[1] - 30, f"PM2.5: {pm25}", fontsize=8, color='black', ha='center',
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))
        ax.text(pos_co2[0], pos_co2[1] - 30, f"CO2: {co2}", fontsize=8, color='black', ha='center',
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))
        occ_text = "O" if occupancy == 1 else "X"
        ax.text(pos_occ[0], pos_occ[1] - 30, f"재실: {occ_text}", fontsize=8, color='black', ha='center',
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))
        # 단비 좌석 이름 표시 (원 중앙, 반투명 배경)
        ax.text(x, y, seat_names.get('seat8', 'seat8'), color='white',
                fontsize=10, ha='center', va='center',
                bbox=dict(facecolor='black', alpha=0.3, edgecolor='none'))
    else:
        x, y = seat_positions['seat8']
        ax.text(x, y, "데이터 없음", fontsize=10, color='red', ha='center')
    ax.axis('off')
# --- 애니메이션 객체 생성 ---
anim = FuncAnimation(fig, update, interval=30000, cache_frame_data=False)
plt.show()

# ==============================================================================
# api/index.py - 최종 통합본
# ==============================================================================

# --- 1. 라이브러리 불러오기 및 .env 파일 로드 ---
# 이 부분이 가장 먼저 실행되어 .env 파일에서 API 키를 불러옵니다.
from dotenv import load_dotenv
from pathlib import Path
import os

# 어떤 상황에서도 정확한 경로의 .env 파일을 읽어오도록 경로를 직접 계산합니다.
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


# --- 2. 나머지 라이브러리 및 Flask 앱 설정 ---
from flask import Flask, request, jsonify, render_template
import requests
import math

# Vercel 및 로컬 환경에서 카카오 API 키 가져오기
KAKAO_API_KEY = os.environ.get('KAKAO_API_KEY')

# Flask 앱 초기화. templates 폴더 위치를 정확히 알려줍니다.
app = Flask(__name__, template_folder='../templates')


# --- 3. 메인 페이지를 보여주는 기능 ---
# 사용자가 처음 접속했을 때 index.html을 보여줍니다.
@app.route('/')
def home():
    return render_template('index.html')


# --- 4. 주변 동네를 검색하는 핵심 API 기능 ---
@app.route('/api/search')
def search_nearby():
    # 웹페이지에서 보낸 검색어와 거리 값을 받습니다.
    query = request.args.get('q')
    distance_limit = request.args.get('distance', default=10, type=int)
    
    # 검색어가 없으면 오류 메시지를 보냅니다.
    if not query:
        return jsonify({"error": "검색어를 입력하세요"}), 400
    
    # .env 파일에서 API 키를 제대로 못 읽어왔으면 오류 메시지를 보냅니다.
    if not KAKAO_API_KEY:
        return jsonify({"error": "서버에 카카오 API 키가 설정되지 않았습니다."}), 500

    try:
        # 1. 출발점 좌표 얻기 (지오코딩)
        headers = {'Authorization': f'KakaoAK {KAKAO_API_KEY}'}
        geo_url = f'https://dapi.kakao.com/v2/local/search/address.json?query={query}'
        geo_response = requests.get(geo_url, headers=headers).json()
        
        if not geo_response.get('documents'):
            return jsonify({"error": "주소를 찾을 수 없습니다."}), 404
            
        start_lon = float(geo_response['documents'][0]['x']) # 경도
        start_lat = float(geo_response['documents'][0]['y']) # 위도

        # 2. 주변 가상 좌표 생성하기
        step = 0.01 
        nearby_dongs = set()
        
        lat_range = int((distance_limit * 0.009) / step)
        lon_range = int((distance_limit * 0.011) / step)

        for i in range(-lat_range, lat_range + 1):
            for j in range(-lon_range, lon_range + 1):
                check_lat = start_lat + i * step
                check_lon = start_lon + j * step

                # 3. 좌표를 주소로 바꾸기 (리버스 지오코딩)
                reverse_geo_url = f'https://dapi.kakao.com/v2/local/geo/coord2address.json?x={check_lon}&y={check_lat}'
                reverse_response = requests.get(reverse_geo_url, headers=headers).json()

                if reverse_response.get('documents'):
                    address_info = reverse_response['documents'][0]
                    if address_info.get('address') and address_info['address'].get('region_2depth_name') and address_info['address'].get('region_3depth_name'):
                        sgg = address_info['address']['region_2depth_name']
                        dong = address_info['address']['region_3depth_name']
                        nearby_dongs.add(f"{sgg} {dong}")

        # 4. 결과 정리하기
        if not nearby_dongs:
            return jsonify({"result": "주변 동네를 찾을 수 없습니다."})

        result_string = ",".join(sorted(list(nearby_dongs)))
        
        return jsonify({"result": result_string})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- 5. 로컬 테스트를 위한 실행 코드 ---
# 이 부분은 Vercel에서는 무시되고, 우리 컴퓨터에서 python api/index.py를 실행할 때만 작동합니다.
if __name__ == '__main__':
    app.run(debug=True)
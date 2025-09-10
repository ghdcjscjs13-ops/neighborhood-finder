from dotenv import load_dotenv
from pathlib import Path
import os

print("--- .env 파일 읽기 테스트 시작 ---")

# api/index.py 와 동일한 방법으로 .env 파일 경로를 찾습니다.
env_path = Path(__file__).resolve().parent / '.env'

# .env 파일을 로드하고, 성공 여부를 변수에 저장합니다.
was_loaded = load_dotenv(dotenv_path=env_path)

if not was_loaded:
    print(f"경고: {env_path} 경로에서 .env 파일을 찾지 못했습니다.")

# KAKAO_API_KEY 환경 변수를 읽어옵니다.
api_key = os.environ.get('KAKAO_API_KEY')

if api_key:
    # 키의 일부만 보여줘서 유출을 방지합니다.
    print(f"✅ 성공: .env 파일에서 API 키를 읽었습니다.")
    print(f"   - 읽어온 키 (앞 4자리): {api_key[:4]}****")
else:
    print("❌ 실패: .env 파일에서 KAKAO_API_KEY를 찾을 수 없습니다.")
    print("   - .env 파일 이름이 정확한지 (예: .env.txt 가 아닌지) 확인하세요.")
    print(f"   - .env 파일이 {env_path} 경로에 있는지 확인하세요.")

print("--- 테스트 종료 ---")
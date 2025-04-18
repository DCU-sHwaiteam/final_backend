from app import create_app
from dotenv import load_dotenv
import os

# .env 파일 로드 전에 환경 변수를 덮어쓰지 않도록
dotenv_path = "/home/ec2-user/flask_backend/.env"

# .env 파일 로드
load_dotenv(dotenv_path=dotenv_path)

# .env 파일이 제대로 로드되었는지 확인
print("🌍 .env loaded DB_HOST =", os.getenv("DB_HOST"))
print("🌍 .env path:", dotenv_path)

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

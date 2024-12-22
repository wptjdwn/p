from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx
from starlette.requests import Request

app = FastAPI()

templates = Jinja2Templates(directory="templates")

API_KEY = ""
BASE_URL = "https://www.koreaexim.go.kr/site/program/financial/exchangeJSON"

async def fetch_exchange_rates():
    try:
        async with httpx.AsyncClient() as client:
            url = f"{BASE_URL}?authkey={API_KEY}&searchdate=20231223&data=AP01"  # API 요청 URL
            response = await client.get(url)
            response.raise_for_status()  # 응답 상태가 2xx 범위 외면 예외 발생
            data = response.json()
            if data:
                rates = {}
                for item in data:
                    currency = item['curr_cd']
                    if currency in ['USD', 'EUR', 'KRW']:
                        rates[currency] = item['deal_bas_r']
                return rates
            else:
                raise ValueError("환율 데이터를 찾을 수 없습니다.")
    except httpx.HTTPStatusError as http_error:
        raise HTTPException(status_code=500, detail=f"HTTP 요청 오류: {http_error}")
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"환율 데이터를 처리하는 중 오류 발생: {error}")

# 환율 데이터를 반환하는 API 엔드포인트
@app.get("/api/exchange-rates/")
async def get_exchange_rates():
    rates = await fetch_exchange_rates()
    return rates

# 메인 화면을 보여주는 엔드포인트
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):  # request를 인자로 받아야 함
    try:
        rates = await fetch_exchange_rates()  # 환율 정보 가져오기
        return templates.TemplateResponse("index.html", {"request": request, "rates": rates})
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"템플릿 처리 오류: {str(e)}")

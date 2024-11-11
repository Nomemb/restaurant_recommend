from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# 정적 파일 서빙 (map.html이 프로젝트 루트 디렉토리에 있는 경우)
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/map", response_class=HTMLResponse)
async def get_map(request: Request):
    # `map.html` 파일을 반환
    with open("map.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)
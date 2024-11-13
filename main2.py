from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

import folium
import requests
import pandas as pd
import logging
from scripts import mongo_db
app = FastAPI()

# Static and templates setup
app.mount("/static", StaticFiles(directory="."), name="static")
templates = Jinja2Templates(directory="templates")
logger = logging.getLogger("uvicorn.error")

# Google Maps Geocoding API 키 설정 (본인의 키로 교체하세요)
GOOGLE_API_KEY = "AIzaSyDHYYrVTyeLmyjfMAV7RDZrk-aNhf-ZoOw"

# 예시 데이터프레임 (식당 데이터)
path = f"dataset/test.json"
restaurant_df = pd.read_json(path)


def get_coordinates_google(address):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": GOOGLE_API_KEY}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            latitude = data["results"][0]["geometry"]["location"]["lat"]
            longitude = data["results"][0]["geometry"]["location"]["lng"]
            return [latitude, longitude]

    return None

def generate_map(current_location, address):
    map_folium = folium.Map(location=current_location, zoom_start=15)
    folium.Marker(
        location=current_location,
        popup=address,
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(map_folium)

    for row in mongo_db.select_all_data():
        popup_text = f"""
        <b>식당 이름:</b> {row["store_name"]}<br>
        <b>식당 주소:</b> {row["addr"]}<br>
        <b>별점:</b> {row["score"]}점<br>
        <b>설명:</b> {row["summary"]}
        """
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            popup=folium.Popup(popup_text, max_width=1000),
            icon=folium.Icon(color='red', icon='cutlery')
        ).add_to(map_folium)

    map_folium.save('map.html')

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/maps/")
async def get_location(address: str = Form(...)):
    coordinates = get_coordinates_google(address)
    if coordinates:
        generate_map(coordinates, address)
        sorted_restaurants = restaurant_df.copy()
        sorted_restaurants['distance'] = (
            (sorted_restaurants['latitude'] - coordinates[0])**2 +
            (sorted_restaurants['longitude'] - coordinates[1])**2
        ) ** 0.5
        sorted_restaurants = sorted_restaurants.sort_values(by='distance').head(3)
        return templates.TemplateResponse(
            "recommend.html",
            {
                "request": {},
                "address": address,
                "restaurants": sorted_restaurants.to_dict(orient="records"),
                "map_url": "/static/map.html"
            }
        )

generate_map(get_coordinates_google("노량진역"), "노량진역")
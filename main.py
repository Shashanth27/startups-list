from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio
from scraper import scrape_startups, save_data
import os

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

@app.get("/scrape/{start_page}/{end_page}")
async def scrape(start_page: int, end_page: int):
    try:
        if start_page > end_page:
            raise HTTPException(status_code=400, detail="Start page cannot be greater than end page")
            
        data = await scrape_startups(start_page, end_page)
        if data.empty:
            return {"status": "error", "message": "No data found"}
            
        csv_path = save_data(data)
        return {
            "status": "success",
            "count": len(data),
            "data": data.to_dict('records'),
            "file_path": csv_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join("output", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename)
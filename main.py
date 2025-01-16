import logging
import asyncio
from fastapi import FastAPI
# FUT: Enable while using with UI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.api import api_router
from api.v1.portfolio.portfolio_routes import run_hourly_updates

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI setup
app = FastAPI()

# Allow all origins to make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow any origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
async def health_check():
    return {"message": "ok"}

# v1 sub-router 
app.include_router(api_router, prefix="/v1")

ascii_art = """
╭━━╮╱╱╱╭╮╱╭┳━━┳╮╱╱╭┳━━━╮
┃╭╮┃╱╱╱┃┃╱┃┣┫┣┫╰╮╭╯┃╭━━╯
┃╰╯╰╮╱╱┃╰━╯┃┃┃╰╮┃┃╭┫╰━━╮
┃╭━╮┣━━┫╭━╮┃┃┃╱┃╰╯┃┃╭━━╯
┃╰━╯┣━━┫┃╱┃┣┫┣╮╰╮╭╯┃╰━━╮
╰━━━╯╱╱╰╯╱╰┻━━╯╱╰╯╱╰━━━╯
"""
print(ascii_art)

@app.on_event("startup")
async def startup_event():
    """
    Startup event to run the hourly updates in the background.
    """
    logger.info("Starting hourly updates...")
    asyncio.create_task(run_hourly_updates())
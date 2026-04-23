import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from database import (
    create_recipe, delete_recipe, get_all_recipes, get_recipe,
    init_db, update_recipe, update_recipe_error,
)
from extractor import extract_recipe

app = FastAPI(title="Reel Recipe")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_executor = ThreadPoolExecutor(max_workers=3)


@app.on_event("startup")
async def startup():
    init_db()


class ReelRequest(BaseModel):
    url: str


async def _process_reel_task(recipe_id: int, url: str):
    loop = asyncio.get_event_loop()
    try:
        data = await loop.run_in_executor(_executor, extract_recipe, url)
        update_recipe(recipe_id, data)
        print(f"Recipe {recipe_id} ready: {data.get('title')}")
    except Exception as e:
        update_recipe_error(recipe_id, str(e))
        print(f"Recipe {recipe_id} failed: {e}")


@app.post("/api/reels")
async def submit_reel(request: ReelRequest, background_tasks: BackgroundTasks):
    recipe_id = create_recipe(request.url)
    background_tasks.add_task(_process_reel_task, recipe_id, request.url)
    return {"id": recipe_id, "status": "processing"}


@app.get("/api/recipes")
async def list_recipes():
    return get_all_recipes()


@app.get("/api/recipes/{recipe_id}")
async def get_recipe_endpoint(recipe_id: int):
    recipe = get_recipe(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@app.delete("/api/recipes/{recipe_id}")
async def delete_recipe_endpoint(recipe_id: int):
    delete_recipe(recipe_id)
    return {"ok": True}


# Serve the built frontend in production
_frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if _frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(_frontend_dist), html=True), name="static")

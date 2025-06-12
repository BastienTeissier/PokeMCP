from fastapi import FastAPI

from domains.pokemon import fetch_pokemon_data

app = FastAPI()


@app.get("/pokemon/{pokemon_name}")
async def read_pokemon(pokemon_name: str):
    return await fetch_pokemon_data(pokemon_name)

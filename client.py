from fastmcp import Client
from google import genai
import asyncio

config = {
    "mcpServers": {
        "pokemcp": {
            "url": "http://localhost:9999/sse",
            "transport": "sse"
        },
    }
}

client = Client(config)
gemini_client = genai.Client()

async def main():
    async with client:
        response = await gemini_client.aio.models.generate_content(
            model="gemini-2.0-flash",
            contents="Give me more information about the Pokémon Charizard",
            config=genai.types.GenerateContentConfig(
                temperature=0,
                tools=[client.session],
            ),
        )
        print(response.text)

if __name__ == "__main__":
    asyncio.run(main())
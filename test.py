import asyncio
import asyncpg

async def main():
    conn = await asyncpg.connect(
        user="postgres",
        password="prayush@7797",
        database="bookly_db",
        host="127.0.0.1",
        port=5432,
    )

    print(await conn.fetch("SELECT 'hello'"))
    await conn.close()

asyncio.run(main())
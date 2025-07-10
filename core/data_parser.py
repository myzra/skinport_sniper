from dotenv import load_dotenv
import requests
import asyncio
from listing_logger import write_to_file, get_params
from filter_engine import filter_item

import sys
import os

from pathlib import Path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
from bot.discord_bot import send_to_discord, bot

load_dotenv()

API_URL = os.getenv('API_URL')
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

def resize_list(ls: list) -> list:
    return ls[-100:]

async def monitor_sales():
    known_sales = []

    query_params = get_params()

    while True:    
        try:   
            response = requests.get(API_URL)
            if response.ok:
                print("looking for filterd offers")
                sales = response.json()

                for sale in sales:
                    sId = sale['sale']['saleId']
                    if sId not in known_sales:
                        known_sales.append(sId)
                        s = sale['sale']  
                        listing_text = f"{s['marketName']} - {s['wear']:.4f} - {s['salePrice'] / 100:.2f} EUR ({s['saleId']})"

                        if filter_item(sale=sale, query_params=query_params):
                            await send_to_discord(format_price(sale['sale']))
                            print(f"[MATCH] {listing_text}")
                            write_to_file(f"[MATCH] {listing_text}")
                        else:
                            print(f"[NEW] {listing_text}")
            else:
                print("Error while parsing the websocket data:", response.status_code)

        except Exception as e:
            print("Error:", e)

        known_sales[:] = resize_list(known_sales)

        await asyncio.sleep(5)


def format_price(sale):
    price = sale.get('salePrice')
    if isinstance(price, int):
        formatted_price = price / 100
        sale['salePrice'] = formatted_price
    return sale


async def main():
    await asyncio.gather(
        bot.start(TOKEN),
        monitor_sales()
    )


if __name__ == "__main__":
    asyncio.run(main())
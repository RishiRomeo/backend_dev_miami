import aiohttp
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def calculate_coinbase_buy_cost(orders, quantity):
    total_cost = 0
    remaining = quantity
    
    for price_str, size_str, num_orders in orders:
        if remaining <= 0:
            break
            
        price = float(price_str)
        available = float(size_str) * num_orders
        
        trade_amount = min(available, remaining)
        cost_at_level = trade_amount * price
        total_cost += cost_at_level
        remaining -= trade_amount
        

    
    return total_cost, quantity - remaining

def calculate_coinbase_sell_revenue(orders, quantity):
    total_revenue = 0
    remaining = quantity
    
    for price_str, size_str, num_orders in orders:
        if remaining <= 0:
            break
            
        price = float(price_str)
        available = float(size_str) * num_orders
        
        trade_amount = min(available, remaining)
        revenue_at_level = trade_amount * price
        total_revenue += revenue_at_level
        remaining -= trade_amount
        

    
    return total_revenue, quantity - remaining

def calculate_gemini_buy_cost(orders, quantity):
    total_cost = 0
    remaining = quantity
    
    for order in orders:
        if remaining <= 0:
            break
            
        price = float(order['price'])
        available = float(order['amount'])
        
        trade_amount = min(available, remaining)
        cost_at_level = trade_amount * price
        total_cost += cost_at_level
        remaining -= trade_amount
        

    
    return total_cost, quantity - remaining

def calculate_gemini_sell_revenue(orders, quantity):
    total_revenue = 0
    remaining = quantity
    
    for order in orders:
        if remaining <= 0:
            break
            
        price = float(order['price'])
        available = float(order['amount'])
        
        trade_amount = min(available, remaining)
        revenue_at_level = trade_amount * price
        total_revenue += revenue_at_level
        remaining -= trade_amount
        

    
    return total_revenue, quantity - remaining

async def fetch_orderbooks(session):
    coinbase_task = session.get("https://api.exchange.coinbase.com/products/BTC-USD/book?level=2")
    gemini_task = session.get("https://api.gemini.com/v1/book/BTCUSD")
    
    coinbase_response, gemini_response = await asyncio.gather(coinbase_task, gemini_task)
    
    coinbase = await coinbase_response.json()
    gemini = await gemini_response.json()
    
    return coinbase, gemini

async def analyze_prices():
    quantity = 10.0
    
    async with aiohttp.ClientSession() as session:
        logger.info("Fetching orderbooks from both exchanges...")
        coinbase, gemini = await fetch_orderbooks(session)
    
    print(f"\n{'='*50}")
    print(f"Analysis at {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*50}")
    
    print(f"\n=== BUYING {quantity} BTC (buying from asks) ===")
    
    cb_buy_cost, cb_buy_filled = calculate_coinbase_buy_cost(coinbase['asks'], quantity)
    gem_buy_cost, gem_buy_filled = calculate_gemini_buy_cost(gemini['asks'], quantity)

    cb_buy_avg = cb_buy_cost / cb_buy_filled if cb_buy_filled > 0 else 0
    gem_buy_avg = gem_buy_cost / gem_buy_filled if gem_buy_filled > 0 else 0

    logger.info(f"It would cost ${cb_buy_cost:,.2f} to buy 10 bitcoin on Coinbase (avg price: ${cb_buy_avg:,.2f}/BTC)")
    logger.info(f"It would cost ${gem_buy_cost:,.2f} to buy 10 bitcoin on Gemini (avg price: ${gem_buy_avg:,.2f}/BTC)")


    print(f"\n=== SELLING {quantity} BTC (selling from bids) ===")

    cb_sell_revenue, cb_sell_filled = calculate_coinbase_sell_revenue(coinbase['bids'], quantity)
    gem_sell_revenue, gem_sell_filled = calculate_gemini_sell_revenue(gemini['bids'], quantity)

    cb_sell_avg = cb_sell_revenue / cb_sell_filled if cb_sell_filled > 0 else 0
    gem_sell_avg = gem_sell_revenue / gem_sell_filled if gem_sell_filled > 0 else 0

    logger.info(f"It would net ${cb_sell_revenue:,.2f} selling 10 bitcoin on Coinbase (avg price: ${cb_sell_avg:,.2f}/BTC)")
    logger.info(f"It would net ${gem_sell_revenue:,.2f} selling 10 bitcoin on Gemini (avg price: ${gem_sell_avg:,.2f}/BTC)")

    print(f"\n=== SUMMARY ===")
    if cb_buy_cost < gem_buy_cost:
        print(f"Best place to BUY: Coinbase (${cb_buy_cost - gem_buy_cost:,.2f} cheaper)")
    else:
        print(f"Best place to BUY: Gemini (${gem_buy_cost - cb_buy_cost:,.2f} cheaper)")
        
    if cb_sell_revenue > gem_sell_revenue:
        print(f"Best place to SELL: Coinbase (${cb_sell_revenue - gem_sell_revenue:,.2f} more)")
    else:
        print(f"Best place to SELL: Gemini (${gem_sell_revenue - cb_sell_revenue:,.2f} more)")

async def main():
    logger.info("Starting Bitcoin price analyzer - checking every 10 seconds...")

    try:
        while True:
            await analyze_prices()
            print(f"\nWaiting 10 seconds for next update...")
            await asyncio.sleep(10)
    
    except KeyboardInterrupt:
        print("\n\nStopping price analyzer. Goodbye!")
    except Exception as e:
        logger.error(f"Error in main loop: {e}")

def run():
    asyncio.run(main())

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    run()
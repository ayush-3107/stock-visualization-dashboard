import yfinance as yf
import pandas as pd
import requests
import json
import time

def get_stock_data(ticker, period="1mo"):
    """Fetch stock data with better error handling"""
    try:
        # Add a small delay to avoid rate limiting
        time.sleep(0.5)
        
        stock = yf.Ticker(ticker)
        data = stock.history(period=period)
        
        if data.empty:
            print(f"No data found for {ticker}")
            return None
            
        return data
    except Exception as e:
        print(f"Error fetching data for {ticker}: {str(e)}")
        # Try alternative approach
        try:
            stock = yf.download(ticker, period=period, progress=False)
            return stock
        except:
            return None

def get_stock_info(ticker):
    """Get basic stock information with better error handling"""
    try:
        time.sleep(0.5)  # Rate limiting
        
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Check if info is valid
        if not info or 'currentPrice' not in info:
            # Fallback to history data for price
            hist = stock.history(period="1d")
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                previous_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            else:
                current_price = 0
                previous_close = 0
        else:
            current_price = info.get('currentPrice', 0)
            previous_close = info.get('previousClose', 0)
        
        currency_symbol = get_currency_symbol(ticker)
        
        return {
            'name': info.get('longName', info.get('shortName', ticker)),
            'current_price': current_price,
            'previous_close': previous_close,
            'market_cap': info.get('marketCap', 0),
            'currency_symbol': currency_symbol
        }
    except Exception as e:
        print(f"Error fetching info for {ticker}: {str(e)}")
        return None

def yahoo_search_stocks(query):
    """Search using Yahoo Finance autocomplete with better error handling"""
    if len(query) < 2:
        return []
    
    try:
        time.sleep(0.3)  # Rate limiting
        
        url = f"https://query1.finance.yahoo.com/v1/finance/search?q={query}&lang=en-US&region=US&quotesCount=10&newsCount=0"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            suggestions = []
            
            for quote in data.get('quotes', []):
                suggestions.append({
                    'symbol': quote.get('symbol', ''),
                    'name': quote.get('longname', quote.get('shortname', '')),
                    'exchange': quote.get('exchange', '')
                })
            return suggestions
        return []
    except Exception as e:
        print(f"Search error: {str(e)}")
        return []

def get_currency_symbol(ticker):
    """Determine currency symbol based on stock ticker"""
    if ticker.endswith('.NS') or ticker.endswith('.BO'):
        return '₹'  # Indian Rupee symbol
    elif ticker.endswith('.L'):
        return '£'  # British Pound
    elif ticker.endswith('.TO'):
        return 'C$'  # Canadian Dollar
    elif ticker.endswith('.HK'):
        return 'HK$'  # Hong Kong Dollar
    else:
        return '$'  # Default to US Dollar

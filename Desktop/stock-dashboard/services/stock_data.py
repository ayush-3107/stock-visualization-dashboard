import yfinance as yf
import pandas as pd
import requests
import json

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

def get_stock_data(ticker, period="1mo"):
    """Fetch stock data"""
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period)
        return data
    except Exception as e:
        print(f"Error fetching data for {ticker}: {str(e)}")
        return None

def get_stock_info(ticker):
    """Get basic stock information with correct currency"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        currency_symbol = get_currency_symbol(ticker)
        
        return {
            'name': info.get('longName', ticker),
            'current_price': info.get('currentPrice', 0),
            'previous_close': info.get('previousClose', 0),
            'market_cap': info.get('marketCap', 0),
            'currency_symbol': currency_symbol
        }
    except Exception as e:
        print(f"Error fetching info for {ticker}: {str(e)}")
        return None

def yahoo_search_stocks(query):
    """Search using Yahoo Finance autocomplete"""
    if len(query) < 2:
        return []
    
    try:
        url = f"https://query1.finance.yahoo.com/v1/finance/search?q={query}&lang=en-US&region=US&quotesCount=10&newsCount=0"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers)
        
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

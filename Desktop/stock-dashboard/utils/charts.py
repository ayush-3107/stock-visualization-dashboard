import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

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

def create_line_chart(data, ticker):
    """Create a simple line chart for stock prices with correct currency"""
    currency_symbol = get_currency_symbol(ticker)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Close'],
        mode='lines',
        name=f'{ticker} Close Price',
        line=dict(color='blue', width=2)
    ))
    
    fig.update_layout(
        title=f'{ticker} Stock Price',
        xaxis_title='Date',
        yaxis_title=f'Price ({currency_symbol})',
        hovermode='x unified',
        height=500
    )
    return fig

def create_candlestick_chart(data, ticker):
    """Create candlestick chart with correct currency"""
    currency_symbol = get_currency_symbol(ticker)
    
    fig = go.Figure(data=go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name=ticker
    ))
    
    fig.update_layout(
        title=f'{ticker} Candlestick Chart',
        xaxis_title='Date',
        yaxis_title=f'Price ({currency_symbol})',
        xaxis_rangeslider_visible=False,
        height=500
    )
    return fig

def add_moving_averages(fig, data, ticker):
    """Add moving averages to the chart"""
    # Calculate moving averages
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['MA50'] = data['Close'].rolling(window=50).mean()
    
    # Add MA20
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['MA20'],
        mode='lines',
        name='MA20',
        line=dict(color='orange', width=1)
    ))
    
    # Add MA50
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['MA50'],
        mode='lines',
        name='MA50',
        line=dict(color='red', width=1)
    ))
    
    return fig

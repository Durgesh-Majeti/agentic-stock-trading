# Upstox API Complete Guide

## 📋 Table of Contents

1. [Overview](#overview)
2. [API Key Generation](#api-key-generation)
3. [Authentication Flow](#authentication-flow)
4. [Access Token Management](#access-token-management)
5. [API Functions](#api-functions)
6. [WebSocket Market Data](#websocket-market-data)
7. [Rate Limits](#rate-limits)
8. [Python Implementation Examples](#python-implementation-examples)
9. [Best Practices](#best-practices)
10. [Error Handling](#error-handling)

---

## Overview

Upstox provides a RESTful API (v3) and WebSocket streaming for:
- **Market Data**: Real-time quotes, historical candles, OHLC data
- **Order Management**: Place, modify, cancel orders
- **Portfolio**: Holdings, positions, margins
- **User Profile**: Account information, fund details

**Base URL**: `https://api.upstox.com/v2/` (v2 for auth) and `https://api.upstox.com/v3/` (v3 for data/orders)

**Authentication**: OAuth 2.0 with access tokens

**SDK**: `upstox-python-sdk` (official Python SDK)

---

## API Key Generation

### Step 1: Register Developer Account

1. Visit [Upstox Developer Portal](https://developer.upstox.com/)
2. Sign up/Login with your Upstox account
3. Navigate to "My Apps" section

### Step 2: Create New Application

1. Click "Create New App"
2. Fill in application details:
   - **App Name**: Your application name
   - **Redirect URI**: `http://localhost:8080/callback` (or your callback URL)
   - **Description**: Brief description of your app
3. Submit the form

### Step 3: Get API Credentials

After app creation, you'll receive:
- **API Key** (Client ID): `YOUR_API_KEY`
- **API Secret** (Client Secret): `YOUR_API_SECRET`
- **Redirect URI**: Must match exactly with registered URI

**⚠️ Important**: 
- Keep API Secret secure (never expose in client-side code)
- Redirect URI must match exactly (including protocol, port, path)
- API Key is public, but API Secret is private

### Example Credentials Structure

```python
UPSTOX_API_KEY = "your_api_key_here"
UPSTOX_API_SECRET = "your_api_secret_here"
UPSTOX_REDIRECT_URI = "http://localhost:8080/callback"
```

---

## Authentication Flow

Upstox uses **OAuth 2.0 Authorization Code Flow**:

```
┌─────────┐         ┌──────────┐         ┌─────────┐
│  App    │────────▶│  Upstox  │────────▶│  User   │
│         │◀────────│  Server  │◀────────│         │
└─────────┘         └──────────┘         └─────────┘
     │                    │                    │
     │  1. Redirect       │  2. Login          │
     │     to login       │  3. Authorize       │
     │                    │                    │
     │  4. Get auth code  │                    │
     │◀───────────────────│                    │
     │                    │                    │
     │  5. Exchange code  │                    │
     │     for token      │                    │
     │───────────────────▶│                    │
     │                    │                    │
     │  6. Access token   │                    │
     │◀───────────────────│                    │
```

### Step-by-Step Authentication

#### Step 1: Generate Login URL

```python
import urllib.parse

def get_login_url(api_key: str, redirect_uri: str) -> str:
    """Generate Upstox login URL for user authentication."""
    base_url = "https://api.upstox.com/v2/login/authorization/dialog"
    
    params = {
        "response_type": "code",
        "client_id": api_key,
        "redirect_uri": redirect_uri,
        "state": "state123",  # Optional: for CSRF protection
        "scope": "read"  # or "read write" for trading
    }
    
    query_string = urllib.parse.urlencode(params)
    login_url = f"{base_url}?{query_string}"
    
    return login_url

# Example usage
api_key = "YOUR_API_KEY"
redirect_uri = "http://localhost:8080/callback"
login_url = get_login_url(api_key, redirect_uri)
print(f"Visit this URL: {login_url}")
```

**User Action**: User visits the URL and logs in with Upstox credentials.

#### Step 2: Handle Authorization Code

After user login, Upstox redirects to your `redirect_uri` with authorization code:

```
http://localhost:8080/callback?code=AUTHORIZATION_CODE&state=state123
```

**Extract the code**:

```python
from urllib.parse import urlparse, parse_qs

def extract_auth_code(redirect_url: str) -> str:
    """Extract authorization code from redirect URL."""
    parsed = urlparse(redirect_url)
    query_params = parse_qs(parsed.query)
    auth_code = query_params.get('code', [None])[0]
    return auth_code

# Example
redirect_url = "http://localhost:8080/callback?code=abc123xyz&state=state123"
auth_code = extract_auth_code(redirect_url)
print(f"Authorization Code: {auth_code}")
```

#### Step 3: Exchange Code for Access Token

```python
import requests

def get_access_token(
    auth_code: str,
    api_key: str,
    api_secret: str,
    redirect_uri: str
) -> dict:
    """Exchange authorization code for access token."""
    
    url = "https://api.upstox.com/v2/login/authorization/token"
    
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "code": auth_code,
        "client_id": api_key,
        "client_secret": api_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }
    
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    
    token_data = response.json()
    return token_data

# Example usage
token_response = get_access_token(
    auth_code="AUTHORIZATION_CODE",
    api_key="YOUR_API_KEY",
    api_secret="YOUR_API_SECRET",
    redirect_uri="http://localhost:8080/callback"
)

print(token_response)
# Response:
# {
#     "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#     "token_type": "Bearer",
#     "expires_in": 86400,
#     "refresh_token": null,
#     "user_id": "user123",
#     "extended_token": "extended_token_here"  # Optional, for long-term access
# }
```

**Response Fields**:
- `access_token`: Use this for API requests (valid until 3:30 AM next day)
- `token_type`: Always "Bearer"
- `expires_in`: Seconds until expiration
- `user_id`: Your Upstox user ID
- `extended_token`: For long-term read-only access (1 year validity)

---

## Access Token Management

### Token Validity

- **Standard Access Token**: Valid until **3:30 AM** the following day (regardless of generation time)
- **Extended Token**: Valid for **1 year** (read-only access, requires special approval)

### Token Refresh Strategy

**⚠️ Important**: Upstox does NOT support refresh tokens. You must:
1. Re-authenticate daily (before 3:30 AM)
2. Or use extended token for read-only operations

### Automated Token Generation

For production, implement semi-automated token generation:

```python
import requests
from datetime import datetime, time
import schedule
import time as time_module

class UpstoxTokenManager:
    """Manages Upstox access token lifecycle."""
    
    def __init__(self, api_key: str, api_secret: str, redirect_uri: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.redirect_uri = redirect_uri
        self.access_token = None
        self.token_expiry = None
        self.extended_token = None
    
    def is_token_valid(self) -> bool:
        """Check if current token is still valid."""
        if not self.access_token or not self.token_expiry:
            return False
        
        # Token expires at 3:30 AM next day
        now = datetime.now()
        expiry = self.token_expiry
        
        return now < expiry
    
    def get_new_token(self, auth_code: str) -> dict:
        """Get new access token using authorization code."""
        url = "https://api.upstox.com/v2/login/authorization/token"
        
        data = {
            "code": auth_code,
            "client_id": self.api_key,
            "client_secret": self.api_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code"
        }
        
        response = requests.post(url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        
        # Store token
        self.access_token = token_data["access_token"]
        
        # Calculate expiry (3:30 AM next day)
        now = datetime.now()
        tomorrow = now.replace(hour=3, minute=30, second=0, microsecond=0)
        if tomorrow <= now:
            tomorrow = tomorrow.replace(day=tomorrow.day + 1)
        self.token_expiry = tomorrow
        
        if "extended_token" in token_data:
            self.extended_token = token_data["extended_token"]
        
        return token_data
    
    def get_valid_token(self) -> str:
        """Get valid access token, refresh if needed."""
        if not self.is_token_valid():
            raise ValueError("Token expired. Re-authenticate required.")
        return self.access_token

# Usage
token_manager = UpstoxTokenManager(
    api_key="YOUR_API_KEY",
    api_secret="YOUR_API_SECRET",
    redirect_uri="http://localhost:8080/callback"
)
```

### Extended Token (Long-term Access)

For read-only operations that need long-term access:

1. **Request Extended Token**: Contact Upstox support for multi-client application enrollment
2. **Use Extended Token**: Valid for 1 year, read-only access
3. **Use Cases**: 
   - Historical data backfill
   - Portfolio monitoring
   - Analytics dashboards

```python
# Use extended token for read-only operations
extended_token = token_response.get("extended_token")
if extended_token:
    # Use for read-only API calls
    headers = {"Authorization": f"Bearer {extended_token}"}
```

---

## API Functions

### Base Configuration

```python
import upstox_client
from upstox_client.rest import ApiException

# Configure access token
configuration = upstox_client.Configuration()
configuration.access_token = "YOUR_ACCESS_TOKEN"

# Create API client
api_client = upstox_client.ApiClient(configuration)
```

### 1. Market Data APIs

#### Get Full Market Quote

```python
from upstox_client import MarketQuoteApi

def get_market_quote(instrument_keys: list, access_token: str):
    """Get full market quote for instruments."""
    
    configuration = upstox_client.Configuration()
    configuration.access_token = access_token
    
    api_instance = MarketQuoteApi(upstox_client.ApiClient(configuration))
    
    try:
        # instrument_keys format: ["NSE_EQ|INE467B01029", "NSE_INDEX|Nifty 50"]
        response = api_instance.get_full_market_quote(
            instrument_keys=instrument_keys
        )
        return response
    except ApiException as e:
        print(f"Exception: {e}")
        return None

# Example
instrument_keys = [
    "NSE_EQ|INE467B01029",  # RELIANCE
    "NSE_INDEX|Nifty 50"
]
quotes = get_market_quote(instrument_keys, access_token)
```

#### Get OHLC Data

```python
from upstox_client import MarketQuoteApi

def get_ohlc(
    instrument_key: str,
    interval: str,
    to_date: str,
    from_date: str,
    access_token: str
):
    """Get OHLC candle data.
    
    Args:
        instrument_key: e.g., "NSE_EQ|INE467B01029"
        interval: "1minute", "5minute", "30minute", "day"
        to_date: "2024-01-15"
        from_date: "2024-01-01"
    """
    
    configuration = upstox_client.Configuration()
    configuration.access_token = access_token
    
    api_instance = MarketQuoteApi(upstox_client.ApiClient(configuration))
    
    try:
        response = api_instance.get_market_quote_ohlc(
            instrument_key=instrument_key,
            interval=interval,
            to_date=to_date,
            from_date=from_date
        )
        return response
    except ApiException as e:
        print(f"Exception: {e}")
        return None

# Example
ohlc_data = get_ohlc(
    instrument_key="NSE_EQ|INE467B01029",
    interval="day",
    from_date="2024-01-01",
    to_date="2024-01-15",
    access_token=access_token
)
```

#### Get Historical Candles

```python
from upstox_client import HistoryApi

def get_historical_candles(
    instrument_key: str,
    interval: str,
    to_date: str,
    from_date: str,
    access_token: str
):
    """Get historical candle data."""
    
    configuration = upstox_client.Configuration()
    configuration.access_token = access_token
    
    api_instance = HistoryApi(upstox_client.ApiClient(configuration))
    
    try:
        response = api_instance.get_historical_candle_data(
            instrument_key=instrument_key,
            interval=interval,
            to_date=to_date,
            from_date=from_date
        )
        return response
    except ApiException as e:
        print(f"Exception: {e}")
        return None
```

### 2. Order Management APIs

#### Place Order

```python
from upstox_client import OrderApi
from upstox_client.models import PlaceOrderRequest

def place_order(
    instrument_token: str,
    quantity: int,
    order_type: str,  # "MARKET" or "LIMIT"
    transaction_type: str,  # "BUY" or "SELL"
    product: str,  # "D" (Delivery), "I" (Intraday), "CO" (Cover Order)
    price: float = 0,  # Required for LIMIT orders
    validity: str = "DAY",  # "DAY", "IOC", "TILL_CANCEL"
    access_token: str = None
):
    """Place a trading order."""
    
    configuration = upstox_client.Configuration()
    configuration.access_token = access_token
    
    api_instance = OrderApi(upstox_client.ApiClient(configuration))
    
    order = PlaceOrderRequest(
        quantity=quantity,
        product=product,
        validity=validity,
        price=price,
        tag="string",  # Optional tag
        instrument_token=instrument_token,
        order_type=order_type,
        transaction_type=transaction_type,
        disclosed_quantity=0,
        trigger_price=0,
        is_amo=False  # After Market Order
    )
    
    try:
        response = api_instance.place_order(order)
        return response
    except ApiException as e:
        print(f"Exception: {e}")
        return None

# Example: Market Buy Order
order_response = place_order(
    instrument_token="NSE_EQ|INE467B01029",
    quantity=1,
    order_type="MARKET",
    transaction_type="BUY",
    product="D",  # Delivery
    access_token=access_token
)

# Example: Limit Sell Order
order_response = place_order(
    instrument_token="NSE_EQ|INE467B01029",
    quantity=1,
    order_type="LIMIT",
    transaction_type="SELL",
    product="D",
    price=2500.0,  # Limit price
    access_token=access_token
)
```

#### Modify Order

```python
from upstox_client import OrderApi
from upstox_client.models import ModifyOrderRequest

def modify_order(
    order_id: str,
    quantity: int = None,
    price: float = None,
    order_type: str = None,
    validity: str = None,
    access_token: str = None
):
    """Modify an existing order."""
    
    configuration = upstox_client.Configuration()
    configuration.access_token = access_token
    
    api_instance = OrderApi(upstox_client.ApiClient(configuration))
    
    modify_request = ModifyOrderRequest(
        order_id=order_id,
        quantity=quantity,
        price=price,
        order_type=order_type,
        validity=validity
    )
    
    try:
        response = api_instance.modify_order(modify_request)
        return response
    except ApiException as e:
        print(f"Exception: {e}")
        return None
```

#### Cancel Order

```python
from upstox_client import OrderApi

def cancel_order(order_id: str, access_token: str):
    """Cancel an order."""
    
    configuration = upstox_client.Configuration()
    configuration.access_token = access_token
    
    api_instance = OrderApi(upstox_client.ApiClient(configuration))
    
    try:
        response = api_instance.cancel_order(order_id=order_id)
        return response
    except ApiException as e:
        print(f"Exception: {e}")
        return None
```

#### Get Order Book

```python
from upstox_client import OrderApi

def get_order_book(access_token: str):
    """Get all orders."""
    
    configuration = upstox_client.Configuration()
    configuration.access_token = access_token
    
    api_instance = OrderApi(upstox_client.ApiClient(configuration))
    
    try:
        response = api_instance.get_order_book()
        return response
    except ApiException as e:
        print(f"Exception: {e}")
        return None
```

### 3. Portfolio APIs

#### Get Holdings

```python
from upstox_client import PortfolioApi

def get_holdings(access_token: str):
    """Get user holdings."""
    
    configuration = upstox_client.Configuration()
    configuration.access_token = access_token
    
    api_instance = PortfolioApi(upstox_client.ApiClient(configuration))
    
    try:
        response = api_instance.get_holdings()
        return response
    except ApiException as e:
        print(f"Exception: {e}")
        return None
```

#### Get Positions

```python
from upstox_client import PortfolioApi

def get_positions(access_token: str):
    """Get user positions."""
    
    configuration = upstox_client.Configuration()
    configuration.access_token = access_token
    
    api_instance = PortfolioApi(upstox_client.ApiClient(configuration))
    
    try:
        response = api_instance.get_positions()
        return response
    except ApiException as e:
        print(f"Exception: {e}")
        return None
```

#### Get Margins

```python
from upstox_client import PortfolioApi

def get_margins(access_token: str):
    """Get available margins."""
    
    configuration = upstox_client.Configuration()
    configuration.access_token = access_token
    
    api_instance = PortfolioApi(upstox_client.ApiClient(configuration))
    
    try:
        response = api_instance.get_margins()
        return response
    except ApiException as e:
        print(f"Exception: {e}")
        return None
```

### 4. User Profile APIs

#### Get User Profile

```python
from upstox_client import UserApi

def get_user_profile(access_token: str):
    """Get user profile information."""
    
    configuration = upstox_client.Configuration()
    configuration.access_token = access_token
    
    api_instance = UserApi(upstox_client.ApiClient(configuration))
    
    try:
        response = api_instance.get_profile()
        return response
    except ApiException as e:
        print(f"Exception: {e}")
        return None
```

#### Get Fund Details

```python
from upstox_client import UserApi

def get_funds(access_token: str):
    """Get fund details."""
    
    configuration = upstox_client.Configuration()
    configuration.access_token = access_token
    
    api_instance = UserApi(upstox_client.ApiClient(configuration))
    
    try:
        response = api_instance.get_fund_margin()
        return response
    except ApiException as e:
        print(f"Exception: {e}")
        return None
```

### 5. Instrument Master

#### Get Instrument Master

```python
from upstox_client import MarketQuoteApi

def get_instrument_master(exchange: str, access_token: str):
    """Get instrument master data.
    
    Args:
        exchange: "NSE_EQ", "NSE_FO", "BSE_EQ", etc.
    """
    
    configuration = upstox_client.Configuration()
    configuration.access_token = access_token
    
    api_instance = MarketQuoteApi(upstox_client.ApiClient(configuration))
    
    try:
        response = api_instance.get_master(exchange=exchange)
        return response
    except ApiException as e:
        print(f"Exception: {e}")
        return None

# Example: Get NSE Equity instruments
instruments = get_instrument_master("NSE_EQ", access_token)
```

---

## WebSocket Market Data

Upstox provides WebSocket streaming for real-time market data.

### Installation

```bash
pip install upstox-python-sdk
```

### WebSocket Connection

```python
import upstox_client
from upstox_client import MarketDataStreamerV3

def setup_websocket(access_token: str, instrument_keys: list):
    """Setup WebSocket for real-time market data."""
    
    configuration = upstox_client.Configuration()
    configuration.access_token = access_token
    
    # Initialize streamer
    streamer = MarketDataStreamerV3(
        upstox_client.ApiClient(configuration),
        instrument_keys,
        "full"  # Mode: "full" or "ltp"
    )
    
    # Message handler
    def on_message(message):
        print(f"Received: {message}")
        # Process market data here
    
    # Error handler
    def on_error(error):
        print(f"WebSocket Error: {error}")
    
    # Connect handler
    def on_connect():
        print("WebSocket Connected")
    
    # Disconnect handler
    def on_disconnect():
        print("WebSocket Disconnected")
    
    # Set handlers
    streamer.on("message", on_message)
    streamer.on("error", on_error)
    streamer.on("connect", on_connect)
    streamer.on("disconnect", on_disconnect)
    
    # Connect
    streamer.connect()
    
    return streamer

# Example usage
instrument_keys = [
    "NSE_INDEX|Nifty 50",
    "NSE_INDEX|Nifty Bank",
    "NSE_EQ|INE467B01029"  # RELIANCE
]

streamer = setup_websocket(access_token, instrument_keys)

# Keep connection alive
import time
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    streamer.disconnect()
```

### WebSocket Modes

- **"full"**: Complete market data (LTP, volume, bid/ask, etc.)
- **"ltp"**: Last Traded Price only (lighter)

### Subscription Limits

- **Standard**: 1 WebSocket connection, up to 50 instruments
- **Upstox Plus**: 5 WebSocket connections, up to 50 instruments per connection

---

## Rate Limits

Upstox enforces rate limits to ensure service reliability:

### API Rate Limits

- **Orders**: 
  - 10 requests per second
  - 100 requests per minute
  - 1000 requests per 30 minutes

- **Market Data**:
  - 20 requests per second
  - 200 requests per minute

### WebSocket Limits

- **Standard**: 1 connection, 50 instruments
- **Plus Plan**: 5 connections, 50 instruments each

### Best Practices

1. **Implement Rate Limiting**: Use token bucket or sliding window
2. **Cache Responses**: Cache market data for short periods
3. **Batch Requests**: Combine multiple instruments in single request
4. **Use WebSocket**: For real-time data instead of polling

```python
from time import sleep
from collections import deque
from datetime import datetime, timedelta

class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, max_calls: int, period_seconds: int):
        self.max_calls = max_calls
        self.period_seconds = period_seconds
        self.calls = deque()
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        now = datetime.now()
        
        # Remove old calls outside the period
        while self.calls and (now - self.calls[0]).total_seconds() > self.period_seconds:
            self.calls.popleft()
        
        # If at limit, wait
        if len(self.calls) >= self.max_calls:
            sleep_time = self.period_seconds - (now - self.calls[0]).total_seconds()
            if sleep_time > 0:
                sleep(sleep_time)
                self.calls.popleft()
        
        # Record this call
        self.calls.append(now)

# Usage
rate_limiter = RateLimiter(max_calls=20, period_seconds=1)  # 20 calls per second

for i in range(100):
    rate_limiter.wait_if_needed()
    # Make API call
    response = make_api_call()
```

---

## Python Implementation Examples

### Complete Example: Upstox Client Class

```python
import upstox_client
from upstox_client.rest import ApiException
from typing import List, Dict, Optional
from datetime import datetime
import requests

class UpstoxClient:
    """Complete Upstox API client wrapper."""
    
    def __init__(self, access_token: str):
        """Initialize Upstox client with access token."""
        self.configuration = upstox_client.Configuration()
        self.configuration.access_token = access_token
        self.api_client = upstox_client.ApiClient(self.configuration)
        
        # Initialize API instances
        self.market_api = upstox_client.MarketQuoteApi(self.api_client)
        self.order_api = upstox_client.OrderApi(self.api_client)
        self.portfolio_api = upstox_client.PortfolioApi(self.api_client)
        self.user_api = upstox_client.UserApi(self.api_client)
        self.history_api = upstox_client.HistoryApi(self.api_client)
    
    # Market Data Methods
    def get_quote(self, instrument_keys: List[str]) -> Optional[Dict]:
        """Get full market quote."""
        try:
            return self.market_api.get_full_market_quote(instrument_keys=instrument_keys)
        except ApiException as e:
            print(f"Error getting quote: {e}")
            return None
    
    def get_ohlc(
        self,
        instrument_key: str,
        interval: str,
        from_date: str,
        to_date: str
    ) -> Optional[Dict]:
        """Get OHLC data."""
        try:
            return self.market_api.get_market_quote_ohlc(
                instrument_key=instrument_key,
                interval=interval,
                from_date=from_date,
                to_date=to_date
            )
        except ApiException as e:
            print(f"Error getting OHLC: {e}")
            return None
    
    def get_historical_candles(
        self,
        instrument_key: str,
        interval: str,
        from_date: str,
        to_date: str
    ) -> Optional[Dict]:
        """Get historical candles."""
        try:
            return self.history_api.get_historical_candle_data(
                instrument_key=instrument_key,
                interval=interval,
                from_date=from_date,
                to_date=to_date
            )
        except ApiException as e:
            print(f"Error getting historical data: {e}")
            return None
    
    # Order Methods
    def place_order(
        self,
        instrument_token: str,
        quantity: int,
        order_type: str,
        transaction_type: str,
        product: str = "D",
        price: float = 0,
        validity: str = "DAY"
    ) -> Optional[Dict]:
        """Place an order."""
        try:
            order = upstox_client.PlaceOrderRequest(
                quantity=quantity,
                product=product,
                validity=validity,
                price=price,
                tag="",
                instrument_token=instrument_token,
                order_type=order_type,
                transaction_type=transaction_type,
                disclosed_quantity=0,
                trigger_price=0,
                is_amo=False
            )
            return self.order_api.place_order(order)
        except ApiException as e:
            print(f"Error placing order: {e}")
            return None
    
    def cancel_order(self, order_id: str) -> Optional[Dict]:
        """Cancel an order."""
        try:
            return self.order_api.cancel_order(order_id=order_id)
        except ApiException as e:
            print(f"Error canceling order: {e}")
            return None
    
    def get_orders(self) -> Optional[Dict]:
        """Get order book."""
        try:
            return self.order_api.get_order_book()
        except ApiException as e:
            print(f"Error getting orders: {e}")
            return None
    
    # Portfolio Methods
    def get_holdings(self) -> Optional[Dict]:
        """Get holdings."""
        try:
            return self.portfolio_api.get_holdings()
        except ApiException as e:
            print(f"Error getting holdings: {e}")
            return None
    
    def get_positions(self) -> Optional[Dict]:
        """Get positions."""
        try:
            return self.portfolio_api.get_positions()
        except ApiException as e:
            print(f"Error getting positions: {e}")
            return None
    
    def get_margins(self) -> Optional[Dict]:
        """Get margins."""
        try:
            return self.portfolio_api.get_margins()
        except ApiException as e:
            print(f"Error getting margins: {e}")
            return None
    
    # User Methods
    def get_profile(self) -> Optional[Dict]:
        """Get user profile."""
        try:
            return self.user_api.get_profile()
        except ApiException as e:
            print(f"Error getting profile: {e}")
            return None

# Usage Example
if __name__ == "__main__":
    # Initialize client
    client = UpstoxClient(access_token="YOUR_ACCESS_TOKEN")
    
    # Get market quote
    quotes = client.get_quote(["NSE_EQ|INE467B01029"])
    print(quotes)
    
    # Get historical data
    candles = client.get_historical_candles(
        instrument_key="NSE_EQ|INE467B01029",
        interval="day",
        from_date="2024-01-01",
        to_date="2024-01-15"
    )
    print(candles)
    
    # Get holdings
    holdings = client.get_holdings()
    print(holdings)
```

---

## Best Practices

### 1. Token Management

- **Store tokens securely**: Use environment variables or secure vaults
- **Monitor expiry**: Check token validity before API calls
- **Implement retry logic**: Handle token expiry gracefully
- **Use extended tokens**: For read-only long-term operations

### 2. Error Handling

```python
from upstox_client.rest import ApiException

def safe_api_call(api_func, *args, **kwargs):
    """Wrapper for safe API calls with error handling."""
    try:
        return api_func(*args, **kwargs)
    except ApiException as e:
        if e.status == 401:
            # Token expired
            print("Token expired. Re-authenticate required.")
        elif e.status == 429:
            # Rate limit exceeded
            print("Rate limit exceeded. Wait before retrying.")
        elif e.status == 400:
            # Bad request
            print(f"Bad request: {e.body}")
        else:
            print(f"API Error: {e}")
        return None
```

### 3. Instrument Token Format

Upstox uses specific format for instrument tokens:
- **Equity**: `NSE_EQ|INE467B01029` (Exchange|ISIN)
- **Index**: `NSE_INDEX|Nifty 50`
- **Futures**: `NSE_FO|12345` (Exchange|Token)

**Getting Instrument Tokens**:
1. Use instrument master API
2. Search by symbol/ISIN
3. Store mapping in database

### 4. Data Validation

```python
def validate_order_params(
    instrument_token: str,
    quantity: int,
    order_type: str,
    transaction_type: str
) -> bool:
    """Validate order parameters before placing."""
    
    # Check quantity
    if quantity <= 0:
        print("Quantity must be positive")
        return False
    
    # Check order type
    if order_type not in ["MARKET", "LIMIT", "SL", "SL-M"]:
        print("Invalid order type")
        return False
    
    # Check transaction type
    if transaction_type not in ["BUY", "SELL"]:
        print("Invalid transaction type")
        return False
    
    # Check instrument token format
    if "|" not in instrument_token:
        print("Invalid instrument token format")
        return False
    
    return True
```

### 5. Logging and Monitoring

```python
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def log_api_call(api_name: str, params: dict, response: dict):
    """Log API calls for monitoring."""
    logger.info(f"API Call: {api_name}")
    logger.debug(f"Params: {params}")
    logger.debug(f"Response: {response}")
```

---

## Error Handling

### Common Error Codes

| Status Code | Meaning | Solution |
|------------|---------|----------|
| 400 | Bad Request | Check request parameters |
| 401 | Unauthorized | Token expired or invalid |
| 403 | Forbidden | Insufficient permissions |
| 429 | Rate Limit | Wait and retry |
| 500 | Server Error | Retry with exponential backoff |

### Error Handling Example

```python
import time
from upstox_client.rest import ApiException

def retry_api_call(api_func, max_retries=3, *args, **kwargs):
    """Retry API call with exponential backoff."""
    
    for attempt in range(max_retries):
        try:
            return api_func(*args, **kwargs)
        except ApiException as e:
            if e.status == 401:
                # Token expired, don't retry
                raise
            elif e.status == 429:
                # Rate limit, wait longer
                wait_time = (2 ** attempt) * 1  # Exponential backoff
                print(f"Rate limited. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
            elif e.status >= 500:
                # Server error, retry
                wait_time = (2 ** attempt) * 1
                print(f"Server error. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                # Client error, don't retry
                raise
        
        if attempt == max_retries - 1:
            raise Exception("Max retries exceeded")
    
    return None
```

---

## Summary

### Key Takeaways

1. **Authentication**: OAuth 2.0 flow with daily token refresh
2. **Token Management**: Tokens expire at 3:30 AM daily
3. **API Version**: Use v3 APIs (v2 deprecated)
4. **Rate Limits**: Implement rate limiting for production
5. **WebSocket**: Use for real-time data instead of polling
6. **Error Handling**: Implement retry logic and proper error handling
7. **Security**: Keep API secrets secure, never expose in client code

### Integration Checklist

- [ ] Register app and get API credentials
- [ ] Implement OAuth 2.0 flow
- [ ] Set up token management system
- [ ] Implement rate limiting
- [ ] Add error handling and retry logic
- [ ] Test with paper trading first
- [ ] Set up logging and monitoring
- [ ] Implement WebSocket for real-time data (optional)

---

## References

- [Upstox Developer Portal](https://developer.upstox.com/)
- [Upstox API Documentation](https://upstox.com/developer/api-documentation)
- [Upstox Python SDK](https://github.com/upstox/upstox-python)
- [Upstox Python SDK Docs](https://upstox.github.io/upstox-python/)

---

**Last Updated**: January 2025

**Note**: API specifications may change. Always refer to official Upstox documentation for the latest information.

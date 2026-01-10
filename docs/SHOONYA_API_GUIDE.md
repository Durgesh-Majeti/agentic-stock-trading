# Shoonya API Complete Guide

## 📋 Table of Contents

1. [Overview](#overview)
2. [API Key Generation](#api-key-generation)
3. [Authentication Flow](#authentication-flow)
4. [Session Management](#session-management)
5. [API Functions](#api-functions)
6. [WebSocket Market Data](#websocket-market-data)
7. [Rate Limits](#rate-limits)
8. [Python Implementation Examples](#python-implementation-examples)
9. [Best Practices](#best-practices)
10. [Error Handling](#error-handling)

---

## Overview

Shoonya (by Finvasia) provides a comprehensive REST API and WebSocket streaming for:
- **Market Data**: Real-time quotes, historical candles, OHLC data
- **Order Management**: Place, modify, cancel orders
- **Portfolio**: Holdings, positions, margins
- **User Profile**: Account information, fund details

**Base URL**: `https://api.shoonya.com/`

**Authentication**: Session-based with user credentials + 2FA

**SDK**: `ShoonyaApi-Py` (official Python SDK from GitHub)

**Key Advantage**: Excellent WebSocket support for 500+ stocks simultaneously

---

## API Key Generation

### Step 1: Register Shoonya Account

1. Visit [Shoonya](https://shoonya.com/)
2. Sign up for a trading account
3. Complete KYC verification

### Step 2: Generate API Key

1. Log in to **Prism Portal**: [https://prism.shoonya.com](https://prism.shoonya.com)
2. Click on **"API Key"** button (top right)
3. Generate a new API key
4. Copy and securely store:
   - **API Key** (appkey)
   - **API Secret** (if provided)

**⚠️ Important**: 
- Keep API key secure (never expose in client-side code)
- API key is tied to your account
- One API key per account

### Step 3: Set Up Two-Factor Authentication (2FA)

**Option A: TOTP (Time-Based One-Time Password) - Recommended**

1. Log in to Shoonya account
2. Navigate to **Profile → 2FA Settings**
3. Scan QR code with authenticator app (Google Authenticator, Microsoft Authenticator)
4. Save the TOTP secret securely
5. Generate TOTP codes (valid for 30 seconds)

**Option B: OTP (SMS/Email)**

1. Enable OTP in account settings
2. Receive OTP via SMS/Email during login

**For API Usage**: TOTP is preferred for automation

### Step 4: Get Vendor Code

**Vendor Code Format**: `{ClientCode}_U`

Example:
- Client Code: `FA12345`
- Vendor Code: `FA12345_U`

**Where to find**: Your client code is shown in your Shoonya account dashboard

### Step 5: Get IMEI/MAC Address

- **Desktop**: Use MAC address (e.g., `AA:BB:CC:DD:EE:FF`)
- **Mobile**: Use IMEI number
- **Virtual Machine**: Generate a unique identifier

**Note**: IMEI is used for device identification and session management

### Example Credentials Structure

```python
SHOONYA_CREDENTIALS = {
    "user_id": "FA12345",
    "password": "your_password",  # Will be SHA-256 encrypted
    "two_fa": "123456",  # TOTP from authenticator app
    "vendor_code": "FA12345_U",
    "api_secret": "your_api_key_from_prism",
    "imei": "AA:BB:CC:DD:EE:FF"  # MAC address for desktop
}
```

---

## Authentication Flow

Shoonya uses **session-based authentication** with credentials + 2FA:

```
┌─────────┐         ┌──────────┐
│  App    │────────▶│  Shoonya │
│         │◀────────│  Server  │
└─────────┘         └──────────┘
     │                    │
     │  1. Login Request  │
     │     (credentials)  │
     │                    │
     │  2. Session Token  │
     │◀───────────────────│
     │                    │
     │  3. API Requests   │
     │     (with token)   │
     │───────────────────▶│
```

### Step-by-Step Authentication

#### Step 1: Encrypt Password

Shoonya requires **SHA-256 encrypted password**:

```python
import hashlib

def encrypt_password(password: str) -> str:
    """Encrypt password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

# Example
plain_password = "my_password_123"
encrypted_password = encrypt_password(plain_password)
print(f"Encrypted: {encrypted_password}")
```

#### Step 2: Generate TOTP

If using TOTP (recommended for automation):

```python
import pyotp  # pip install pyotp

def get_totp(secret: str) -> str:
    """Generate TOTP from secret."""
    totp = pyotp.TOTP(secret)
    return totp.now()

# Example
totp_secret = "JBSWY3DPEHPK3PXP"  # From QR code
current_totp = get_totp(totp_secret)
print(f"Current TOTP: {current_totp}")
```

#### Step 3: Login

```python
from NorenRestApiPy.NorenApi import NorenApi
import pyotp

class ShoonyaApi(NorenApi):
    """Shoonya API wrapper."""
    
    def __init__(self):
        NorenApi.__init__(self)
        self.host = "https://api.shoonya.com/NorenWClientTP/"
        self.websocket = "wss://api.shoonya.com/NorenWSTP/"
    
    def login(
        self,
        user_id: str,
        password: str,
        two_fa: str,
        vendor_code: str,
        api_secret: str,
        imei: str
    ) -> dict:
        """Login to Shoonya API."""
        
        # Encrypt password
        encrypted_pwd = hashlib.sha256(password.encode()).hexdigest()
        
        # Login request
        login_response = self.login(
            userid=user_id,
            pwd=encrypted_pwd,
            factor2=two_fa,  # TOTP or OTP
            vc=vendor_code,
            apkversion="1.0.0",
            appkey=api_secret,
            imei=imei
        )
        
        return login_response

# Example usage
api = ShoonyaApi()

# Get TOTP
totp_secret = "YOUR_TOTP_SECRET"
current_totp = pyotp.TOTP(totp_secret).now()

# Login
response = api.login(
    user_id="FA12345",
    password="your_password",
    two_fa=current_totp,
    vendor_code="FA12345_U",
    api_secret="your_api_key",
    imei="AA:BB:CC:DD:EE:FF"
)

print(response)
# Response:
# {
#     "stat": "Ok",
#     "susertoken": "abc123xyz...",
#     "uname": "FA12345",
#     "actid": "FA12345",
#     "email": "user@example.com",
#     "brname": "Finvasia",
#     "exarr": ["NSE", "BSE", "NFO", "CDS", "MCX"],
#     "orarr": ["NSE", "BSE", "NFO", "CDS", "MCX"]
# }
```

**Response Fields**:
- `stat`: Status ("Ok" on success)
- `susertoken`: Session token (use for all API calls)
- `uname`: Username
- `actid`: Account ID
- `exarr`: Enabled exchanges
- `orarr`: Order-enabled exchanges

#### Step 4: Store Session Token

```python
# Store session token for subsequent requests
session_token = response["susertoken"]
api.set_session_token(session_token)

# All subsequent API calls will use this token
```

---

## Session Management

### Session Validity

- **Session Duration**: Typically valid for 24 hours
- **Auto-Expiry**: Session expires after inactivity or at end of day
- **Re-login Required**: If session expires, re-authenticate

### Session Refresh

Shoonya doesn't provide explicit refresh tokens. Handle session expiry:

```python
class ShoonyaSessionManager:
    """Manage Shoonya API sessions."""
    
    def __init__(self, credentials: dict):
        self.credentials = credentials
        self.api = ShoonyaApi()
        self.session_token = None
        self.session_expiry = None
    
    def login(self) -> bool:
        """Login and establish session."""
        try:
            # Get TOTP
            totp_secret = self.credentials.get("totp_secret")
            current_totp = pyotp.TOTP(totp_secret).now()
            
            # Encrypt password
            encrypted_pwd = hashlib.sha256(
                self.credentials["password"].encode()
            ).hexdigest()
            
            # Login
            response = self.api.login(
                userid=self.credentials["user_id"],
                pwd=encrypted_pwd,
                factor2=current_totp,
                vc=self.credentials["vendor_code"],
                apkversion="1.0.0",
                appkey=self.credentials["api_secret"],
                imei=self.credentials["imei"]
            )
            
            if response.get("stat") == "Ok":
                self.session_token = response["susertoken"]
                self.api.set_session_token(self.session_token)
                
                # Set expiry (24 hours from now)
                from datetime import datetime, timedelta
                self.session_expiry = datetime.now() + timedelta(hours=24)
                
                return True
            else:
                print(f"Login failed: {response}")
                return False
                
        except Exception as e:
            print(f"Login error: {e}")
            return False
    
    def is_session_valid(self) -> bool:
        """Check if session is still valid."""
        if not self.session_token:
            return False
        
        # Check expiry
        if self.session_expiry and datetime.now() >= self.session_expiry:
            return False
        
        # Try a lightweight API call to verify
        try:
            # Get user profile (lightweight check)
            profile = self.api.get_user_details()
            return profile.get("stat") == "Ok"
        except:
            return False
    
    def ensure_session(self) -> bool:
        """Ensure valid session, re-login if needed."""
        if not self.is_session_valid():
            print("Session expired, re-logging in...")
            return self.login()
        return True

# Usage
credentials = {
    "user_id": "FA12345",
    "password": "your_password",
    "totp_secret": "YOUR_TOTP_SECRET",
    "vendor_code": "FA12345_U",
    "api_secret": "your_api_key",
    "imei": "AA:BB:CC:DD:EE:FF"
}

session_manager = ShoonyaSessionManager(credentials)
session_manager.login()

# Before any API call
if session_manager.ensure_session():
    # Make API calls
    quotes = api.get_quotes("NSE", "RELIANCE-EQ")
```

---

## API Functions

### Base Setup

```python
from NorenRestApiPy.NorenApi import NorenApi

class ShoonyaApi(NorenApi):
    """Shoonya API wrapper."""
    
    def __init__(self):
        NorenApi.__init__(self)
        self.host = "https://api.shoonya.com/NorenWClientTP/"
        self.websocket = "wss://api.shoonya.com/NorenWSTP/"

# Initialize after login
api = ShoonyaApi()
# ... login code ...
api.set_session_token(session_token)
```

### 1. Market Data APIs

#### Get Quotes (REST)

```python
def get_quotes(exchange: str, symbol: str) -> dict:
    """Get quote for a single instrument.
    
    Args:
        exchange: "NSE", "BSE", "NFO", etc.
        symbol: Trading symbol (e.g., "RELIANCE-EQ")
    """
    try:
        quote = api.get_quotes(exchange, symbol)
        return quote
    except Exception as e:
        print(f"Error getting quote: {e}")
        return None

# Example
quote = get_quotes("NSE", "RELIANCE-EQ")
print(quote)
# Response includes: LTP, volume, bid, ask, OHLC, etc.
```

**⚠️ Note**: For multiple instruments, use WebSocket instead of multiple REST calls.

#### Get Multiple Quotes

```python
def get_multiple_quotes(instruments: list) -> dict:
    """Get quotes for multiple instruments.
    
    Args:
        instruments: List of tuples [(exchange, symbol), ...]
    """
    try:
        # Format: "NSE|RELIANCE-EQ"
        instrument_strings = [f"{ex}|{sym}" for ex, sym in instruments]
        quotes = api.get_quotes_multiple(instrument_strings)
        return quotes
    except Exception as e:
        print(f"Error getting quotes: {e}")
        return None

# Example
instruments = [
    ("NSE", "RELIANCE-EQ"),
    ("NSE", "TCS-EQ"),
    ("NSE", "INFY-EQ")
]
quotes = get_multiple_quotes(instruments)
```

#### Get Historical Data (Intraday)

```python
def get_intraday_data(
    exchange: str,
    symbol: str,
    start_time: str,
    end_time: str,
    interval: str = "1"
) -> dict:
    """Get intraday historical data.
    
    Args:
        exchange: "NSE", "BSE", etc.
        symbol: Trading symbol
        start_time: "DD-MM-YYYY HH:MM:SS"
        end_time: "DD-MM-YYYY HH:MM:SS"
        interval: "1" (1 minute), "5" (5 minutes), "15", "30", "60"
    """
    try:
        data = api.get_time_price_series(
            exchange=exchange,
            token=symbol,
            starttime=start_time,
            endtime=end_time,
            interval=interval
        )
        return data
    except Exception as e:
        print(f"Error getting intraday data: {e}")
        return None

# Example
intraday = get_intraday_data(
    exchange="NSE",
    symbol="RELIANCE-EQ",
    start_time="01-01-2024 09:15:00",
    end_time="01-01-2024 15:30:00",
    interval="5"  # 5-minute candles
)
```

#### Get Historical Data (Daily)

```python
def get_daily_data(
    exchange: str,
    symbol: str,
    start_date: str,
    end_date: str
) -> dict:
    """Get daily historical data.
    
    Args:
        exchange: "NSE", "BSE", etc.
        symbol: Trading symbol
        start_date: "DD-MM-YYYY"
        end_date: "DD-MM-YYYY"
    """
    try:
        data = api.get_daily_price_series(
            exchange=exchange,
            token=symbol,
            startdate=start_date,
            enddate=end_date
        )
        return data
    except Exception as e:
        print(f"Error getting daily data: {e}")
        return None

# Example
daily = get_daily_data(
    exchange="NSE",
    symbol="RELIANCE-EQ",
    start_date="01-01-2023",
    end_date="31-12-2023"
)
```

### 2. Order Management APIs

#### Place Order

```python
def place_order(
    exchange: str,
    symbol: str,
    quantity: int,
    buy_or_sell: str,  # "B" for Buy, "S" for Sell
    product_type: str,  # "C" (Cash), "D" (Delivery), "I" (Intraday)
    price_type: str,  # "LMT" (Limit), "MKT" (Market), "SL" (Stop Loss)
    price: float = 0,  # Required for Limit orders
    trigger_price: float = 0,  # For Stop Loss orders
    retention: str = "DAY"  # "DAY", "IOC", "EOS"
) -> dict:
    """Place a trading order."""
    
    try:
        order_params = {
            "buy_or_sell": buy_or_sell,
            "product_type": product_type,
            "exchange": exchange,
            "tradingsymbol": symbol,
            "quantity": quantity,
            "discloseqty": 0,
            "price_type": price_type,
            "price": price,
            "trigger_price": trigger_price,
            "retention": retention,
            "remarks": "my_order_001"
        }
        
        response = api.place_order(**order_params)
        return response
    except Exception as e:
        print(f"Error placing order: {e}")
        return None

# Example: Market Buy Order
order = place_order(
    exchange="NSE",
    symbol="RELIANCE-EQ",
    quantity=1,
    buy_or_sell="B",
    product_type="D",  # Delivery
    price_type="MKT"  # Market order
)

# Example: Limit Sell Order
order = place_order(
    exchange="NSE",
    symbol="RELIANCE-EQ",
    quantity=1,
    buy_or_sell="S",
    product_type="D",
    price_type="LMT",
    price=2500.0  # Limit price
)

# Example: Stop Loss Order
order = place_order(
    exchange="NSE",
    symbol="RELIANCE-EQ",
    quantity=1,
    buy_or_sell="S",
    product_type="D",
    price_type="SL",
    trigger_price=2400.0,  # Stop loss trigger
    price=2395.0  # Stop loss price
)
```

#### Modify Order

```python
def modify_order(
    order_id: str,
    exchange: str,
    symbol: str,
    quantity: int = None,
    price: float = None,
    price_type: str = None,
    trigger_price: float = None
) -> dict:
    """Modify an existing order."""
    
    try:
        modify_params = {
            "orderno": order_id,
            "exchange": exchange,
            "tradingsymbol": symbol
        }
        
        if quantity:
            modify_params["newquantity"] = quantity
        if price:
            modify_params["newprice"] = price
        if price_type:
            modify_params["newprice_type"] = price_type
        if trigger_price:
            modify_params["newtrigger_price"] = trigger_price
        
        response = api.modify_order(**modify_params)
        return response
    except Exception as e:
        print(f"Error modifying order: {e}")
        return None
```

#### Cancel Order

```python
def cancel_order(order_id: str, exchange: str, symbol: str) -> dict:
    """Cancel an order."""
    
    try:
        response = api.cancel_order(
            orderno=order_id,
            exchange=exchange,
            tradingsymbol=symbol
        )
        return response
    except Exception as e:
        print(f"Error canceling order: {e}")
        return None
```

#### Get Order Book

```python
def get_order_book() -> dict:
    """Get all orders."""
    
    try:
        orders = api.get_order_book()
        return orders
    except Exception as e:
        print(f"Error getting order book: {e}")
        return None
```

#### Get Trade Book

```python
def get_trade_book() -> dict:
    """Get all executed trades."""
    
    try:
        trades = api.get_trade_book()
        return trades
    except Exception as e:
        print(f"Error getting trade book: {e}")
        return None
```

### 3. Portfolio APIs

#### Get Holdings

```python
def get_holdings() -> dict:
    """Get current holdings."""
    
    try:
        holdings = api.get_holdings()
        return holdings
    except Exception as e:
        print(f"Error getting holdings: {e}")
        return None

# Example
holdings = get_holdings()
# Returns list of holdings with: symbol, quantity, avg_price, LTP, P&L, etc.
```

#### Get Positions

```python
def get_positions() -> dict:
    """Get open positions."""
    
    try:
        positions = api.get_positions()
        return positions
    except Exception as e:
        print(f"Error getting positions: {e}")
        return None

# Example
positions = get_positions()
# Returns list of positions with: symbol, quantity, avg_price, LTP, P&L, etc.
```

#### Get Limits

```python
def get_limits() -> dict:
    """Get available margins and limits."""
    
    try:
        limits = api.get_limits()
        return limits
    except Exception as e:
        print(f"Error getting limits: {e}")
        return None

# Example
limits = get_limits()
# Returns: cash, margin, available margin, etc.
```

### 4. User Profile APIs

#### Get User Details

```python
def get_user_details() -> dict:
    """Get user profile information."""
    
    try:
        profile = api.get_user_details()
        return profile
    except Exception as e:
        print(f"Error getting user details: {e}")
        return None
```

### 5. Instrument Master

#### Download Symbol Master

Shoonya provides symbol master files for all exchanges:

```python
import requests
import zipfile
import io

def download_symbol_master(exchange: str = "NSE") -> list:
    """Download symbol master file.
    
    Args:
        exchange: "NSE" or "BSE"
    """
    urls = {
        "NSE": "https://api.shoonya.com/NSE_symbols.txt.zip",
        "BSE": "https://api.shoonya.com/BSE_symbols.txt.zip"
    }
    
    url = urls.get(exchange.upper())
    if not url:
        raise ValueError(f"Invalid exchange: {exchange}")
    
    # Download and extract
    response = requests.get(url)
    response.raise_for_status()
    
    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
        # Extract CSV file
        csv_file = zip_file.namelist()[0]
        content = zip_file.read(csv_file).decode('utf-8')
    
    # Parse CSV
    lines = content.strip().split('\n')
    headers = lines[0].split(',')
    
    instruments = []
    for line in lines[1:]:
        values = line.split(',')
        instrument = dict(zip(headers, values))
        instruments.append(instrument)
    
    return instruments

# Example
nse_instruments = download_symbol_master("NSE")
# Returns list of all NSE instruments with: Token, TradingSymbol, Exchange, etc.

# Find specific stock
reliance = next(
    (inst for inst in nse_instruments 
     if inst.get("TradingSymbol") == "RELIANCE-EQ"),
    None
)
print(reliance)
```

---

## WebSocket Market Data

Shoonya provides excellent WebSocket support for real-time market data streaming.

### WebSocket Setup

```python
from NorenRestApiPy.NorenApi import NorenApi

class ShoonyaApi(NorenApi):
    """Shoonya API with WebSocket support."""
    
    def __init__(self):
        NorenApi.__init__(self)
        self.host = "https://api.shoonya.com/NorenWClientTP/"
        self.websocket = "wss://api.shoonya.com/NorenWSTP/"
    
    def setup_websocket(
        self,
        order_update_callback=None,
        subscribe_callback=None,
        socket_open_callback=None
    ):
        """Setup WebSocket connection."""
        
        self.start_websocket(
            order_update_callback=order_update_callback,
            subscribe_callback=subscribe_callback,
            socket_open_callback=socket_open_callback
        )

# Initialize and login
api = ShoonyaApi()
# ... login code ...

# Define callbacks
def on_market_data(message):
    """Handle market data updates."""
    print(f"Market Data: {message}")
    # Process: LTP, volume, bid, ask, OHLC, etc.

def on_order_update(order):
    """Handle order updates."""
    print(f"Order Update: {order}")
    # Process: order status, fills, etc.

def on_socket_open():
    """Handle socket connection."""
    print("WebSocket connected!")
    
    # Subscribe to instruments
    instruments = [
        "NSE|RELIANCE-EQ",
        "NSE|TCS-EQ",
        "NSE|INFY-EQ"
    ]
    api.subscribe(instruments)

# Start WebSocket
api.setup_websocket(
    order_update_callback=on_order_update,
    subscribe_callback=on_market_data,
    socket_open_callback=on_socket_open
)

# Keep connection alive
import time
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    api.stop_websocket()
```

### Subscribe to Instruments

```python
def subscribe_to_instruments(instruments: list):
    """Subscribe to market data for instruments.
    
    Args:
        instruments: List of strings in format "EXCHANGE|SYMBOL"
    """
    try:
        api.subscribe(instruments)
        print(f"Subscribed to {len(instruments)} instruments")
    except Exception as e:
        print(f"Error subscribing: {e}")

# Example: Subscribe to Nifty 500 stocks
nifty_500_symbols = [
    "NSE|RELIANCE-EQ",
    "NSE|TCS-EQ",
    "NSE|INFY-EQ",
    # ... 497 more
]

subscribe_to_instruments(nifty_500_symbols)
```

### Unsubscribe from Instruments

```python
def unsubscribe_from_instruments(instruments: list):
    """Unsubscribe from market data."""
    try:
        api.unsubscribe(instruments)
        print(f"Unsubscribed from {len(instruments)} instruments")
    except Exception as e:
        print(f"Error unsubscribing: {e}")
```

### WebSocket Advantages

- **Real-time**: Instant market data updates
- **Efficient**: Single connection for multiple instruments
- **Scalable**: Can handle 500+ stocks simultaneously
- **Lightweight**: Lower bandwidth than REST polling

---

## Rate Limits

Shoonya enforces rate limits to ensure service stability:

### REST API Limits

- **get_quotes API**: 
  - 10 requests per second
  - 200 requests per minute
  - ⚠️ **Exceeding limits may result in temporary blocking**

### Order Placement Limits

- **Orders per second**: 20
- **Orders per minute**: 200
- ⚠️ **Exceeding limits may result in order rejections**

### WebSocket Limits

- **No explicit limits** documented
- **Recommended**: Use WebSocket for real-time data instead of REST polling
- **Best Practice**: Monitor connection health and reconnect if needed

### Best Practices

1. **Use WebSocket**: For real-time data instead of REST polling
2. **Batch Requests**: Combine multiple instruments when possible
3. **Implement Rate Limiting**: Add delays between REST API calls
4. **Cache Responses**: Cache historical data to reduce API calls

```python
from time import sleep
from collections import deque
from datetime import datetime, timedelta

class ShoonyaRateLimiter:
    """Rate limiter for Shoonya API calls."""
    
    def __init__(self, max_calls: int, period_seconds: int):
        self.max_calls = max_calls
        self.period_seconds = period_seconds
        self.calls = deque()
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        now = datetime.now()
        
        # Remove old calls
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

# Usage for get_quotes (10 req/sec)
quotes_limiter = ShoonyaRateLimiter(max_calls=10, period_seconds=1)

for symbol in symbols:
    quotes_limiter.wait_if_needed()
    quote = api.get_quotes("NSE", symbol)
```

---

## Python Implementation Examples

### Complete Example: Shoonya Client Class

```python
from NorenRestApiPy.NorenApi import NorenApi
import hashlib
import pyotp
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time

class ShoonyaClient:
    """Complete Shoonya API client wrapper."""
    
    def __init__(self, credentials: dict):
        """Initialize Shoonya client.
        
        Args:
            credentials: Dict with user_id, password, totp_secret, 
                        vendor_code, api_secret, imei
        """
        self.api = NorenApi()
        self.api.host = "https://api.shoonya.com/NorenWClientTP/"
        self.api.websocket = "wss://api.shoonya.com/NorenWSTP/"
        
        self.credentials = credentials
        self.session_token = None
        self.session_expiry = None
        
        # Login
        self.login()
    
    def login(self) -> bool:
        """Login to Shoonya API."""
        try:
            # Get TOTP
            totp_secret = self.credentials.get("totp_secret")
            current_totp = pyotp.TOTP(totp_secret).now()
            
            # Encrypt password
            encrypted_pwd = hashlib.sha256(
                self.credentials["password"].encode()
            ).hexdigest()
            
            # Login
            response = self.api.login(
                userid=self.credentials["user_id"],
                pwd=encrypted_pwd,
                factor2=current_totp,
                vc=self.credentials["vendor_code"],
                apkversion="1.0.0",
                appkey=self.credentials["api_secret"],
                imei=self.credentials["imei"]
            )
            
            if response.get("stat") == "Ok":
                self.session_token = response["susertoken"]
                self.api.set_session_token(self.session_token)
                self.session_expiry = datetime.now() + timedelta(hours=24)
                print("✅ Login successful")
                return True
            else:
                print(f"❌ Login failed: {response}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def is_session_valid(self) -> bool:
        """Check if session is valid."""
        if not self.session_token:
            return False
        if self.session_expiry and datetime.now() >= self.session_expiry:
            return False
        return True
    
    def ensure_session(self) -> bool:
        """Ensure valid session."""
        if not self.is_session_valid():
            return self.login()
        return True
    
    # Market Data Methods
    def get_quote(self, exchange: str, symbol: str) -> Optional[Dict]:
        """Get market quote."""
        if not self.ensure_session():
            return None
        try:
            return self.api.get_quotes(exchange, symbol)
        except Exception as e:
            print(f"Error getting quote: {e}")
            return None
    
    def get_intraday_data(
        self,
        exchange: str,
        symbol: str,
        start_time: str,
        end_time: str,
        interval: str = "1"
    ) -> Optional[Dict]:
        """Get intraday historical data."""
        if not self.ensure_session():
            return None
        try:
            return self.api.get_time_price_series(
                exchange=exchange,
                token=symbol,
                starttime=start_time,
                endtime=end_time,
                interval=interval
            )
        except Exception as e:
            print(f"Error getting intraday data: {e}")
            return None
    
    def get_daily_data(
        self,
        exchange: str,
        symbol: str,
        start_date: str,
        end_date: str
    ) -> Optional[Dict]:
        """Get daily historical data."""
        if not self.ensure_session():
            return None
        try:
            return self.api.get_daily_price_series(
                exchange=exchange,
                token=symbol,
                startdate=start_date,
                enddate=end_date
            )
        except Exception as e:
            print(f"Error getting daily data: {e}")
            return None
    
    # Order Methods
    def place_order(
        self,
        exchange: str,
        symbol: str,
        quantity: int,
        buy_or_sell: str,
        product_type: str = "D",
        price_type: str = "MKT",
        price: float = 0,
        trigger_price: float = 0
    ) -> Optional[Dict]:
        """Place an order."""
        if not self.ensure_session():
            return None
        try:
            order_params = {
                "buy_or_sell": buy_or_sell,
                "product_type": product_type,
                "exchange": exchange,
                "tradingsymbol": symbol,
                "quantity": quantity,
                "discloseqty": 0,
                "price_type": price_type,
                "price": price,
                "trigger_price": trigger_price,
                "retention": "DAY",
                "remarks": "api_order"
            }
            return self.api.place_order(**order_params)
        except Exception as e:
            print(f"Error placing order: {e}")
            return None
    
    def cancel_order(self, order_id: str, exchange: str, symbol: str) -> Optional[Dict]:
        """Cancel an order."""
        if not self.ensure_session():
            return None
        try:
            return self.api.cancel_order(
                orderno=order_id,
                exchange=exchange,
                tradingsymbol=symbol
            )
        except Exception as e:
            print(f"Error canceling order: {e}")
            return None
    
    def get_orders(self) -> Optional[Dict]:
        """Get order book."""
        if not self.ensure_session():
            return None
        try:
            return self.api.get_order_book()
        except Exception as e:
            print(f"Error getting orders: {e}")
            return None
    
    # Portfolio Methods
    def get_holdings(self) -> Optional[Dict]:
        """Get holdings."""
        if not self.ensure_session():
            return None
        try:
            return self.api.get_holdings()
        except Exception as e:
            print(f"Error getting holdings: {e}")
            return None
    
    def get_positions(self) -> Optional[Dict]:
        """Get positions."""
        if not self.ensure_session():
            return None
        try:
            return self.api.get_positions()
        except Exception as e:
            print(f"Error getting positions: {e}")
            return None
    
    def get_limits(self) -> Optional[Dict]:
        """Get margins."""
        if not self.ensure_session():
            return None
        try:
            return self.api.get_limits()
        except Exception as e:
            print(f"Error getting limits: {e}")
            return None
    
    # WebSocket Methods
    def start_websocket(
        self,
        order_update_callback=None,
        subscribe_callback=None,
        socket_open_callback=None
    ):
        """Start WebSocket connection."""
        if not self.ensure_session():
            return False
        try:
            self.api.start_websocket(
                order_update_callback=order_update_callback,
                subscribe_callback=subscribe_callback,
                socket_open_callback=socket_open_callback
            )
            return True
        except Exception as e:
            print(f"Error starting WebSocket: {e}")
            return False
    
    def subscribe(self, instruments: List[str]):
        """Subscribe to instruments via WebSocket."""
        try:
            self.api.subscribe(instruments)
        except Exception as e:
            print(f"Error subscribing: {e}")
    
    def unsubscribe(self, instruments: List[str]):
        """Unsubscribe from instruments."""
        try:
            self.api.unsubscribe(instruments)
        except Exception as e:
            print(f"Error unsubscribing: {e}")

# Usage Example
if __name__ == "__main__":
    credentials = {
        "user_id": "FA12345",
        "password": "your_password",
        "totp_secret": "YOUR_TOTP_SECRET",
        "vendor_code": "FA12345_U",
        "api_secret": "your_api_key",
        "imei": "AA:BB:CC:DD:EE:FF"
    }
    
    # Initialize client
    client = ShoonyaClient(credentials)
    
    # Get market quote
    quote = client.get_quote("NSE", "RELIANCE-EQ")
    print(quote)
    
    # Get historical data
    daily = client.get_daily_data(
        "NSE", "RELIANCE-EQ",
        "01-01-2023", "31-12-2023"
    )
    print(daily)
    
    # Get holdings
    holdings = client.get_holdings()
    print(holdings)
```

---

## Best Practices

### 1. Session Management

- **Monitor Session**: Check validity before API calls
- **Auto Re-login**: Implement automatic re-login on expiry
- **Error Handling**: Handle session expiry gracefully

### 2. TOTP Management

- **Use TOTP**: Prefer TOTP over OTP for automation
- **Sync Time**: Ensure system clock is synchronized (TOTP is time-based)
- **Backup Secret**: Store TOTP secret securely

### 3. WebSocket Usage

- **Prefer WebSocket**: Use WebSocket for real-time data instead of REST polling
- **Connection Health**: Monitor connection and reconnect if needed
- **Batch Subscriptions**: Subscribe to multiple instruments at once

### 4. Rate Limiting

- **Implement Limits**: Add rate limiting for REST API calls
- **Use WebSocket**: Reduces REST API usage
- **Cache Data**: Cache historical data to reduce API calls

### 5. Error Handling

```python
def safe_api_call(api_func, *args, **kwargs):
    """Wrapper for safe API calls."""
    try:
        return api_func(*args, **kwargs)
    except Exception as e:
        error_msg = str(e)
        
        if "session" in error_msg.lower() or "token" in error_msg.lower():
            # Session expired, re-login
            print("Session expired, re-logging in...")
            client.login()
            # Retry once
            return api_func(*args, **kwargs)
        elif "rate limit" in error_msg.lower():
            # Rate limit exceeded
            print("Rate limit exceeded, waiting...")
            time.sleep(60)
            return None
        else:
            print(f"API Error: {e}")
            return None
```

### 6. Symbol Format

Shoonya uses specific symbol format:
- **Equity**: `RELIANCE-EQ` (Symbol-EQ)
- **Futures**: `NIFTY24JANFUT` (Symbol+Expiry+FUT)
- **Options**: `NIFTY24JAN18000CE` (Symbol+Expiry+Strike+CE/PE)

**Getting Symbols**: Use symbol master file or API to get correct format

---

## Error Handling

### Common Error Codes

| Error | Meaning | Solution |
|-------|--------|----------|
| `E01` | Invalid credentials | Check user_id, password, 2FA |
| `E02` | Session expired | Re-login |
| `E03` | Invalid symbol | Check symbol format |
| `E04` | Insufficient margin | Check available margin |
| `E05` | Rate limit exceeded | Wait and retry |
| `E06` | Order rejected | Check order parameters |

### Error Handling Example

```python
def handle_api_error(response: dict) -> bool:
    """Handle API error responses."""
    if response.get("stat") == "Ok":
        return True
    
    error_code = response.get("emsg", "")
    
    if "session" in error_code.lower():
        print("Session expired, re-logging in...")
        client.login()
        return False
    elif "rate limit" in error_code.lower():
        print("Rate limit exceeded, waiting 60 seconds...")
        time.sleep(60)
        return False
    else:
        print(f"API Error: {error_code}")
        return False
```

---

## Summary

### Key Takeaways

1. **Authentication**: Session-based with credentials + 2FA (TOTP recommended)
2. **Session Management**: Sessions expire after 24 hours, implement auto re-login
3. **WebSocket**: Excellent support for 500+ stocks simultaneously
4. **Rate Limits**: 10 req/sec for quotes, 20 orders/sec
5. **Symbol Format**: Use `SYMBOL-EQ` format for equity
6. **Password Encryption**: SHA-256 required

### Integration Checklist

- [ ] Register Shoonya account and complete KYC
- [ ] Generate API key from Prism portal
- [ ] Set up TOTP 2FA
- [ ] Get vendor code (ClientCode_U)
- [ ] Install ShoonyaApi-Py SDK
- [ ] Implement session management
- [ ] Set up WebSocket for real-time data
- [ ] Test with paper trading first
- [ ] Implement error handling and retry logic
- [ ] Set up logging and monitoring

---

## References

- [Shoonya Website](https://shoonya.com/)
- [Prism Portal](https://prism.shoonya.com)
- [Shoonya Python API GitHub](https://github.com/Shoonya-Dev/ShoonyaApi-Py)
- [Shoonya API Documentation PDF](https://shoonya.com/static/website/pdf/shoonya-Python-API.pdf)
- [Shoonya FAQ](https://faq.shoonya.com/api/)
- [Symbol Master Files](https://api.shoonya.com/NSE_symbols.txt.zip)

---

**Last Updated**: January 2025

**Note**: API specifications may change. Always refer to official Shoonya documentation for the latest information.

# Telegram Bot Guide

**Version**: 1.0  
**Last Updated**: January 2025

---

## Overview

The Telegram Bot serves as the primary user interface for the Agentic Stock Trading System. It provides:
- Trade approvals
- System status monitoring
- Real-time alerts
- Portfolio queries
- Emergency controls

---

## Setup

### Step 1: Create Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Follow prompts to name your bot
4. Copy the **bot token** (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Get Chat ID

1. Start a chat with your bot
2. Send any message to your bot
3. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Find your `chat_id` in the response (e.g., `123456789`)

### Step 3: Configure

Add to `.env`:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

---

## Commands

### Basic Commands

#### `/start`
**Purpose**: Initialize bot and show welcome message

**Usage**: `/start`

**Response**: Welcome message with available commands

---

#### `/status`
**Purpose**: Get system status

**Usage**: `/status`

**Response**:
```
System Status:
✅ Database: Connected
✅ Ollama: Running
✅ Shoonya: Connected
⚠️ Upstox: Disconnected
📊 Active Positions: 3
💰 Portfolio Value: ₹1,25,000
```

---

#### `/positions`
**Purpose**: List all current positions

**Usage**: `/positions`

**Response**:
```
Current Positions:
1. RELIANCE: 10 @ ₹2,450 (P&L: +2.5%)
2. TCS: 5 @ ₹3,200 (P&L: -1.2%)
3. INFY: 8 @ ₹1,500 (P&L: +0.8%)
```

---

#### `/kill`
**Purpose**: Emergency stop - halts all trading

**Usage**: `/kill`

**Response**: 
```
⚠️ EMERGENCY STOP ACTIVATED
All trading operations halted.
Type /resume to restart.
```

**Security**: Requires confirmation

---

#### `/resume`
**Purpose**: Resume trading after emergency stop

**Usage**: `/resume`

**Response**: `✅ Trading resumed`

---

### Query Commands

#### `/query <question>`
**Purpose**: Ask questions about portfolio, stocks, or system

**Usage**: 
- `/query show me oversold stocks`
- `/query what is my total P&L`
- `/query find stocks with RSI < 30`

**Response**: Natural language response from Database Librarian agent

---

### Approval Commands

When a trade signal is generated, the bot sends an approval request:

```
📊 New Trade Signal

Stock: RELIANCE
Action: BUY
Entry: ₹2,450
Stop Loss: ₹2,401 (2%)
Target: ₹2,548 (4%)
Confidence: 82%

[✅ Approve] [❌ Reject]
```

**Buttons**:
- **✅ Approve**: Executes the trade
- **❌ Reject**: Cancels the trade

---

## Alerts & Notifications

### Trade Alerts

**When**: Trade executed, stop loss hit, target reached

**Format**:
```
🔔 Trade Alert

RELIANCE: Target reached @ ₹2,548
Entry: ₹2,450 | Exit: ₹2,548
P&L: +4.0% (+₹980)
```

---

### System Alerts

**When**: System errors, API failures, critical events

**Format**:
```
⚠️ System Alert

Shoonya API connection lost
Switching to Upstox backup...
```

---

### Portfolio Alerts

**When**: Daily P&L summary, significant changes

**Format**:
```
📊 Daily Summary

Portfolio Value: ₹1,25,000
Today's P&L: +1.2% (+₹1,500)
Active Positions: 3
```

---

## Inline Keyboards

### Trade Approval Keyboard

```python
[
    [InlineKeyboardButton("✅ Approve", callback_data="approve_123")],
    [InlineKeyboardButton("❌ Reject", callback_data="reject_123")]
]
```

### Status Keyboard

```python
[
    [InlineKeyboardButton("📊 Positions", callback_data="positions")],
    [InlineKeyboardButton("💰 P&L", callback_data="pnl")],
    [InlineKeyboardButton("⚙️ Settings", callback_data="settings")]
]
```

---

## Implementation

### Bot Handler Structure

```python
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

async def start(update: Update, context):
    """Handle /start command."""
    await update.message.reply_text("Welcome! Use /help for commands.")

async def handle_approval(update: Update, context):
    """Handle trade approval button clicks."""
    query = update.callback_query
    if query.data.startswith("approve_"):
        # Execute trade
        await query.answer("Trade approved!")
    elif query.data.startswith("reject_"):
        # Cancel trade
        await query.answer("Trade rejected!")

# Register handlers
app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_approval))
```

---

## Error Handling

### Common Issues

**Issue**: Bot not responding
- **Solution**: Check bot token, verify bot is running

**Issue**: "Unauthorized" error
- **Solution**: Verify bot token is correct

**Issue**: Messages not received
- **Solution**: Check chat_id, ensure bot is started

---

## Security

### Best Practices

1. **Never expose bot token**: Keep in `.env`, never commit to git
2. **Verify chat_id**: Only respond to authorized users
3. **Rate limiting**: Implement to prevent spam
4. **Confirmation for critical actions**: Require confirmation for `/kill`

---

## Rate Limits

**Telegram API Limits**:
- 30 messages/second per bot
- 20 messages/second per chat

**Implementation**: Use rate limiting in bot handlers

---

## Testing

### Test Bot Locally

```python
# scripts/test_telegram_bot.py
from telegram import Bot

bot = Bot(token="YOUR_BOT_TOKEN")
updates = await bot.get_updates()
print(updates)
```

### Send Test Message

```python
await bot.send_message(
    chat_id=YOUR_CHAT_ID,
    text="Test message from trading bot"
)
```

---

## Configuration

### Environment Variables

```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
TELEGRAM_ENABLED=true
```

### Settings

```python
# config/settings.py
telegram_bot_token: str = ""
telegram_chat_id: str = ""
telegram_enabled: bool = True
```

---

## Monitoring

### Bot Health Check

```python
async def check_telegram_health():
    """Check if Telegram bot is operational."""
    try:
        bot = Bot(token=settings.telegram_bot_token)
        me = await bot.get_me()
        return me is not None
    except Exception as e:
        logger.error(f"Telegram bot error: {e}")
        return False
```

---

## Related Documentation

- [API Integration Summary](API_INTEGRATION_SUMMARY.md) - All API integrations
- [Configuration Reference](04_CONFIGURATION_REFERENCE.md) - Bot configuration
- [Troubleshooting Guide](06_TROUBLESHOOTING_AND_DEBUGGING.md) - Common issues

---

**Quick Reference**: See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for all commands.

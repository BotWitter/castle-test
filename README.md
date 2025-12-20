# X/Twitter Castle Test

The API solution for generating valid Castle.io(castle_token) tokens for X (Twitter) automation. High throughput, low latency, and seamless integration for automated workflows.


## 🚀 Quick Start

### Installation

```bash
pip install tls-client pycryptodome requests
```

### Basic Usage

```bash
# Basic authentication
python main.py username_or_email

# With proxy support
python main.py username_or_email --proxy http://user:pass@proxy:port

# With API key
python main.py username_or_email --api-key YOUR_API_KEY
```

## 💰 Pricing Plans

| Plan | Price | Rate Limit | Hourly Limit |
|------|-------|------------|--------------|
| **Starter** | $10/mo | 5 req/sec | 2,000 req/hour |
| **Basic** | $18/mo | 10 req/sec | 5,000 req/hour |
| **Pro** ⭐ | $30/mo | 20 req/sec | 12,000 req/hour |
| **Scale** | $50/mo | 40 req/sec | 30,000 req/hour |

## 🔗 API Endpoint

```
https://castle.botwitter.com/generate-token
```

## 💬 Support

Join our Discord community for help and updates:

**Discord:** https://discord.gg/5Th3puHagr

---

## 📋 Command Reference

### Arguments

- `username_or_email` - Your Twitter username or email (required)
- `--proxy` - Proxy server URL in format `http://user:pass@proxy:port` (optional)
- `--api-key` - Your API key for authentication (required)

### Examples

```bash
# Simple usage
python main.py myusername

# With authenticated proxy
python main.py myemail@example.com --proxy http://user:pass@proxy.example.com:8080
```

## Credits

[XClientTransaction](https://github.com/iSarabjitDhiman/XClientTransaction)
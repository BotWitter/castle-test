## x/twitter Castle Test

API access: 100 req/sec, 30,000/hour 35$ monthly

API access: 50 req/sec, 15,000/hour  20$ monthly

Endpoint:   `castle.botwitter.com/generate-token`

https://discord.gg/5Th3puHagr

## Usage

### Basic Authentication

```bash
python main.py username_or_email
```

### With Proxy

```bash
python main.py username_or_email --proxy http://user:pass@proxy:port
```

### With API Key

```bash
python main.py username_or_email --api-key YOUR_API_KEY
```

## Requirements

```bash
pip install tls-client pycryptodome requests
```
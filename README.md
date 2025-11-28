## x/twitter Castle Test

## Price
```
100 req/sec, 30,000/hour 50$ monthly
35 req/sec, 15,000/hour  25$ monthly 
10 req/sec, 10,000/hour 10$ monthly
```
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

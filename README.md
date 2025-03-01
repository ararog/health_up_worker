# Health Up Worker

A kafka consumer which receives messages from a Kafka topic, processes the messages, 
and sends SMS messages to a specified phone number using the Twilio API.

## License

MIT

## Requirements

Python 3.6

## Installation

### Clone the repository: 

```bash
git clone https://github.com/ararog/health_up_worker.git
```

### Update the .env file:

```plaintext
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_NUMBER=
DB_SERVER=
DB_NAME=
OPENAI_API_KEY=
TO_NUMBER=
```

### Server setup:

1. Create a Twilio account and get your account SID and auth token.
2. Update the .env file with your Twilio account SID, auth token, and twilio phone number, your phone number, and openai api key.

## Starting server

```bash
cd health_up_worker
uv sync
uv run main.py
```

## Testing

Open your whatsapp and send a message to your twilio number.
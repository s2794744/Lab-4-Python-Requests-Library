import requests
import json
import logging
from pathlib import Path

# Set up paths for saving files
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"

# Make sure the folders exist
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

#Set up logging
logging.basicConfig(
    filename=LOG_DIR / "lab4.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s" 

)

#  Connect to the Dad Jokes API
url = "https://icanhazdadjoke.com/"

headers = {
    "Accept": "application/json"
}

try:
    response = requests.get(
        url,
        headers=headers,
        timeout=10
    )

    # Check if the request was successful
    if response.status_code == 200:
        logging.info("LAB4_JOKE_HTTP_OK")
    else:
        logging.error("LAB4_ERR: HTTP %s", response.status_code)
        raise SystemExit(1)

except requests.RequestException as error:
    logging.error("LAB4_ERR: %s", error)
    raise SystemExit(1)

try:
    joke_data = response.json()
    joke = joke_data.get("joke")

    if not isinstance(joke, str) or not joke.strip():
        logging.error("LAB4_ERR: Joke missing from JSON")
        raise SystemExit(1)

    logging.info("LAB4_JOKE_JSON_OK")

except (ValueError, TypeError) as error:
    logging.error("LAB4_ERR: Invalid JSON - %s", error)
    raise SystemExit(1)

# Save the full JSON response
with open(DATA_DIR / "joke.json", "w") as file:
    json.dump(joke_data, file, indent=4)

# Save the joke as a text file
with open(DATA_DIR / "joke.txt", "w") as file:
    file.write(joke + "\n")

# Print only the joke
print(joke)
logging.info("LAB4_JOKE_PRINTED")

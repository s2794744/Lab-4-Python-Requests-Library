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

# Set up logging
logging.basicConfig(
    filename=LOG_DIR / "lab4.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

# Deck of Cards API
BASE_URL = "https://deckofcardsapi.com/api/deck"

#Create a new shuffled deck
def create_deck():
    url = f"{BASE_URL}/new/shuffle/?deck_count=1"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        deck_data = response.json()
        deck_id = deck_data.get("deck_id")

        if not deck_data.get("success") or not deck_id:
            logging.error("LAB4_ERR: Failed to create deck")
            raise SystemExit(1)

        logging.info("LAB4_DECK_CREATE_OK")
        return deck_id

    except (requests.RequestException, ValueError) as error:
        logging.error("LAB4_ERR: %s", error)
        raise SystemExit(1)

# Ask how many players will play
def get_players():
    while True:
        try:
            players = int(input("How many players? (2 or more): "))

            if 2 <= players <= 52:
                return players
            else:
                print("Please enter between 2 and 52 players.")
                logging.error("LAB4_ERR: Invalid player count")

        except ValueError:
            print("Please enter a valid number.")
            logging.error("LAB4_ERR: Invalid player input")

#Draw cards for the players
def draw_cards(deck_id, player_count):
    url = f"{BASE_URL}/{deck_id}/draw/?count={player_count}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        draw_data = response.json()
        cards = draw_data.get("cards", [])

        if not draw_data.get("success") or len(cards) != player_count:
            logging.error("LAB4_ERR: Failed to draw cards")
            raise SystemExit(1)

        logging.info("LAB4_DRAW_OK")
        return draw_data

    except (requests.RequestException, ValueError) as error:
        logging.error("LAB4_ERR: %s", error)
        raise SystemExit(1)

# Convert card ranks into numbers
def get_card_value(card):
    value = card["value"]

    ranks = {
        "ACE": 14,
        "KING": 13,
        "QUEEN": 12,
        "JACK": 11
    }

    if value in ranks:
        return ranks[value]
    else:
        return int(value)

# Start the High Card game
def play_game():
    player_count = get_players()

    # Create a new shuffled deck
    deck_id = create_deck()

    # Create a list of players
    players =  list(range(1, player_count + 1))

    # Store the results of each round
    rounds = []
    round_number = 1

    print("\nWelcome to the High Card Game!")
    print(f"Number of players: {player_count}")

    # Keep playing until there is one winner
    remaining_cards = 52

    while True:
        print(f"\nRound {round_number}")

        # Create a new deck if there are not enough cards
        if remaining_cards < len(players):
            deck_id = create_deck()
            remaining_cards = 52

        # Draw one card for each remaining player
        draw_data = draw_cards(deck_id, len(players))
        cards = draw_data["cards"]
        remaining_cards = draw_data["remaining"]

        # Store each player's card and rank
        results = []

        for player, card in zip(players, cards):
            value = get_card_value(card)

            results.append({
                "player": player,
                "card": card["value"],
                "suit": card["suit"],
                "rank": value
            })

            print(f"Player {player}: {card['value']} of {card['suit']}")

        # Find the highest card value
        highest_value = max(result["rank"] for result in results)

        # Find all players who have the highest card
        winners = [
            result["player"]
            for result in results
            if result["rank"] == highest_value
        ]

        # Save this round
        rounds.append({
            "round": round_number,
            "cards": results,
            "draw_response": draw_data
        })

        # Check if there is only one winner
        if len(winners) == 1:
            winner = winners[0]
            print(f"\nPlayer {winner} wins the game!")
            break

        # Handle tied players
        else:
            print(f"Tie between players: {winners}")
            logging.info("LAB4_TIE_ROUND")

            # Only tied players continue
            players = winners
            round_number += 1

    # Save all rounds to a JSON file
    with open(DATA_DIR / "high_card_rounds.json", "w") as file:
        json.dump(rounds, file, indent=4)

    # Create a summary of the game
    summary = [
        "High Card Game Results",
        f"Number of players: {player_count}",
        f"Total rounds played: {round_number}",
        f"Winner: Player {winner}"
    ]

    # Save the summary to a text file
    with open(DATA_DIR / "high_card_result.txt", "w") as file:
        file.write("\n".join(summary) + "\n")

    logging.info("LAB4_GAME_END")

if __name__ == "__main__":
    play_game()



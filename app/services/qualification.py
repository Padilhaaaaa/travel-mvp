def get_next_question(state: str) -> str:
    questions = {
        "start": "Hi! I can help qualify your trip request. First, what destination city or place do you have in mind?",
        "ask_period": "Great. What travel period are you considering?",
        "ask_travelers": "How many travelers will be part of this trip?",
        "ask_budget": "What budget range do you have in mind for this trip?",
        "ask_trip_type": "What kind of trip are you looking for? For example: couple, family, leisure, corporate.",
        "done": "Thanks. I have everything I need to qualify this lead."
    }
    return questions.get(state, "Thanks. I have everything I need.")


def infer_region(destination_city: str) -> str:
    city = destination_city.lower()

    if city in ["cancun", "mexico city", "tulum", "playa del carmen"]:
        return "Mexico"

    if city in ["miami", "orlando", "new york", "las vegas", "los angeles"]:
        return "USA"

    return "LATAM"


def classify_lead(destination_region: str, travelers_count: int, budget_range: str) -> str:
    score = 0
    budget_text = budget_range.lower().replace(" ", "")

    if destination_region in ["USA", "Mexico"]:
        score += 2
    else:
        score += 1

    if travelers_count >= 2:
        score += 1

    if any(value in budget_text for value in ["20k", "25k", "30k", "35k", "40k"]):
        score += 2
    elif any(value in budget_text for value in ["10k", "12k", "15k", "18k"]):
        score += 1

    if score >= 5:
        return "hot"
    if score >= 3:
        return "warm"
    return "cold"


def process_conversation_step(session: dict, message: str) -> dict:
    state = session.get("state", "start")
    lead = session.get("lead", {})

    if state == "start":
        lead["destination_city"] = message.strip()
        lead["destination_region"] = infer_region(lead["destination_city"])
        return {
            "reply": get_next_question("ask_period"),
            "state": "ask_period",
            "lead": lead,
            "completed": False
        }

    if state == "ask_period":
        lead["travel_period_text"] = message.strip()
        return {
            "reply": get_next_question("ask_travelers"),
            "state": "ask_travelers",
            "lead": lead,
            "completed": False
        }

    if state == "ask_travelers":
        try:
            lead["travelers_count"] = int(message.strip())
        except ValueError:
            return {
                "reply": "Please enter only the number of travelers, for example: 2",
                "state": "ask_travelers",
                "lead": lead,
                "completed": False
            }

        return {
            "reply": get_next_question("ask_budget"),
            "state": "ask_budget",
            "lead": lead,
            "completed": False
        }

    if state == "ask_budget":
        lead["budget_range"] = message.strip()
        return {
            "reply": get_next_question("ask_trip_type"),
            "state": "ask_trip_type",
            "lead": lead,
            "completed": False
        }

    if state == "ask_trip_type":
        lead["trip_type"] = message.strip()
        lead["lead_temperature"] = classify_lead(
            lead["destination_region"],
            lead["travelers_count"],
            lead["budget_range"]
        )

        return {
            "reply": (
                f"Perfect. I qualified this opportunity as {lead['lead_temperature']} lead "
                f"for {lead['destination_city']} ({lead['destination_region']})."
            ),
            "state": "done",
            "lead": lead,
            "completed": True
        }

    return {
        "reply": get_next_question("done"),
        "state": "done",
        "lead": lead,
        "completed": True
    }
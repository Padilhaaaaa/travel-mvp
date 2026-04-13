DESTINATION_OPTIONS = {
    "1": ("Chile", "Santiago"),
    "2": ("Chile", "Atacama"),
    "3": ("Peru", "Cusco / Machu Picchu"),
    "4": ("Colômbia", "Cartagena"),
    "5": ("Argentina", "Buenos Aires"),
    "6": ("México", "Cancún"),
    "7": ("República Dominicana", "Punta Cana"),
    "8": ("Outro", "A definir"),
}

TRIP_TYPE_OPTIONS = {
    "1": "Casal",
    "2": "Família",
    "3": "Amigos",
    "4": "Lua de mel",
    "5": "Solo",
}

BUDGET_OPTIONS = {
    "1": "Até R$ 5 mil por pessoa",
    "2": "R$ 5 mil a R$ 8 mil por pessoa",
    "3": "R$ 8 mil a R$ 12 mil por pessoa",
    "4": "Acima de R$ 12 mil por pessoa",
}

DECISION_TIMING_OPTIONS = {
    "1": "Quero fechar nos próximos 7 dias",
    "2": "Quero decidir ainda este mês",
    "3": "Estou pesquisando para os próximos meses",
    "4": "Ainda estou sem previsão",
}

PRIORITY_OPTIONS = {
    "1": "Melhor custo-benefício",
    "2": "Mais conforto",
    "3": "Roteiro completo com passeios",
    "4": "Experiência exclusiva",
    "5": "Praticidade e suporte",
}


def get_next_question(state: str) -> str:
    questions = {
        "start": (
            "Olá! Sou o assistente da LC Turismo e vou entender rapidamente o perfil da sua viagem "
            "para direcionar você da melhor forma.\n\n"
            "Qual destino você tem em mente hoje?\n"
            "1. Chile - Santiago\n"
            "2. Chile - Atacama\n"
            "3. Peru - Cusco / Machu Picchu\n"
            "4. Colômbia - Cartagena\n"
            "5. Argentina - Buenos Aires\n"
            "6. México - Cancún\n"
            "7. República Dominicana - Punta Cana\n"
            "8. Outro destino"
        ),
        "destination_city": (
            "Perfeito. Qual cidade, roteiro ou experiência você quer fazer nessa viagem?\n"
            "Exemplo: Valle Nevado, deserto, vinícolas, neve, praias, roteiro romântico."
        ),
        "travel_period_text": (
            "Ótimo. Em que período você pretende viajar?\n"
            "Pode me responder algo como: julho, setembro, réveillon, férias de dezembro ou data flexível."
        ),
        "travelers_count": (
            "Quantas pessoas vão viajar?"
        ),
        "trip_type": (
            "Entendi. Qual é o perfil dessa viagem?\n"
            "1. Casal\n"
            "2. Família\n"
            "3. Amigos\n"
            "4. Lua de mel\n"
            "5. Solo"
        ),
        "budget_range": (
            "Para eu indicar opções mais alinhadas, qual faixa de investimento você imagina por pessoa?\n"
            "1. Até R$ 5 mil por pessoa\n"
            "2. R$ 5 mil a R$ 8 mil por pessoa\n"
            "3. R$ 8 mil a R$ 12 mil por pessoa\n"
            "4. Acima de R$ 12 mil por pessoa"
        ),
        "decision_timing": (
            "Em que momento você pretende decidir ou fechar essa viagem?\n"
            "1. Quero fechar nos próximos 7 dias\n"
            "2. Quero decidir ainda este mês\n"
            "3. Estou pesquisando para os próximos meses\n"
            "4. Ainda estou sem previsão"
        ),
        "priority_focus": (
            "E hoje, o que pesa mais para você nessa viagem?\n"
            "1. Melhor custo-benefício\n"
            "2. Mais conforto\n"
            "3. Roteiro completo com passeios\n"
            "4. Experiência exclusiva\n"
            "5. Praticidade e suporte"
        ),
    }

    return questions.get(state, "Tudo certo.")


def process_conversation_step(session: dict, message: str) -> dict:
    state = session.get("state", "start")
    lead = session.get("lead", {})
    text = message.strip()

    if state == "start":
        option = DESTINATION_OPTIONS.get(text)

        if option:
            lead["destination_country"] = option[0]
            lead["destination_city"] = option[1]
        else:
            lead["destination_country"] = "Outro"
            lead["destination_city"] = text

        next_state = "destination_city"

        if lead["destination_city"] != "A definir":
            next_state = "travel_period_text"

        return {
            "state": next_state,
            "lead": lead,
            "reply": get_next_question(next_state),
            "completed": False,
        }

    if state == "destination_city":
        lead["destination_city"] = text
        next_state = "travel_period_text"

        return {
            "state": next_state,
            "lead": lead,
            "reply": get_next_question(next_state),
            "completed": False,
        }

    if state == "travel_period_text":
        lead["travel_period_text"] = text
        next_state = "travelers_count"

        return {
            "state": next_state,
            "lead": lead,
            "reply": get_next_question(next_state),
            "completed": False,
        }

    if state == "travelers_count":
        try:
            travelers_count = int(text)
            if travelers_count <= 0:
                raise ValueError
        except ValueError:
            return {
                "state": state,
                "lead": lead,
                "reply": "Por favor, me informe o número de viajantes usando apenas números. Exemplo: 2",
                "completed": False,
            }

        lead["travelers_count"] = travelers_count
        next_state = "trip_type"

        return {
            "state": next_state,
            "lead": lead,
            "reply": get_next_question(next_state),
            "completed": False,
        }

    if state == "trip_type":
        lead["trip_type"] = TRIP_TYPE_OPTIONS.get(text, text)
        next_state = "budget_range"

        return {
            "state": next_state,
            "lead": lead,
            "reply": get_next_question(next_state),
            "completed": False,
        }

    if state == "budget_range":
        lead["budget_range"] = BUDGET_OPTIONS.get(text, text)
        next_state = "decision_timing"

        return {
            "state": next_state,
            "lead": lead,
            "reply": get_next_question(next_state),
            "completed": False,
        }

    if state == "decision_timing":
        lead["decision_timing"] = DECISION_TIMING_OPTIONS.get(text, text)
        next_state = "priority_focus"

        return {
            "state": next_state,
            "lead": lead,
            "reply": get_next_question(next_state),
            "completed": False,
        }

    if state == "priority_focus":
        lead["priority_focus"] = PRIORITY_OPTIONS.get(text, text)
        lead["lead_temperature"] = classify_lead_temperature(lead)
        lead["notes_summary"] = build_notes_summary(lead)

        return {
            "state": "completed",
            "lead": lead,
            "reply": (
                "Perfeito! Já organizei as principais informações da sua viagem. "
                "Nosso time pode seguir com uma proposta mais alinhada ao seu perfil.\n\n"
                "Em instantes, um consultor da LC Turismo pode continuar esse atendimento com você."
            ),
            "completed": True,
        }

    return {
        "state": state,
        "lead": lead,
        "reply": "Não entendi muito bem sua resposta. Vamos continuar do ponto em que paramos.",
        "completed": False,
    }


def classify_lead_temperature(lead: dict) -> str:
    score = 0

    destination = lead.get("destination_country", "").lower()
    period = lead.get("travel_period_text", "").lower()
    travelers = lead.get("travelers_count", 0)
    budget = lead.get("budget_range", "").lower()
    decision = lead.get("decision_timing", "").lower()

    if destination and destination != "outro":
        score += 2

    if any(keyword in period for keyword in ["julho", "agosto", "setembro", "outubro", "novembro", "dezembro", "janeiro", "fevereiro", "março", "abril", "maio", "junho", "réveillon", "ferias", "férias"]):
        score += 2
    elif period:
        score += 1

    if travelers >= 2:
        score += 1

    if "8 mil" in budget or "12 mil" in budget or "acima" in budget:
        score += 2
    elif "5 mil" in budget:
        score += 1

    if "7 dias" in decision:
        score += 3
    elif "este mês" in decision:
        score += 2
    elif "próximos meses" in decision:
        score += 1

    if score >= 8:
        return "hot"
    if score >= 5:
        return "warm"
    return "cold"


def build_notes_summary(lead: dict) -> str:
    return (
        f"Destino: {lead.get('destination_country', '-')}; "
        f"Roteiro/Cidade: {lead.get('destination_city', '-')}; "
        f"Período: {lead.get('travel_period_text', '-')}; "
        f"Viajantes: {lead.get('travelers_count', '-')}; "
        f"Perfil: {lead.get('trip_type', '-')}; "
        f"Orçamento: {lead.get('budget_range', '-')}; "
        f"Decisão: {lead.get('decision_timing', '-')}; "
        f"Prioridade: {lead.get('priority_focus', '-')}"
    )
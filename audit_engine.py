import os
import base64
import json
import re
from groq import Groq
from rag import get_relevant_context
from dotenv import load_dotenv

load_dotenv()

def encode_image(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")

def calculate_conformity_score(diagnostic: str, niveau_risque: str) -> int:
    score = 50
    if niveau_risque == "Faible":
        score = 85
    elif niveau_risque == "Moyen":
        score = 55
    elif niveau_risque == "Élevé":
        score = 25
    return max(0, min(100, score))

def get_action_priority(conformity_score: int, niveau_risque: str) -> dict:
    if conformity_score < 30 or niveau_risque == "Élevé":
        return {"priorite": "URGENT", "delai": "24 heures", "couleur": "red"}
    elif conformity_score < 70 or niveau_risque == "Moyen":
        return {"priorite": "Court terme", "delai": "15 jours", "couleur": "orange"}
    else:
        return {"priorite": "Planifié", "delai": "3 mois", "couleur": "green"}

def analyze_audit(constat_text: str, image_bytes: bytes) -> dict:
    
    # Récupération du contexte
    try:
        context = get_relevant_context(constat_text)
    except Exception as e:
        print(f"Erreur RAG: {e}")
        context = ""

    # Initialisation Groq
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return _error_response("Clé GROQ_API_KEY manquante")

    client = Groq(api_key=api_key)
    base64_image = encode_image(image_bytes)

    system_prompt = """Tu es un auditeur qualité ISO 9001. Réponds UNIQUEMENT en JSON :

{
  "diagnostic": "diagnostic court",
  "clauses_concernees": ["clause1", "clause2"],
  "niveau_risque": "Faible | Moyen | Élevé",
  "actions_correctives": ["action1", "action2"],
  "recommandations": "conseils"
}"""

    user_message = f"Constat: {constat_text}\nContexte: {context}"

    try:
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": user_message},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]}
            ],
            temperature=0.2,
            max_tokens=1000,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(completion.choices[0].message.content)
        
    except Exception as e:
        return _error_response(f"Erreur Groq: {str(e)}")

    conformity_score = calculate_conformity_score(result.get("diagnostic", ""), result.get("niveau_risque", "Moyen"))
    priority_info = get_action_priority(conformity_score, result.get("niveau_risque", "Moyen"))

    result["conformite_score"] = conformity_score
    result["priorite_action"] = priority_info["priorite"]
    result["delai_recommandation"] = priority_info["delai"]
    result["priorite_couleur"] = priority_info["couleur"]

    return result

def _error_response(message: str) -> dict:
    return {
        "diagnostic": message,
        "clauses_concernees": ["Erreur technique"],
        "niveau_risque": "Moyen",
        "actions_correctives": ["Vérifier la clé API", "Réessayer"],
        "recommandations": "Problème technique",
        "conformite_score": 0,
        "priorite_action": "URGENT",
        "delai_recommandation": "Immédiat",
        "priorite_couleur": "red"
    }
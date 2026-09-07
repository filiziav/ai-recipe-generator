"""
AI Recipe Generator - Skolprojekt
Backend: Flask (Python 3) med Google Gemini API (google-genai)

Denna applikation fungerar som webbserver och API för receptgeneratorn.
Den tar emot råvaror, portionsantal och önskemål från webbläsaren
och skickar en förfrågan till Google Gemini AI via officiella 'google-genai' SDK:n.

SÄKERHET:
API-nyckeln laddas ALLTID från miljövariabeln GEMINI_API_KEY (eller från .env).
Nyckeln skrivs aldrig direkt i koden eller till versionshantering (GitHub).
"""

import os
import json
import logging
from typing import List
from flask import Flask, render_template, request, jsonify
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# Konfigurera loggning
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Standardmodell för Gemini (använder stabil flash-modell)
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")


def load_env_file():
    """
    Hjälpfunktion för att läsa in miljövariabler från en lokal .env-fil om den finns.
    Detta gör det smidigt för elever att köra projektet lokalt utan att installera extra paket.
    """
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, val = line.split("=", 1)
                        key = key.strip()
                        val = val.strip().strip("'\"")
                        if key and key not in os.environ:
                            os.environ[key] = val
        except Exception as e:
            logger.warning(f"Kunde inte läsa .env-fil: {e}")


# Läs eventuell .env-fil vid start
load_env_file()


# -----------------------------------------------------------------------------
# Pydantic-schema för strukturerat JSON-svar från Gemini
# Detta garanterar att AI-modellen svarar med exakt de fält webbsidan förväntar sig.
# -----------------------------------------------------------------------------
class RecipeModel(BaseModel):
    title: str = Field(description="Receptets inbjudande och kreativa titel på svenska")
    description: str = Field(description="En kort och aptitretande beskrivning av rätten på svenska")
    servings: int = Field(description="Antal portioner som receptet är beräknat för")
    prep_time: str = Field(description="Ungefärlig förberedelsetid, t.ex. '15 min'")
    cook_time: str = Field(description="Ungefärlig tillagningstid, t.ex. '20 min'")
    preferences: str = Field(description="Önskemål och preferenser som beaktats, t.ex. 'Vegetariskt, Starkt'")
    ingredients: List[str] = Field(description="Lista med ingredienser och mängder anpassade för antalet portioner på svenska")
    instructions: List[str] = Field(description="Numrerade eller stegvisa instruktioner för tillagningen på svenska")
    chef_tip: str = Field(description="Ett smart tips från kocken för att lyfta smaken eller förenkla tillagningen")


def generate_recipe_with_gemini(ingredients: str, servings: int, preferences: str) -> dict:
    """
    Anropar Google Gemini API via google-genai SDK för att generera ett skräddarsytt recept.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY saknas! Vänligen sätt miljövariabeln GEMINI_API_KEY "
            "eller skapa en .env-fil med din nyckel (se .env.example)."
        )

    # Initiera Gemini-klienten med API-nyckeln från miljövariabeln
    client = genai.Client(api_key=api_key)

    # Skapa en tydlig prompt på svenska
    prompt = f"""
Du är en professionell och inspirerande kock och receptkreatör.
Skapa ett komplett, välsmakande och genomtänkt recept på svenska baserat på följande förutsättningar:

- Tillgängliga råvaror och ingredienser: {ingredients}
- Antal portioner: {servings}
- Önskemål och preferenser: {preferences if preferences else 'Inga särskilda önskemål'}

Instruktioner för receptet:
1. Receptet MÅSTE skrivas helt på god, naturlig och inbjudande svenska.
2. Anpassa alla mått och ingredienser exakt efter {servings} portioner.
3. Du får använda basvaror som vanligen finns i ett skafferi (t.ex. salt, svartpeppar, olja, smör, vatten, enkla kryddor).
4. Följ användarens önskemål noga (till exempel om rätten ska vara vegetarisk, snabb, stark eller barnvänlig).
5. Instruktionerna ska vara tydliga och enkla att följa i köket.
6. Svara strikt enligt det angivna JSON-schemat.
"""

    # Konfigurera strukturerat JSON-svar
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=RecipeModel,
        temperature=0.7,
    )

    logger.info(f"Anropar Gemini ({GEMINI_MODEL}) för receptgenerering...")
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=config,
    )

    # Extrahera och tolka JSON-svaret
    raw_text = response.text
    if not raw_text:
        raise ValueError("Tomt svar mottogs från Gemini API.")

    recipe_data = json.loads(raw_text)
    return recipe_data


# -----------------------------------------------------------------------------
# Webbserver-rutter
# -----------------------------------------------------------------------------

@app.route("/")
def index():
    """Visar startsidan för receptgeneratorn."""
    return render_template("index.html")


@app.route("/api/generate-recipe", methods=["POST"])
def api_generate_recipe():
    """
    API-ändpunkt som tar emot användarens val och genererar ett recept via Google Gemini AI.
    Tar emot JSON: { "ingredients": "...", "servings": 2, "preferences": "..." }
    """
    data = request.get_json(silent=True) or {}

    ingredients = data.get("ingredients", "").strip()
    servings = data.get("servings", 2)
    preferences = data.get("preferences", "").strip()

    # Validering: Kontrollera att användaren har angett minst en ingrediens
    if not ingredients:
        return jsonify({
            "success": False,
            "error": "Vänligen ange vilka ingredienser du har hemma."
        }), 400

    # Validera portionsantal
    try:
        servings = int(servings)
        if servings < 1 or servings > 20:
            servings = 2
    except (ValueError, TypeError):
        servings = 2

    # Kontrollera om API-nyckeln är satt innan vi gör API-anrop
    if not os.environ.get("GEMINI_API_KEY"):
        return jsonify({
            "success": False,
            "error": "GEMINI_API_KEY saknas i miljön. Lägg till din API-nyckel i miljövariabeln GEMINI_API_KEY eller i en .env-fil för att generera recept med AI."
        }), 400

    # Anropa Google Gemini AI
    try:
        recipe = generate_recipe_with_gemini(ingredients, servings, preferences)
        return jsonify({
            "success": True,
            "recipe": recipe
        })
    except ValueError as ve:
        logger.warning(f"Valideringsfel eller konfigurationsfel vid AI-anrop: {ve}")
        return jsonify({
            "success": False,
            "error": str(ve)
        }), 400
    except Exception as e:
        logger.error(f"Fel vid anrop till Google Gemini API: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": f"Ett fel uppstod vid kommunikation med Google Gemini AI: {str(e)}"
        }), 500


if __name__ == "__main__":
    print("-------------------------------------------------------")
    print(" AI Recipe Generator startar med Google Gemini AI!")
    print(f" Modell: {GEMINI_MODEL}")
    print(f" API-nyckel laddad: {'JA' if os.environ.get('GEMINI_API_KEY') else 'NEJ (se .env.example)'}")
    print(" Öppna webbläsaren på: http://localhost:5000")
    print("-------------------------------------------------------")
    app.run(host="0.0.0.0", port=5000, debug=True)

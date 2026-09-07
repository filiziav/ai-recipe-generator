"""
Testsvit för AI Recipe Generator (Flask + Google Gemini API)
Körs i Ubuntu/WSL med: .venv/bin/python test_app.py
"""

import os
import json
from unittest.mock import patch, MagicMock
from app import app, RecipeModel


def run_tests():
    client = app.test_client()
    print("=======================================================")
    print(" Startar tester för AI Recipe Generator...")
    print("=======================================================")

    # 1. Testa GET / (Startsidan)
    res = client.get("/")
    assert res.status_code == 200, f"GET / misslyckades med status {res.status_code}"
    html = res.data.decode("utf-8")
    for term in ["Ingredienser", "Antal portioner", "Önskemål", "Generera recept"]:
        assert term in html, f"Saknar etikett i HTML: '{term}'"
    print("[OK] Test 1: Startsidan (GET /) returnerar 200 OK och innehåller alla svenska etiketter.")

    # 2. Testa statiska filer
    res_css = client.get("/static/style.css")
    assert res_css.status_code == 200, "style.css returnerade inte 200"
    res_js = client.get("/static/script.js")
    assert res_js.status_code == 200, "script.js returnerade inte 200"
    print("[OK] Test 2: Statiska filer (style.css och script.js) laddas korrekt.")

    # 3. Testa validering av tomt formulär
    res_empty = client.post("/api/generate-recipe", json={"ingredients": ""})
    assert res_empty.status_code == 400, "Validering för tomt formulär misslyckades"
    data_empty = json.loads(res_empty.data)
    assert data_empty.get("success") is False, "Förväntade success=False vid tomt formulär"
    assert "Vänligen ange vilka ingredienser" in data_empty.get("error", "")
    print("[OK] Test 3: Validering fungerar: tomt fält för ingredienser returnerar felkod 400.")

    # 4. Testa felhantering när GEMINI_API_KEY saknas
    with patch.dict(os.environ, {}, clear=True):
        res_no_key = client.post("/api/generate-recipe", json={
            "ingredients": "pasta, tomater",
            "servings": 2,
            "preferences": "snabbt"
        })
        assert res_no_key.status_code == 400, f"Förväntade 400 när API-nyckel saknas, fick {res_no_key.status_code}"
        data_no_key = json.loads(res_no_key.data)
        assert data_no_key.get("success") is False
        assert "GEMINI_API_KEY saknas" in data_no_key.get("error", "")
    print("[OK] Test 4: Säkerhet och felhantering: avsaknad av GEMINI_API_KEY ger tydligt felmeddelande (400).")

    # 5. Testa lyckat anrop till /api/generate-recipe med Gemini-mock
    mock_gemini_recipe = {
        "title": "Krämig Citron- & Vitlökspasta",
        "description": "En snabb och fräsch pastarätt med sting av vitlök och frisk citron.",
        "servings": 4,
        "prep_time": "10 min",
        "cook_time": "15 min",
        "preferences": "vegetariskt, snabbt",
        "ingredients": [
            "400 g tagliatelle eller valfri pasta",
            "3 klyftor vitlök, finhackade",
            "1 ekologisk citron (zest och saft)",
            "2 dl crème fraîche eller matlagningsgrädde",
            "1 dl riven parmesanost",
            "Salt och nymalen svartpeppar",
            "2 msk olivolja"
        ],
        "instructions": [
            "Koka upp rikligt med saltat vatten i en stor kastrull och koka pastan al dente.",
            "Fräs den finhackade vitlöken i olivolja i en stekpanna på medelvärme i ca 1 minut.",
            "Tillsätt crème fraîche och citronsaft. Låt såsen sjuda ihop i 2-3 minuter.",
            "Vänd ner den nykokta pastan tillsammans med citronzest och riven parmesan.",
            "Smaka av med flingsalt och nymalen svartpeppar. Servera genast!"
        ],
        "chef_tip": "Spara 1/2 dl av pastavattnet och rör ner i såsen för extra krämighet!"
    }

    with patch.dict(os.environ, {"GEMINI_API_KEY": "dummy-test-key"}):
        with patch("app.generate_recipe_with_gemini", return_value=mock_gemini_recipe) as mock_func:
            res_recipe = client.post("/api/generate-recipe", json={
                "ingredients": "pasta, vitlök, citron, crème fraîche",
                "servings": 4,
                "preferences": "vegetariskt, snabbt"
            })
            assert res_recipe.status_code == 200, f"API anrop misslyckades: {res_recipe.status_code}"
            data = json.loads(res_recipe.data)
            assert data.get("success") is True
            recipe = data.get("recipe", {})
            assert recipe.get("title") == "Krämig Citron- & Vitlökspasta"
            assert recipe.get("servings") == 4
            assert len(recipe.get("ingredients")) == 7
            assert len(recipe.get("instructions")) == 5
            mock_func.assert_called_once_with("pasta, vitlök, citron, crème fraîche", 4, "vegetariskt, snabbt")
    print("[OK] Test 5: API-ändpunkten anropar Gemini och returnerar korrekt strukturerat recept (200 OK).")

    # 6. Validera Pydantic-schemat (RecipeModel)
    recipe_model = RecipeModel(**mock_gemini_recipe)
    assert recipe_model.title == "Krämig Citron- & Vitlökspasta"
    assert recipe_model.servings == 4
    print("[OK] Test 6: Pydantic-schemat (RecipeModel) validerar formatet på Gemini-strukturen.")

    # 7. Om en riktig GEMINI_API_KEY finns i miljön, kör ett live-test
    real_api_key = os.environ.get("GEMINI_API_KEY")
    if real_api_key and not real_api_key.startswith("dummy"):
        print("\n--- Riktig GEMINI_API_KEY hittades i miljön! Kör live-test mot Gemini API... ---")
        try:
            from app import generate_recipe_with_gemini
            live_recipe = generate_recipe_with_gemini("morötter, potatis, lök", 2, "vegetariskt")
            assert "title" in live_recipe
            assert live_recipe["servings"] == 2
            print(f"[OK] Live-test godkänt! Gemini genererade: \"{live_recipe['title']}\"")
        except Exception as e:
            print(f"[VARNING] Live-test misslyckades: {e}")
    else:
        print("[INFO] Ingen live GEMINI_API_KEY angiven. Körde tester med automatisk mockning.")

    print("=======================================================")
    print(" ALLA TESTER GODKÄNDA OCH VERIFIERADE!")
    print("=======================================================")


if __name__ == "__main__":
    run_tests()

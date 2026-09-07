# AI Recipe Generator (Skolprojekt)

En enkel och ren webbapplikation byggd med **Python & Flask** på backend och **HTML, CSS och JavaScript** på frontend. Applikationen använder **Google Gemini AI** (`google-genai`) för att skapa skräddarsydda recept på svenska utifrån råvaror man har hemma.

---

## 📁 Projektstruktur

```text
ai-recipe-generator/
│
├── app.py                  # Flask-webbserver och API integrerat med Google Gemini
├── requirements.txt        # Python-beroenden (Flask, google-genai, pydantic)
├── test_app.py             # Automatiska tester för API, validering och modellschema
├── .gitignore              # Skyddar API-nycklar och .env från GitHub
├── .env.example            # Mall för miljövariabeln GEMINI_API_KEY
├── README.md               # Dokumentation och instruktioner
│
├── static/
│   ├── style.css           # Modern och responsiv stilmall
│   └── script.js           # Hanterar formulär, API-anrop och dynamisk visning
│
└── templates/
    └── index.html          # Webbplatsens huvudsida med svenskt gränssnitt
```

---

## 🔑 Konfigurera din Google Gemini API-nyckel

> [!IMPORTANT]
> **Säkerhet:** Skriv aldrig din API-nyckel direkt i källkoden och ladda aldrig upp den på GitHub. Filen `.gitignore` är konfigurerad för att automatiskt förhindra att `.env` laddas upp.

Välj ett av följande två sätt att sätta nyckeln i Ubuntu/WSL:

### Alternativ A: Skapa en `.env`-fil (Enklast)
Skapa en fil med namnet `.env` i projektmappen:
```bash
cp .env.example .env
nano .env
```
Fyll i din API-nyckel:
```env
GEMINI_API_KEY=din_faktiska_gemini_api_nyckel_här
```

### Alternativ B: Sätt som miljövariabel i terminalen
```bash
export GEMINI_API_KEY="din_faktiska_gemini_api_nyckel_här"
```

---

## 🚀 Hur du kör projektet i Ubuntu / WSL

Projektet körs i projektets virtuella miljö (`.venv`).

### 1. Navigera till projektmappen i WSL
```bash
cd /mnt/c/Users/fvatt/.gemini/antigravity/scratch/ai-recipe-generator
```

### 2. Starta servern
```bash
.venv/bin/python app.py
```
*(Eller aktivera miljön med `source .venv/bin/activate` och kör `python3 app.py`)*

### 3. Öppna i din webbläsare
Öppna valfri webbläsare i Windows (Chrome, Edge, Firefox, etc.) och gå till:
👉 **[http://localhost:5000](http://localhost:5000)**

---

## 🧪 Kör testerna

Kör testsviten för att verifiera servern, valideringen och AI-schemat:
```bash
.venv/bin/python test_app.py
```

---

## 💡 Hur AI-receptgeneratorn fungerar

1. **Klienten (Frontend)**:
   - Användaren anger råvaror i **Ingredienser**, väljer **Antal portioner** och eventuella **Önskemål** (t.ex. vegetariskt, snabbt).
   - När användaren klickar på **Generera recept** skickas en JSON-förfrågan via `fetch()` till `/api/generate-recipe`.

2. **Servern (Backend + Gemini AI)**:
   - Flask tar emot förfrågan och validerar indata.
   - Den initierar `genai.Client` med `GEMINI_API_KEY` och anropar modellen `gemini-3.6-flash`.
   - Med hjälp av **Structured Outputs** (via `pydantic` och `RecipeModel`) garanteras att Gemini alltid returnerar ett välformaterat JSON-objekt med titel, portioner, tillagningstid, ingredienslista och numrerade instruktioner på svenska.

3. **Presentation**:
   - `script.js` tar emot JSON-svaret och bygger upp det färdiga receptet på sidan utan att webbsidan behöver laddas om.

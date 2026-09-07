# AI Recipe Generator (Skolprojekt)

---

## Projektstruktur

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
Applikationen är driftsatt på AWS EC2 och finns tillgänglig här:
http://16.171.146.78:5000

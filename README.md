# Dust Investment Agent – Prototyp

Private Streamlit-Anwendung für einen kompakten Dust Investment Report.

## Funktionen
- Eingabe von Börsenticker oder FMP-Symbol
- Abruf von Profil, Kurs, GuV, Bilanz und Cashflow
- deterministische Kennzahlenberechnung
- einfacher Dust Investment Score
- qualitative Analyse über die OpenAI Responses API
- PDF-Export
- Friedrich Vorwerk als Testfall (`VH2.DE`)

## Lokal starten
```bash
git clone <DEIN-REPOSITORY>
cd dust-investment-agent
python -m venv .venv
```
Windows: `.venv\Scripts\activate`
macOS/Linux: `source .venv/bin/activate`

Dann:
```bash
pip install -r requirements.txt
streamlit run app.py
```

Kopiere `.streamlit/secrets.example.toml` nach `.streamlit/secrets.toml` und trage deine API-Schlüssel ein. Diese Datei niemals zu GitHub hochladen.

## Streamlit Community Cloud
1. Dateien in dein privates GitHub-Repository hochladen.
2. In Streamlit Community Cloud eine neue App erstellen.
3. Repository, Branch und `app.py` auswählen.
4. Unter Advanced settings / Secrets eintragen:
```toml
OPENAI_API_KEY = "..."
FMP_API_KEY = "..."
OPENAI_MODEL = "gpt-5-mini"
```
5. App bereitstellen.

## Grenzen
Der Prototyp erfindet keine fehlenden Daten. Vor Anlageentscheidungen sind Geschäftsbericht, Quartalsbericht, IR-Mitteilungen und aktuelle Marktdaten gegenzuprüfen. Keine individuelle Anlageberatung.

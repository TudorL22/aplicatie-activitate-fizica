import os
from dotenv import load_dotenv
import google.generativeai as genai

# Încărcăm variabilele din .env
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


class AntrenorAI:
    def __init__(self):
        # Dacă nu găsește cheia → AI dezactivat
        if not GOOGLE_API_KEY or GOOGLE_API_KEY.strip() == "":
            print("⚠ AVERTISMENT: Nu există API key în .env")
            self.activ = False
            return

        try:
            genai.configure(api_key=GOOGLE_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.5-flash')

            self.activ = True
        except Exception as e:
            print("Eroare configurare AI:", e)
            self.activ = False

    def chat_cu_antrenorul(self, mesaj_user, istoric, active, exercitii_disponibile):
        if not self.activ:
            return (
                "AI-ul nu este configurat. Verifică fișierul .env "
                "și adaugă GOOGLE_API_KEY."
            )

        context = f"""
Ești un antrenor personal profesionist.
Istoric utilizator: {istoric}
Exerciții active: {active}
Exerciții disponibile: {exercitii_disponibile}

Întrebarea utilizatorului: {mesaj_user}

Răspunde scurt, logic și personalizat.
"""

        try:
            reply = self.model.generate_content(context)
            return reply.text
        except Exception as e:
            return f"Eroare în conectarea la AI: {e}"

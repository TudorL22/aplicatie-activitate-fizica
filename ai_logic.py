import google.generativeai as genai

# PUNE CHEIA TA AICI
GOOGLE_API_KEY = "AIzaSyC1tczJXqTUaT5r7BhkrxaeuAAYCQmqnX4"


class AntrenorAI:
    def __init__(self):
        try:
            genai.configure(api_key=GOOGLE_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.5-pro')
            self.activ = True
        except Exception as e:
            print(f"Eroare AI: {e}")
            self.activ = False

    def chat_cu_antrenorul(self, mesaj_user, istoric, active, exercitii_disponibile):
        if not self.activ:
            return "Eroare: AI neconfigurat sau cheie incorectă."

        context = f"""
        Ești un antrenor personal de fitness.

        CONTEXT UTILIZATOR:
        - Istoric (ce a terminat deja): {istoric}
        - Exerciții ACTIVE acum (ce lucrează): {active}

        REGULĂ: Recomandă DOAR exerciții din această listă disponibilă: {exercitii_disponibile}

        ÎNTREBAREA UTILIZATORULUI: "{mesaj_user}"

        Răspunde scurt și util.
        """

        try:
            response = self.model.generate_content(context)
            return response.text
        except Exception as e:
            return f"Eroare conexiune: {e}"
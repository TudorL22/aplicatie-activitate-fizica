# Aplicație de Activitate Fizică 🏋️‍♂️

Aplicație desktop dezvoltată în **Python**, care permite utilizatorilor să își gestioneze antrenamentele fizice, să urmărească progresul și să primească recomandări pentru antrenamente viitoare cu ajutorul unui modul AI.

Proiect realizat în echipă în cadrul facultății.

---

## Funcționalități
- Autentificare și gestionare utilizatori
- Creare și monitorizare sesiuni de antrenament
- Salvarea datelor despre exerciții (seturi, repetări, durată, calorii)
- Stocarea datelor într-o bază de date locală (SQLite)
- Recomandări pentru antrenamente viitoare folosind inteligență artificială
- Interfață grafică realizată cu Tkinter

---

## Tehnologii utilizate
- Python 3
- Tkinter
- SQLite
- JSON
- Google Generative AI (Gemini)
- Git & GitHub

---

## Structura proiectului
````
aplicatie-activitate-fizica/
│
├── main.py              # punctul de intrare în aplicație
├── database.py          # gestionarea bazei de date
├── workout_logic.py     # logica pentru antrenamente
├── ai_logic.py          # modul AI pentru recomandări
├── users.json           # date utilizatori
└── README.md
````


---

## Instalare și rulare

1. Clonează repository-ul:
```bash
git clone https://github.com/USERNAME/aplicatie-activitate-fizica.git
```
2. Intră în directorul proiectului:
````bash
cd aplicatie-activitate-fizica
````
3. Instalează dependențele necesare:
````bash
pip install google-generativeai
````
4. Rulează aplicația:
````bash
python main.py
````
----
## Observații

- Aplicația rulează local

- Pentru funcționalitățile AI este necesară o cheie API Google

- Baza de date este creată automat la prima rulare

- Proiectul are scop educațional

----

## Autori

- Tudor Lungu
- Ionescu Tudor
- Rotariu Ștefan
- Iancu Teodor
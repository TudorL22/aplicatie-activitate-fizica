import tkinter as tk
from tkinter import messagebox
import json
import os


class NodUtilizator:
    def __init__(self, username, parola, exercitiu_activ=None):
        self.username = username
        self.parola = parola
        self.exercitiu_activ = exercitiu_activ
        self.urmatorul = None


class ListaUtilizatori:
    def __init__(self):
        self.head = None
        self.fisier_salvare = "users.json"

    def adauga_utilizator(self, username, parola, exercitiu_activ=None):
        nou_nod = NodUtilizator(username, parola, exercitiu_activ)
        if not self.head:
            self.head = nou_nod
        else:
            curent = self.head
            while curent.urmatorul:
                curent = curent.urmatorul
            curent.urmatorul = nou_nod
        return nou_nod

    def gaseste_utilizator(self, username, parola):
        curent = self.head
        while curent:
            if curent.username == username and curent.parola == parola:
                return curent
            curent = curent.urmatorul
        return None

    def exista_username(self, username):
        curent = self.head
        while curent:
            if curent.username == username:
                return True
            curent = curent.urmatorul
        return False

    def salveaza_datele(self):
        data_de_salvat = []
        curent = self.head
        while curent:
            user_dict = {
                "username": curent.username,
                "parola": curent.parola,
                "exercitiu_activ": curent.exercitiu_activ
            }
            data_de_salvat.append(user_dict)
            curent = curent.urmatorul

        with open(self.fisier_salvare, "w") as f:
            json.dump(data_de_salvat, f, indent=4)

    def incarca_datele(self):
        if not os.path.exists(self.fisier_salvare):
            return

        try:
            with open(self.fisier_salvare, "r") as f:
                data_incarcata = json.load(f)
                for user in data_incarcata:
                    activ = user.get("exercitiu_activ")
                    self.adauga_utilizator(user["username"], user["parola"], activ)
        except:
            pass


class AplicatieFitness(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Aplicație Activitate Fizică")
        self.geometry("450x600")

        self.lista_utilizatori = ListaUtilizatori()
        self.lista_utilizatori.incarca_datele()

        self.user_curent = None

        if not self.lista_utilizatori.head:
            self.lista_utilizatori.adauga_utilizator("admin", "1234")
            self.lista_utilizatori.salveaza_datele()

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (PaginaStart, PaginaLogin, PaginaSignUp, PaginaSucces, PaginaDashboard):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("PaginaStart")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        if page_name == "PaginaDashboard":
            frame.construieste_dashboard()
        frame.tkraise()

    def login_user(self, nod_user):
        self.user_curent = nod_user
        self.show_frame("PaginaDashboard")

    def logout_user(self):
        self.user_curent = None
        self.show_frame("PaginaStart")


class PaginaStart(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        label = tk.Label(self, text="Bine ai venit!", font=("Arial", 18))
        label.pack(pady=40)

        tk.Button(self, text="1. Log In", width=20, height=2,
                  command=lambda: controller.show_frame("PaginaLogin")).pack(pady=10)

        tk.Button(self, text="2. Sign Up", width=20, height=2,
                  command=lambda: controller.show_frame("PaginaSignUp")).pack(pady=10)


class PaginaSignUp(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Creare Cont Nou", font=("Arial", 16)).pack(pady=20)

        tk.Label(self, text="Alege un Username:").pack()
        self.entry_user = tk.Entry(self)
        self.entry_user.pack(pady=5)

        tk.Label(self, text="Alege o Parolă:").pack()
        self.entry_pass = tk.Entry(self, show="*")
        self.entry_pass.pack(pady=5)

        tk.Label(self, text="Confirmă Parola:").pack()
        self.entry_confirm = tk.Entry(self, show="*")
        self.entry_confirm.pack(pady=5)

        tk.Button(self, text="Creare Cont", bg="#ccffcc",
                  command=self.proceseaza_signup).pack(pady=20)

        tk.Button(self, text="Înapoi",
                  command=lambda: controller.show_frame("PaginaStart")).pack()

    def proceseaza_signup(self):
        user = self.entry_user.get()
        parola = self.entry_pass.get()
        confirm = self.entry_confirm.get()

        if not user or not parola:
            messagebox.showwarning("Eroare", "Toate câmpurile sunt obligatorii!")
            return

        if parola != confirm:
            messagebox.showerror("Eroare", "Parolele nu se potrivesc!")
            return

        if self.controller.lista_utilizatori.exista_username(user):
            messagebox.showerror("Eroare", f"Username-ul '{user}' este deja folosit!")
            return

        self.controller.lista_utilizatori.adauga_utilizator(user, parola)
        self.controller.lista_utilizatori.salveaza_datele()

        self.entry_user.delete(0, 'end')
        self.entry_pass.delete(0, 'end')
        self.entry_confirm.delete(0, 'end')

        self.controller.show_frame("PaginaSucces")


class PaginaSucces(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        label = tk.Label(self, text="Contul a fost creat\ncu succes!",
                         font=("Arial", 16), fg="green")
        label.pack(pady=50)
        tk.Button(self, text="Înapoi la Pagina de Start", width=25, height=2,
                  command=lambda: controller.show_frame("PaginaStart")).pack(pady=20)


class PaginaLogin(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Autentificare", font=("Arial", 16)).pack(pady=30)

        tk.Label(self, text="Username:").pack()
        self.entry_user = tk.Entry(self)
        self.entry_user.pack(pady=5)

        tk.Label(self, text="Parola:").pack()
        self.entry_pass = tk.Entry(self, show="*")
        self.entry_pass.pack(pady=5)

        tk.Button(self, text="Intră în cont",
                  command=self.verifica_login).pack(pady=20)

        tk.Button(self, text="Înapoi",
                  command=lambda: controller.show_frame("PaginaStart")).pack()

    def verifica_login(self):
        user = self.entry_user.get()
        parola = self.entry_pass.get()

        nod_gasit = self.controller.lista_utilizatori.gaseste_utilizator(user, parola)

        if nod_gasit:
            self.entry_user.delete(0, 'end')
            self.entry_pass.delete(0, 'end')
            self.controller.login_user(nod_gasit)
        else:
            messagebox.showerror("Eroare", "Username sau parolă greșită!")


class PaginaDashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.top_frame = tk.Frame(self)
        self.top_frame.pack(fill="x", pady=10)
        tk.Label(self.top_frame, text="Alege Antrenamentul", font=("Arial", 16)).pack()

        self.canvas = tk.Canvas(self)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.date_antrenamente = {
            "Antrenament Piept": ["Bench Press", "Flyers", "Cable Crossovers"],
            "Antrenament Picioare": ["Leg Press", "Calf Raises", "Squats"],
            "Antrenament Spate": ["Seated Cable Rows", "Deadlift", "Pull Ups"],
            "Antrenament Brate": ["Bicep Curl", "Tricep Dips", "Overhead Press"]
        }

    def construieste_dashboard(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        tk.Label(self.scrollable_frame, text=f"Utilizator: {self.controller.user_curent.username}",
                 fg="gray").pack(pady=5)

        for categorie, exercitii in self.date_antrenamente.items():
            self.creeaza_categorie(self.scrollable_frame, categorie, exercitii)

        tk.Button(self.scrollable_frame, text="Delogare", bg="#ffcccc",
                  command=self.controller.logout_user).pack(pady=20)

    def creeaza_categorie(self, parent, categorie, lista_exercitii):
        frame_categorie = tk.Frame(parent, borderwidth=1, relief="solid")
        frame_categorie.pack(fill="x", pady=5, padx=10)

        frame_exercitii = tk.Frame(frame_categorie)

        def toggle_exercitii():
            if frame_exercitii.winfo_viewable():
                frame_exercitii.pack_forget()
            else:
                frame_exercitii.pack(fill="x", pady=5)

        tk.Button(frame_categorie, text=categorie, command=toggle_exercitii,
                  font=("Arial", 11, "bold"), bg="#e0e0e0").pack(fill="x")

        exercitiu_activ_user = self.controller.user_curent.exercitiu_activ

        for ex in lista_exercitii:
            row_frame = tk.Frame(frame_exercitii)
            row_frame.pack(fill="x", pady=2, padx=10)

            tk.Label(row_frame, text=ex, anchor="w").pack(side="left")

            if exercitiu_activ_user == ex:
                btn_frame = tk.Frame(row_frame)
                btn_frame.pack(side="right")

                tk.Button(btn_frame, text="Vezi Progres", bg="lightblue", font=("Arial", 8),
                          command=lambda e=ex: self.arata_progres(e)).pack(side="left", padx=2)

                tk.Button(btn_frame, text="STOP", bg="#ffcccc", font=("Arial", 8),
                          command=self.stop_exercitiu).pack(side="left", padx=2)
            else:
                tk.Button(row_frame, text="START", bg="#90ee90", font=("Arial", 8),
                          command=lambda e=ex: self.porneste_exercitiu(e)).pack(side="right")

    def porneste_exercitiu(self, nume_exercitiu):
        self.controller.user_curent.exercitiu_activ = nume_exercitiu
        self.controller.lista_utilizatori.salveaza_datele()
        self.construieste_dashboard()

    def stop_exercitiu(self):
        self.controller.user_curent.exercitiu_activ = None
        self.controller.lista_utilizatori.salveaza_datele()
        self.construieste_dashboard()

    def arata_progres(self, nume):
        messagebox.showinfo("Progres", f"Aici vei vedea progresul pentru: {nume}")


if __name__ == "__main__":
    app = AplicatieFitness()
    app.mainloop()
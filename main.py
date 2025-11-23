import tkinter as tk
from tkinter import messagebox


# --- STRUCTURI DE DATE (Linked List) ---

class NodUtilizator:
    """Aceasta este structura (nodul) care ține datele unui singur utilizator."""

    def __init__(self, username, parola):
        self.username = username
        self.parola = parola
        self.antrenament_activ = None  # Aici vom stoca ulterior antrenamentul
        self.urmatorul = None  # Pointer către următorul utilizator din listă


class ListaUtilizatori:
    """Aceasta gestionează lista de noduri."""

    def __init__(self):
        self.head = None  # Capul listei (primul utilizator)

    def adauga_utilizator(self, username, parola):
        nou_nod = NodUtilizator(username, parola)
        if not self.head:
            self.head = nou_nod
        else:
            # Parcurgem lista până la final și adăugăm noul nod
            curent = self.head
            while curent.urmatorul:
                curent = curent.urmatorul
            curent.urmatorul = nou_nod

    def exista_username(self, username):
        """Verifică dacă username-ul există deja în listă."""
        curent = self.head
        while curent:
            if curent.username == username:
                return True
            curent = curent.urmatorul
        return False

    def valideaza_login(self, username, parola):
        """Caută perechea username/parolă. Returnează True dacă e corect."""
        curent = self.head
        while curent:
            if curent.username == username and curent.parola == parola:
                return True
            curent = curent.urmatorul
        return False


# --- APLICAȚIA PRINCIPALĂ ---

class AplicatieFitness(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Aplicație Activitate Fizică")
        self.geometry("400x550")

        # Inițializăm lista de utilizatori
        self.lista_utilizatori = ListaUtilizatori()

        # Adăugăm un user de test (opțional, ca să nu trebuiască să creezi unul mereu)
        self.lista_utilizatori.adauga_utilizator("admin", "1234")

        # Containerul principal
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # Lista tuturor paginilor
        for F in (PaginaStart, PaginaLogin, PaginaSignUp, PaginaSucces, PaginaDashboard):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("PaginaStart")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()


# --- PAGINILE ---

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

        # Username
        tk.Label(self, text="Alege un Username:").pack()
        self.entry_user = tk.Entry(self)
        self.entry_user.pack(pady=5)

        # Parola
        tk.Label(self, text="Alege o Parolă:").pack()
        self.entry_pass = tk.Entry(self, show="*")
        self.entry_pass.pack(pady=5)

        # Confirmare Parolă
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

        # Validări
        if not user or not parola:
            messagebox.showwarning("Eroare", "Toate câmpurile sunt obligatorii!")
            return

        if parola != confirm:
            messagebox.showerror("Eroare", "Parolele nu se potrivesc!")
            return

        # Verificăm în lista de structuri dacă userul există deja
        if self.controller.lista_utilizatori.exista_username(user):
            messagebox.showerror("Eroare", f"Username-ul '{user}' este deja folosit!")
            return

        # Dacă totul e ok, adăugăm în listă
        self.controller.lista_utilizatori.adauga_utilizator(user, parola)

        # Curățăm câmpurile
        self.entry_user.delete(0, 'end')
        self.entry_pass.delete(0, 'end')
        self.entry_confirm.delete(0, 'end')

        # Mergem la pagina de succes
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

        # Verificăm folosind lista de structuri din controller
        if self.controller.lista_utilizatori.valideaza_login(user, parola):
            self.controller.show_frame("PaginaDashboard")
            self.entry_user.delete(0, 'end')
            self.entry_pass.delete(0, 'end')
        else:
            messagebox.showerror("Eroare", "Username sau parolă greșită!")


class PaginaDashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        label = tk.Label(self, text="Alege Antrenamentul", font=("Arial", 16))
        label.pack(pady=20)

        lista_frame = tk.Frame(self)
        lista_frame.pack(fill="both", expand=True, padx=20)

        antrenamente = ["Antrenament Piept", "Antrenament Picioare", "Antrenament Spate", "Cardio"]

        for nume in antrenamente:
            self.creeaza_antrenament(lista_frame, nume)

        tk.Button(self, text="Delogare", bg="#ffcccc",
                  command=lambda: controller.show_frame("PaginaStart")).pack(pady=20)

    def creeaza_antrenament(self, parent, nume_antrenament):
        item_frame = tk.Frame(parent, borderwidth=1, relief="solid")
        item_frame.pack(fill="x", pady=5)

        optiuni_frame = tk.Frame(item_frame)

        def toggle_optiuni():
            if optiuni_frame.winfo_viewable():
                optiuni_frame.pack_forget()
            else:
                optiuni_frame.pack(fill="x", pady=5)

        tk.Button(item_frame, text=nume_antrenament, command=toggle_optiuni,
                  font=("Arial", 10, "bold")).pack(fill="x")

        tk.Button(optiuni_frame, text="Opțiunea 1 (Detalii)", width=25).pack()
        tk.Button(optiuni_frame, text="Opțiunea 2 (Start)", width=25).pack()
        tk.Button(optiuni_frame, text="Opțiunea 3 (Istoric)", width=25).pack()


if __name__ == "__main__":
    app = AplicatieFitness()
    app.mainloop()
import tkinter as tk
from tkinter import messagebox
from database import Database
from workout_logic import WorkoutSession


class AplicatieFitness(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Aplicație Activitate Fizică")
        self.geometry("450x600")

        self.db = Database()
        self.user_curent = None

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (PaginaStart, PaginaLogin, PaginaSignUp, PaginaSucces, PaginaDashboard):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("PaginaStart")

    def show_frame(self, name):
        frame = self.frames[name]
        if name == "PaginaDashboard":
            frame.construieste_dashboard()
        frame.tkraise()

    def login_user(self, user_id, username):
        self.user_curent = {"id": user_id, "username": username}
        self.show_frame("PaginaDashboard")

    def logout_user(self):
        self.user_curent = None
        self.show_frame("PaginaStart")


class PaginaStart(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Bine ai venit!", font=("Arial", 18)).pack(pady=40)
        tk.Button(self, text="Log In", width=20,
                  command=lambda: controller.show_frame("PaginaLogin")).pack(pady=10)
        tk.Button(self, text="Sign Up", width=20,
                  command=lambda: controller.show_frame("PaginaSignUp")).pack(pady=10)


class PaginaSignUp(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Creare cont", font=("Arial", 16)).pack(pady=20)

        self.entry_user = tk.Entry(self)
        self.entry_pass = tk.Entry(self, show="*")
        self.entry_conf = tk.Entry(self, show="*")

        for txt, w in [("Username", self.entry_user),
                       ("Parola", self.entry_pass),
                       ("Confirmă parola", self.entry_conf)]:
            tk.Label(self, text=txt).pack()
            w.pack(pady=5)

        tk.Button(self, text="Creează",
                  command=self.signup).pack(pady=20)

        tk.Button(self, text="Înapoi",
                  command=lambda: controller.show_frame("PaginaStart")).pack()

    def signup(self):
        u = self.entry_user.get()
        p = self.entry_pass.get()
        c = self.entry_conf.get()

        if not u or not p:
            messagebox.showerror("Eroare", "Completează toate câmpurile")
            return
        if p != c:
            messagebox.showerror("Eroare", "Parolele nu coincid")
            return
        if not self.controller.db.adauga_utilizator(u, p):
            messagebox.showerror("Eroare", "Username deja existent")
            return

        self.controller.show_frame("PaginaSucces")


class PaginaSucces(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Cont creat cu succes!",
                 fg="green", font=("Arial", 16)).pack(pady=50)
        tk.Button(self, text="Înapoi",
                  command=lambda: controller.show_frame("PaginaStart")).pack()


class PaginaLogin(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Autentificare", font=("Arial", 16)).pack(pady=30)

        self.entry_user = tk.Entry(self)
        self.entry_pass = tk.Entry(self, show="*")

        tk.Label(self, text="Username").pack()
        self.entry_user.pack()
        tk.Label(self, text="Parola").pack()
        self.entry_pass.pack()

        tk.Button(self, text="Login",
                  command=self.login).pack(pady=20)

    def login(self):
        u = self.entry_user.get()
        p = self.entry_pass.get()
        rezultat = self.controller.db.autentifica(u, p)

        if rezultat:
            user_id, username = rezultat
            self.controller.login_user(user_id, username)
        else:
            messagebox.showerror("Eroare", "Login invalid")


class PaginaDashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # o singură sesiune activă permisă
        self.sesiuni = {}

        self.antrenamente = {
            "Piept": ["Bench Press", "Flyers", "Cable Crossovers"],
            "Picioare": ["Squats", "Leg Press", "Calf Raises"],
            "Spate": ["Pull Ups", "Deadlift", "Seated Rows"]
        }

    def construieste_dashboard(self):
        for w in self.winfo_children():
            w.destroy()

        user_id = self.controller.user_curent["id"]
        active = self.controller.db.exercitii_user(user_id)

        tk.Label(self, text=f"Utilizator: {self.controller.user_curent['username']}",
                 fg="gray").pack(pady=10)

        for cat, exs in self.antrenamente.items():
            tk.Label(self, text=cat, font=("Arial", 12, "bold")).pack(pady=5)
            for ex in exs:
                frame = tk.Frame(self)
                frame.pack(fill="x", padx=20)
                tk.Label(frame, text=ex).pack(side="left")

                if ex in self.sesiuni:
                    tk.Button(frame, text="Vezi progres",
                              command=lambda e=ex: self.vezi_progres(e)).pack(side="right")
                    tk.Button(frame, text="STOP",
                              command=lambda e=ex: self.stop(e)).pack(side="right")

                elif ex in active:
                    tk.Button(frame, text="STOP",
                              command=lambda e=ex: self.stop(e)).pack(side="right")

                else:
                    tk.Button(frame, text="START",
                              command=lambda e=ex: self.start(e)).pack(side="right")

        tk.Button(self, text="Delogare",
                  command=self.controller.logout_user,
                  bg="#ffcccc").pack(pady=20)

    def start(self, exercitiu):
        # ❌ blocare start multiplu
        if self.sesiuni:
            messagebox.showwarning(
                "Exercițiu deja activ",
                "Există deja un exercițiu activ.\n"
                "Oprește-l înainte de a începe altul."
            )
            return

        self.sesiuni[exercitiu] = WorkoutSession(exercitiu)
        self.controller.db.adauga_exercitiu(
            self.controller.user_curent["id"], exercitiu
        )
        self.construieste_dashboard()

    def vezi_progres(self, exercitiu):
        sesiune = self.sesiuni.get(exercitiu)
        if not sesiune:
            messagebox.showinfo("Progres exercițiu",
                                "Nu există o sesiune activă pentru acest exercițiu.")
            return

        win = tk.Toplevel(self)
        win.title(f"Progres - {exercitiu}")
        win.geometry("420x360")
        win.resizable(False, False)

        lbl_state = tk.Label(win, font=("Arial", 10))
        lbl_state.pack(pady=4)

        lbl_time = tk.Label(win, font=("Arial", 12))
        lbl_time.pack(pady=4)

        lbl_reps = tk.Label(win, font=("Arial", 12))
        lbl_reps.pack(pady=4)

        lbl_sets = tk.Label(win, font=("Arial", 12))
        lbl_sets.pack(pady=4)

        lbl_cal = tk.Label(win, font=("Arial", 12))
        lbl_cal.pack(pady=4)

        pause_win = {"win": None, "label": None}

        def update():
            if not win.winfo_exists():
                return

            sesiune.step()

            lbl_state.config(text=f"Stare: {sesiune.get_state()}")
            lbl_time.config(text=f"Timp total: {sesiune.get_duration()} sec")
            lbl_reps.config(text=f"Repetiții totale: {sesiune.get_reps_total()}")
            lbl_sets.config(text=f"Serii: {sesiune.get_sets()}")
            lbl_cal.config(text=f"Calorii arse: {sesiune.calories()} kcal")

            if sesiune.pause_just_started:
                pw = tk.Toplevel(win)
                pw.title("Pauză")
                pw.geometry("350x250")
                pw.resizable(False, False)

                tk.Label(pw, text="Pauză! Odihnește-te 1:30",
                         font=("Arial", 12, "bold")).pack(pady=10)
                l = tk.Label(pw, font=("Arial", 18))
                l.pack(pady=10)

                pause_win["win"] = pw
                pause_win["label"] = l

            if sesiune.in_pause and pause_win["win"]:
                pause_win["label"].config(
                    text=f"{sesiune.get_pause_remaining()} sec"
                )
            elif not sesiune.in_pause and pause_win["win"]:
                pause_win["win"].destroy()
                pause_win["win"] = None
                pause_win["label"] = None

            win.after(1000, update)

        update()

    def stop(self, exercitiu):
        sesiune = self.sesiuni.pop(exercitiu, None)

        if sesiune:
            sesiune.step()
            self.controller.db.salveaza_antrenament(
                self.controller.user_curent["id"],
                exercitiu,
                sesiune.start_clock(),
                sesiune.get_duration(),
                sesiune.get_reps_total(),
                sesiune.get_sets(),
                sesiune.calories()
            )

        self.controller.db.sterge_exercitiu(
            self.controller.user_curent["id"], exercitiu
        )
        self.construieste_dashboard()


if __name__ == "__main__":
    app = AplicatieFitness()
    app.mainloop()

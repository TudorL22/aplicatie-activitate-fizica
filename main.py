import tkinter as tk
from tkinter import messagebox
import threading  # <--- IMPORT NECESAR PENTRU MULTITHREADING
from database import Database
from workout_logic import WorkoutSession
from ai_logic import AntrenorAI


class AplicatieFitness(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Aplicație Activitate Fizică")
        self.geometry("500x800")

        self.db = Database()
        self.ai = AntrenorAI()
        self.user_curent = None

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

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
        self.db.sterge_toate_exercitiile_active(user_id)
        self.db.sterge_istoric_sesiune(user_id)

        if "PaginaDashboard" in self.frames:
            self.frames["PaginaDashboard"].reset_interfata()

        self.show_frame("PaginaDashboard")

    def logout_user(self):
        if self.user_curent and "PaginaDashboard" in self.frames:
            self.frames["PaginaDashboard"].opreste_tot_fortat()
        self.user_curent = None
        self.show_frame("PaginaStart")

    def on_closing(self):
        if self.user_curent and "PaginaDashboard" in self.frames:
            self.frames["PaginaDashboard"].opreste_tot_fortat()
        self.destroy()


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
        for txt, w in [("Username", self.entry_user), ("Parola", self.entry_pass),
                       ("Confirmă parola", self.entry_conf)]:
            tk.Label(self, text=txt).pack()
            w.pack(pady=5)
        tk.Button(self, text="Creează", command=self.signup).pack(pady=20)
        tk.Button(self, text="Înapoi", command=lambda: controller.show_frame("PaginaStart")).pack()

    def signup(self):
        u = self.entry_user.get()
        p = self.entry_pass.get()
        c = self.entry_conf.get()
        if not u or not p: messagebox.showerror("Eroare", "Completează toate câmpurile"); return
        if p != c: messagebox.showerror("Eroare", "Parolele nu coincid"); return
        if not self.controller.db.adauga_utilizator(u, p): messagebox.showerror("Eroare",
                                                                                "Username deja existent"); return
        self.controller.show_frame("PaginaSucces")


class PaginaSucces(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Cont creat cu succes!", fg="green", font=("Arial", 16)).pack(pady=50)
        tk.Button(self, text="Înapoi", command=lambda: controller.show_frame("PaginaStart")).pack()


class PaginaLogin(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        tk.Label(self, text="Autentificare", font=("Arial", 16)).pack(pady=30)
        self.entry_user = tk.Entry(self)
        self.entry_pass = tk.Entry(self, show="*")
        tk.Label(self, text="Username").pack();
        self.entry_user.pack()
        tk.Label(self, text="Parola").pack();
        self.entry_pass.pack()
        tk.Button(self, text="Login", command=self.login).pack(pady=20)

    def login(self):
        u = self.entry_user.get()
        p = self.entry_pass.get()
        rezultat = self.controller.db.autentifica(u, p)
        if rezultat:
            user_id, username = rezultat
            self.entry_user.delete(0, tk.END)
            self.entry_pass.delete(0, tk.END)
            self.controller.login_user(user_id, username)
        else:
            messagebox.showerror("Eroare", "Login invalid")


class PaginaDashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.sesiuni = {}
        self.ferestre_progres = {}

        self.antrenamente = {
            "Piept": ["Bench Press", "Flyers", "Cable Crossovers"],
            "Picioare": ["Squats", "Leg Press", "Calf Raises"],
            "Spate": ["Pull Ups", "Deadlift", "Seated Rows"],
            "Brate": ["Bicep Curl", "Tricep Dips", "Overhead Press"]
        }

        # --- ZONA CHAT AI ---
        self.chat_frame = tk.Frame(self, bg="#f0f0f0", bd=2, relief="groove")
        self.chat_frame.pack(fill="x", pady=5, padx=5)

        tk.Label(self.chat_frame, text="Antrenor AI", bg="#f0f0f0", font=("Arial", 10, "bold")).pack()

        input_f = tk.Frame(self.chat_frame, bg="#f0f0f0")
        input_f.pack(pady=2)

        self.chat_entry = tk.Entry(input_f, width=35)
        self.chat_entry.pack(side="left", padx=5)
        self.chat_entry.bind("<Return>", lambda e: self.trimite_ai())

        # Butonul trimite (il salvam ca sa il putem dezactiva cat timp gandeste AI)
        self.btn_trimite = tk.Button(input_f, text="Trimite", bg="#e6e6fa", command=self.trimite_ai)
        self.btn_trimite.pack(side="left")

        self.chat_response = tk.Text(self.chat_frame, height=8, width=55, state="disabled", font=("Arial", 9))
        self.chat_response.pack(pady=5, padx=5)
        # --------------------

        self.content_frame = tk.Frame(self)
        self.content_frame.pack(fill="both", expand=True)

    def reset_interfata(self):
        self.chat_response.config(state="normal")
        self.chat_response.delete("1.0", tk.END)
        self.chat_response.config(state="disabled")
        self.chat_entry.delete(0, tk.END)
        self.sesiuni = {}
        self.ferestre_progres = {}

    def opreste_tot_fortat(self):
        exercitii_active = list(self.sesiuni.keys())
        for ex in exercitii_active:
            self.stop(ex, confirmare=False)

    # --- FUNCTIA MODIFICATA PENTRU MULTITHREADING ---
    def trimite_ai(self):
        msg = self.chat_entry.get()
        if not msg.strip(): return

        # 1. Afisam mesajul de asteptare
        self.chat_response.config(state="normal")
        self.chat_response.delete("1.0", tk.END)
        self.chat_response.insert(tk.END, "Thinking...")
        self.chat_response.config(state="disabled")

        # 2. Dezactivam input-ul ca sa nu trimita de 2 ori
        self.chat_entry.config(state="disabled")
        self.btn_trimite.config(state="disabled")

        # 3. Pregatim datele necesare
        user_id = self.controller.user_curent["id"]
        try:
            istoric = self.controller.db.get_istoric_text(user_id)
        except AttributeError:
            istoric = []
        active = self.controller.db.exercitii_user(user_id)

        toate_ex = []
        for l in self.antrenamente.values():
            toate_ex.extend(l)

        # 4. Definim functia care va rula in fundal (thread)
        def thread_task():
            # Aici dureaza mult, dar nu blocheaza interfata
            raspuns = self.controller.ai.chat_cu_antrenorul(msg, istoric, active, toate_ex)

            # Cand e gata, programam actualizarea interfetei pe firul principal
            self.after(0, lambda: self.afiseaza_raspuns(raspuns))

        # 5. Pornim firul de executie
        threading.Thread(target=thread_task, daemon=True).start()

    def afiseaza_raspuns(self, raspuns):
        """Aceasta functie este chemata cand AI-ul termina de gandit."""
        self.chat_response.config(state="normal")
        self.chat_response.delete("1.0", tk.END)
        self.chat_response.insert(tk.END, raspuns)
        self.chat_response.config(state="disabled")

        # Reactivam input-ul
        self.chat_entry.delete(0, tk.END)
        self.chat_entry.config(state="normal")
        self.btn_trimite.config(state="normal")
        # ------------------------------------------------

    def construieste_dashboard(self):
        for w in self.content_frame.winfo_children():
            w.destroy()

        user_id = self.controller.user_curent["id"]
        active = self.controller.db.exercitii_user(user_id)

        tk.Label(self.content_frame, text=f"Utilizator: {self.controller.user_curent['username']}",
                 fg="gray").pack(pady=5)

        for cat, exs in self.antrenamente.items():
            tk.Label(self.content_frame, text=cat, font=("Arial", 12, "bold")).pack(pady=5)
            for ex in exs:
                frame = tk.Frame(self.content_frame)
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

        tk.Button(self.content_frame, text="Delogare",
                  command=self.controller.logout_user,
                  bg="#ffcccc").pack(pady=20)

    def start(self, exercitiu):
        if self.sesiuni:
            messagebox.showwarning("Atentie", "Exista deja un exercitiu activ.")
            return

        self.sesiuni[exercitiu] = WorkoutSession(exercitiu)
        self.controller.db.adauga_exercitiu(
            self.controller.user_curent["id"], exercitiu
        )
        self.construieste_dashboard()

    def vezi_progres(self, exercitiu):
        sesiune = self.sesiuni.get(exercitiu)
        if not sesiune:
            messagebox.showinfo("Info", "Sesiunea nu este activa local.")
            return

        if exercitiu in self.ferestre_progres:
            try:
                self.ferestre_progres[exercitiu].lift()
                return
            except tk.TclError:
                del self.ferestre_progres[exercitiu]

        win = tk.Toplevel(self)
        win.title(f"Progres - {exercitiu}")
        win.geometry("420x360")

        self.ferestre_progres[exercitiu] = win

        def on_win_close():
            if exercitiu in self.ferestre_progres:
                del self.ferestre_progres[exercitiu]
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_win_close)

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
            if not win.winfo_exists(): return
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
                tk.Label(pw, text="Pauză! Odihnește-te 1:30", font=("Arial", 12, "bold")).pack(pady=10)
                l = tk.Label(pw, font=("Arial", 18))
                l.pack(pady=10)
                pause_win["win"] = pw
                pause_win["label"] = l

            if sesiune.in_pause and pause_win["win"]:
                pause_win["label"].config(text=f"{sesiune.get_pause_remaining()} sec")
            elif not sesiune.in_pause and pause_win["win"]:
                pause_win["win"].destroy()
                pause_win["win"] = None
                pause_win["label"] = None

            win.after(1000, update)

        update()

    def stop(self, exercitiu, confirmare=True):
        if confirmare:
            raspuns = messagebox.askyesno("Stop", "Esti sigur?")
            if not raspuns: return

        if exercitiu in self.ferestre_progres:
            try:
                self.ferestre_progres[exercitiu].destroy()
            except tk.TclError:
                pass
            del self.ferestre_progres[exercitiu]

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

        try:
            self.construieste_dashboard()
        except tk.TclError:
            pass


if __name__ == "__main__":
    app = AplicatieFitness()
    app.mainloop()
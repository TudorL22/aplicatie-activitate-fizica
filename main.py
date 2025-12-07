import tkinter as tk
from tkinter import messagebox
import threading  # <--- IMPORT NECESAR PENTRU MULTITHREADING
from database import Database
from workout_logic import WorkoutSession
from ai_logic import AntrenorAI


# ----------- FITNESS NEON DARK THEME -----------



# Fundal principal
BG_MAIN      = "#0D0B21"   # navy + violet foarte închis

# Panouri / carduri
PANEL_BG     = "#16162A"   # violet grafit

# Texte
TEXT_FG      = "#F2F3FA"   # aproape alb
TEXT_SUB     = "#AAB0C8"   # gri deschis-violet

# Entry-uri
ENTRY_BG  = "#FFFFFF"   # alb curat
ENTRY_FG  = "#0A0F24"   # albastru foarte închis (blue-black)

# Buton primar — gradient neon violet
BTN_PRIMARY_BG       = "#7B2FFF"
BTN_PRIMARY_HOVER    = "#9B54FF"
BTN_PRIMARY_FG       = "white"

# Buton Start — turcoaz neon
BTN_START_BG         = "#00D9A3"
BTN_START_HOVER      = "#00E8B2"
BTN_START_FG         = "black"

# Buton Stop — roșu neon
BTN_STOP_BG          = "#FF3B6A"
BTN_STOP_HOVER       = "#FF5C86"
BTN_STOP_FG          = "white"

# Buton secundar (de ex. Înapoi)
BTN_SECONDARY_BG     = "#2E2E45"
BTN_SECONDARY_HOVER  = "#3C3C55"
BTN_SECONDARY_FG     = "white"

# Compatibilitate cu vechiul cod
BTN_BG       = BTN_PRIMARY_BG
BTN_BG_HOVER = BTN_PRIMARY_HOVER
BTN_FG       = BTN_PRIMARY_FG



# -------- COMPATIBILITATE CU CODUL VECHI --------
BTN_BG = BTN_PRIMARY_BG
BTN_BG_HOVER = BTN_PRIMARY_HOVER
BTN_FG = BTN_PRIMARY_FG

BTN_HEIGHT = 3   # înălțime mai mare
BTN_PADY   = 6   # distanță verticală în interior
BTN_PADX   = 10  # distanță laterală



class AplicatieFitness(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Aplicație Activitate Fizică")

        # dimensiune inițială + maximizare
        self.geometry("900x700")
        try:
            self.state("zoomed")  # Windows
        except Exception:
            pass

        self.configure(bg=BG_MAIN)

        self.db = Database()
        self.ai = AntrenorAI()
        self.user_curent = None

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        container = tk.Frame(self, bg=BG_MAIN)
        container.pack(fill="both", expand=True)

        # facem containerul să se întindă pe tot
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

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
        # curățăm eventualele sesiuni anterioare din DB
        if hasattr(self.db, "sterge_toate_exercitiile_active"):
            self.db.sterge_toate_exercitiile_active(user_id)
        if hasattr(self.db, "sterge_istoric_sesiune"):
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


# ---------------- PAGINA START ----------------
class PaginaStart(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_MAIN)
        self.controller = controller

        wrapper = tk.Frame(self, bg=BG_MAIN)
        wrapper.pack(expand=True, fill="both")

        card = tk.Frame(wrapper, bg=PANEL_BG, bd=0, highlightthickness=0)
        card.place(relx=0.5, rely=0.5, anchor="center")

        title = tk.Label(
            card,
            text="Aplicație Activitate Fizică",
            font=("Arial", 24, "bold"),
            bg=PANEL_BG,
            fg=TEXT_FG,
        )
        title.pack(padx=60, pady=(30, 10))

        subt = tk.Label(
            card,
            text="Monitorizează-ți antrenamentele și discută cu antrenorul AI.",
            font=("Arial", 11),
            bg=PANEL_BG,
            fg=TEXT_SUB,
            wraplength=380,
            justify="center"
        )
        subt.pack(padx=30, pady=(0, 20))

        btn_login = tk.Button(
            card,
            text="👤 Login",
            width=20,
            font=("Arial", 11, "bold"),
            bg=BTN_BG,
            fg=BTN_FG,
            activebackground=BTN_BG_HOVER,
            activeforeground=BTN_FG,
            bd=0,
            relief="flat",
            command=lambda: controller.show_frame("PaginaLogin")
        )
        btn_login.pack(pady=10, ipadx=10, ipady=5)

        btn_signup = tk.Button(
            card,
            text="✚ Sign Up",
            width=20,
            font=("Arial", 11, "bold"),
            bg="#34495e",
            fg=BTN_FG,
            activebackground="#2c3e50",
            activeforeground=BTN_FG,
            bd=0,
            relief="flat",
            command=lambda: controller.show_frame("PaginaSignUp")
        )
        btn_signup.pack(pady=(0, 30), ipadx=10, ipady=5)


# ---------------- PAGINA SIGNUP ----------------
class PaginaSignUp(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_MAIN)
        self.controller = controller

        # wrapper centrat (fără pack — pack suprascria zona clickabilă!)
        wrapper = tk.Frame(self, bg=BG_MAIN)
        wrapper.place(relx=0.5, rely=0.5, anchor="center")

        # card
        card = tk.Frame(wrapper, bg=PANEL_BG, bd=0, highlightthickness=0)
        card.pack(padx=40, pady=40)

        tk.Label(
            card,
            text="Creare cont",
            font=("Arial", 22, "bold"),
            bg=PANEL_BG,
            fg=TEXT_FG
        ).pack(pady=(25, 20))

        # Entry fields
        def add_labeled_entry(text):
            tk.Label(card, text=text, bg=PANEL_BG, fg=TEXT_SUB, anchor="w") \
                .pack(anchor="w", padx=25)

        add_labeled_entry("Username")
        self.entry_user = tk.Entry(
            card, bg=ENTRY_BG, fg=ENTRY_FG,
            insertbackground=ENTRY_FG, relief="flat", width=30
        )
        self.entry_user.pack(pady=(0, 15), padx=25, ipady=6, fill="x")

        add_labeled_entry("Parola")
        self.entry_pass = tk.Entry(
            card, show="*", bg=ENTRY_BG, fg=ENTRY_FG,
            insertbackground=ENTRY_FG, relief="flat", width=30
        )
        self.entry_pass.pack(pady=(0, 15), padx=25, ipady=6, fill="x")

        add_labeled_entry("Confirmă parola")
        self.entry_conf = tk.Entry(
            card, show="*", bg=ENTRY_BG, fg=ENTRY_FG,
            insertbackground=ENTRY_FG, relief="flat", width=30
        )
        self.entry_conf.pack(pady=(0, 20), padx=25, ipady=6, fill="x")

        # Creează cont
        tk.Button(
            card,
            text="Creează cont",
            font=("Arial", 11, "bold"),
            bg=BTN_BG,
            fg=BTN_FG,
            activebackground=BTN_BG_HOVER,
            activeforeground=BTN_FG,
            bd=0,
            relief="flat",
            command=self.signup
        ).pack(pady=(0, 15), padx=40, fill="x", ipady=6)

        # Înapoi
        tk.Button(
            card,
            text="⟵ Înapoi",
            font=("Arial", 10, "bold"),
            bg=BTN_SECONDARY_BG,
            fg=BTN_SECONDARY_FG,
            activebackground=BTN_SECONDARY_HOVER,
            activeforeground=BTN_SECONDARY_FG,
            bd=0,
            relief="flat",
            command=lambda: controller.show_frame("PaginaStart")
        ).pack(pady=(0, 20), padx=60, fill="x", ipady=5)

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


# ---------------- PAGINA SUCCES ----------------
class PaginaSucces(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_MAIN)

        wrapper = tk.Frame(self, bg=BG_MAIN)
        wrapper.pack(expand=True, fill="both")

        card = tk.Frame(wrapper, bg=PANEL_BG, bd=0, highlightthickness=0)
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            card,
            text="Cont creat cu succes!",
            fg="#2ecc71",
            bg=PANEL_BG,
            font=("Arial", 20, "bold")
        ).pack(pady=(35, 15), padx=40)

        tk.Button(
            card,
            text="⟵ Înapoi la Start",
            font=("Arial", 11, "bold"),
            bg=BTN_BG,
            fg=BTN_FG,
            activebackground=BTN_BG_HOVER,
            activeforeground=BTN_FG,
            bd=0,
            relief="flat",
            command=lambda: controller.show_frame("PaginaStart")
        ).pack(pady=(10, 30), padx=60, fill="x", ipady=5)


# ---------------- PAGINA LOGIN ----------------
class PaginaLogin(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_MAIN)
        self.controller = controller

        # wrapper centrat
        wrapper = tk.Frame(self, bg=BG_MAIN)
        wrapper.pack(expand=True)

        # card
        card = tk.Frame(wrapper, bg=PANEL_BG, bd=0, highlightthickness=0)
        card.pack(pady=40, padx=40, fill="x")

        # titlu
        tk.Label(
            card,
            text="Autentificare",
            font=("Arial", 22, "bold"),
            bg=PANEL_BG,
            fg=TEXT_FG
        ).pack(pady=(25, 20))

        # USERNAME
        label_user = tk.Label(card, text="Username", bg=PANEL_BG, fg=TEXT_SUB)
        label_user.pack(anchor="w", padx=25)

        self.entry_user = tk.Entry(
            card,
            bg=ENTRY_BG,
            fg=ENTRY_FG,
            insertbackground=ENTRY_FG,
            relief="flat",
            width=30
        )
        self.entry_user.pack(pady=(0, 15), padx=25, ipady=6, fill="x")

        # PAROLA
        label_pass = tk.Label(card, text="Parolă", bg=PANEL_BG, fg=TEXT_SUB)
        label_pass.pack(anchor="w", padx=25)

        self.entry_pass = tk.Entry(
            card,
            bg=ENTRY_BG,
            fg=ENTRY_FG,
            insertbackground=ENTRY_FG,
            show="*",
            relief="flat",
            width=30
        )
        self.entry_pass.pack(pady=(0, 20), padx=25, ipady=6, fill="x")

        # BUTON LOGIN
        tk.Button(
            card,
            text="Login",
            font=("Arial", 11, "bold"),
            bg=BTN_BG,
            fg=BTN_FG,
            activebackground=BTN_BG_HOVER,
            activeforeground=BTN_FG,
            bd=0,
            relief="flat",
            command=self.login
        ).pack(pady=(0, 15), padx=40, fill="x", ipady=6)

        # BUTON ÎNAPOI
        tk.Button(
            card,
            text="⟵ Înapoi",
            font=("Arial", 10, "bold"),
            bg="#555",
            fg=BTN_FG,
            activebackground="#444",
            activeforeground=BTN_FG,
            bd=0,
            relief="flat",
            command=lambda: controller.show_frame("PaginaStart")
        ).pack(pady=(0, 20), padx=60, fill="x", ipady=5)

    # ---------------------------
    #   LOGARE
    # ---------------------------
    def login(self):
        u = self.entry_user.get().strip()
        p = self.entry_pass.get().strip()

        rezultat = self.controller.db.autentifica(u, p)
        if rezultat:
            user_id, username = rezultat
            self.entry_user.delete(0, tk.END)
            self.entry_pass.delete(0, tk.END)
            self.controller.login_user(user_id, username)
        else:
            messagebox.showerror("Eroare", "Date de autentificare invalide!")





# ---------------- PAGINA DASHBOARD ----------------
class PaginaDashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_MAIN)
        self.controller = controller
        self.sesiuni = {}
        self.ferestre_progres = {}

        self.antrenamente = {
            "Piept": ["Bench Press", "Flyers", "Cable Crossovers"],
            "Picioare": ["Squats", "Leg Press", "Calf Raises"],
            "Spate": ["Pull Ups", "Deadlift", "Seated Rows"],
            "Brate": ["Bicep Curl", "Tricep Dips", "Overhead Press"]
        }

        # --------- CHAT AI (sus, full width) ----------
        self.chat_frame = tk.Frame(self, bg=PANEL_BG, bd=0, highlightthickness=0)
        self.chat_frame.pack(fill="x", pady=8, padx=10)

        tk.Label(
            self.chat_frame,
            text="Antrenor AI",
            bg=PANEL_BG,
            fg=TEXT_FG,
            font=("Arial", 11, "bold")
        ).pack(pady=(5, 2), padx=8, anchor="w")

        input_f = tk.Frame(self.chat_frame, bg=PANEL_BG)
        input_f.pack(pady=4, padx=8, fill="x")

        self.chat_entry = tk.Entry(
            input_f,
            width=35,
            bg=ENTRY_BG,
            fg=ENTRY_FG,
            insertbackground=ENTRY_FG,
            relief="flat"
        )
        self.chat_entry.pack(side="left", padx=(0, 6), fill="x", expand=True, ipady=4)
        self.chat_entry.bind("<Return>", lambda e: self.trimite_ai())

        self.btn_trimite = tk.Button(
            input_f,
            text="Trimite",
            bg=BTN_BG,
            fg=BTN_FG,
            activebackground=BTN_BG_HOVER,
            activeforeground=BTN_FG,
            bd=0,
            relief="flat",
            command=self.trimite_ai
        )
        self.btn_trimite.pack(side="left", ipadx=10, ipady=4)

        self.chat_response = tk.Text(
            self.chat_frame,
            height=7,
            width=55,
            state="disabled",
            font=("Arial", 9),
            bg=ENTRY_BG,
            fg=ENTRY_FG,
            relief="flat"
        )
        self.chat_response.pack(pady=(4, 8), padx=8, fill="x")

        # --------- ZONA CONTINUT (jos) ----------
        self.content_frame = tk.Frame(self, bg=BG_MAIN)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

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

    # --- MULTITHREADING CHAT AI ---
    def trimite_ai(self):
        msg = self.chat_entry.get()
        if not msg.strip():
            return

        # mesaj de așteptare
        self.chat_response.config(state="normal")
        self.chat_response.delete("1.0", tk.END)
        self.chat_response.insert(tk.END, "Thinking...")
        self.chat_response.config(state="disabled")

        # blocăm input
        self.chat_entry.config(state="disabled")
        self.btn_trimite.config(state="disabled")

        user_id = self.controller.user_curent["id"]
        try:
            istoric = self.controller.db.get_istoric_text(user_id)
        except AttributeError:
            istoric = []
        active = self.controller.db.exercitii_user(user_id)

        toate_ex = []
        for l in self.antrenamente.values():
            toate_ex.extend(l)

        def thread_task():
            raspuns = self.controller.ai.chat_cu_antrenorul(msg, istoric, active, toate_ex)
            self.after(0, lambda: self.afiseaza_raspuns(raspuns))

        threading.Thread(target=thread_task, daemon=True).start()

    def afiseaza_raspuns(self, raspuns):
        # Afisam raspunsul
        self.chat_response.config(state="normal")
        self.chat_response.delete("1.0", tk.END)
        self.chat_response.insert(tk.END, raspuns)
        self.chat_response.config(state="disabled")

        # REACTIVAM input-ul
        self.chat_entry.config(state="normal")
        self.btn_trimite.config(state="normal")

        # GOLIM ENTRY-UL DUPA RASPUNS
        self.chat_entry.delete(0, tk.END)

        # MUTAM CURSORUL AUTOMAT
        self.chat_entry.focus_set()

    # -------- DASHBOARD EXERCIȚII --------
    def construieste_dashboard(self):
        for w in self.content_frame.winfo_children():
            w.destroy()

        user_id = self.controller.user_curent["id"]
        active = self.controller.db.exercitii_user(user_id)

        header = tk.Label(
            self.content_frame,
            text=f"Utilizator: {self.controller.user_curent['username']}",
            fg=TEXT_SUB,
            bg=BG_MAIN,
            font=("Arial", 11)
        )
        header.pack(pady=(0, 8), anchor="w")

        for cat, exs in self.antrenamente.items():
            tk.Label(
                self.content_frame,
                text=cat,
                font=("Arial", 13, "bold"),
                fg=TEXT_FG,
                bg=BG_MAIN
            ).pack(pady=(8, 4), anchor="w", padx=10)

            for ex in exs:
                row = tk.Frame(self.content_frame, bg=BG_MAIN)
                row.pack(fill="x", padx=20, pady=2)

                tk.Label(
                    row,
                    text=ex,
                    bg=BG_MAIN,
                    fg=TEXT_FG,
                    font=("Arial", 11)
                ).pack(side="left")

                if ex in self.sesiuni:
                    tk.Button(
                        row,
                        text="Vezi progres",
                        command=lambda e=ex: self.vezi_progres(e),
                        bg=BTN_BG,
                        fg=BTN_FG,
                        activebackground=BTN_BG_HOVER,
                        activeforeground=BTN_FG,
                        bd=0,
                        relief="flat"
                    ).pack(side="right", padx=4)

                    tk.Button(
                        row,
                        text="STOP",
                        command=lambda e=ex: self.stop(e),
                        bg="#c0392b",
                        fg=BTN_FG,
                        activebackground="#922b21",
                        activeforeground=BTN_FG,
                        bd=0,
                        relief="flat"
                    ).pack(side="right", padx=4)

                elif ex in active:
                    tk.Button(
                        row,
                        text="⏹️ STOP",
                        command=lambda e=ex: self.stop(e),
                        bg="#c0392b",
                        fg=BTN_FG,
                        activebackground="#922b21",
                        activeforeground=BTN_FG,
                        bd=0,
                        relief="flat"
                    ).pack(side="right", padx=4)

                else:
                    tk.Button(
                        row,
                        text="▶️ START",
                        command=lambda e=ex: self.start(e),
                        bg="#27ae60",
                        fg=BTN_FG,
                        activebackground="#1e8449",
                        activeforeground=BTN_FG,
                        bd=0,
                        relief="flat"
                    ).pack(side="right", padx=4)

        tk.Button(
            self.content_frame,
            text="Delogare",
            command=self.controller.logout_user,
            bg="#e74c3c",
            fg=BTN_FG,
            activebackground="#c0392b",
            activeforeground=BTN_FG,
            bd=0,
            relief="flat",
            font=("Arial", 10, "bold")
        ).pack(pady=20, ipadx=10, ipady=4)

    def start(self, exercitiu):
        if self.sesiuni:
            messagebox.showwarning("Atentie", "Există deja un exercițiu activ.")
            return

        self.sesiuni[exercitiu] = WorkoutSession(exercitiu)
        self.controller.db.adauga_exercitiu(
            self.controller.user_curent["id"], exercitiu
        )
        self.construieste_dashboard()

    def vezi_progres(self, exercitiu):
        sesiune = self.sesiuni.get(exercitiu)
        if not sesiune:
            messagebox.showinfo("Info", "Sesiunea nu este activă local.")
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
        win.configure(bg=BG_MAIN)

        self.ferestre_progres[exercitiu] = win

        def on_win_close():
            if exercitiu in self.ferestre_progres:
                del self.ferestre_progres[exercitiu]
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_win_close)

        lbl_state = tk.Label(win, font=("Arial", 10), bg=BG_MAIN, fg=TEXT_FG)
        lbl_state.pack(pady=4)
        lbl_time = tk.Label(win, font=("Arial", 12), bg=BG_MAIN, fg=TEXT_FG)
        lbl_time.pack(pady=4)
        lbl_reps = tk.Label(win, font=("Arial", 12), bg=BG_MAIN, fg=TEXT_FG)
        lbl_reps.pack(pady=4)
        lbl_sets = tk.Label(win, font=("Arial", 12), bg=BG_MAIN, fg=TEXT_FG)
        lbl_sets.pack(pady=4)
        lbl_cal = tk.Label(win, font=("Arial", 12), bg=BG_MAIN, fg=TEXT_FG)
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
                pw.configure(bg=BG_MAIN)
                tk.Label(
                    pw,
                    text="Pauză! Odihnește-te 1:30",
                    font=("Arial", 12, "bold"),
                    bg=BG_MAIN,
                    fg=TEXT_FG
                ).pack(pady=10)
                l = tk.Label(pw, font=("Arial", 18), bg=BG_MAIN, fg=TEXT_FG)
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
            raspuns = messagebox.askyesno("Stop", "Ești sigur?")
            if not raspuns:
                return

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

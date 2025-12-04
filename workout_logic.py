import time

try:
    import winsound
except ImportError:
    winsound = None

# MET values (estimări standard pe tip de exercițiu)
MET_VALUES = {
    "Bench Press": 6.0,
    "Flyers": 5.5,
    "Cable Crossovers": 5.5,

    "Squats": 8.0,
    "Leg Press": 7.0,
    "Calf Raises": 4.5,

    "Deadlift": 8.5,
    "Pull Ups": 8.0,
    "Seated Rows": 6.0
}


class WorkoutSession:
    def __init__(self, exercitiu, greutate_kg=70):
        self.exercitiu = exercitiu
        self.greutate = greutate_kg

        self.start_time = time.time()
        self.last_update_time = self.start_time

        # timp
        self.total_elapsed = 0.0        # include pauze
        self.active_elapsed = 0.0       # doar timp efectiv de lucru

        # rep / set / pauză
        self.seconds_per_rep = 5        # 1 rep / 5 s
        self.reps_per_set = 12
        self.pause_length = 90          # 1:30 pauză

        self.reps_total = 0
        self.sets = 1                   # primul set în desfășurare

        self.in_pause = False
        self.pause_remaining = 0.0
        self.pause_just_started = False

    # ------------------------------------------------
    # apelat periodic (de UI) pentru a avansa timpul
    # ------------------------------------------------
    def step(self):
        now = time.time()
        dt = now - self.last_update_time
        if dt < 0:
            dt = 0
        self.last_update_time = now

        self.pause_just_started = False
        self.total_elapsed += dt

        if self.in_pause:
            self.pause_remaining -= dt
            if self.pause_remaining <= 0:
                self.pause_remaining = 0
                self.in_pause = False
                self.sets += 1
            return

        # nu suntem în pauză → timp activ + reps
        self.active_elapsed += dt

        new_reps_total = int(self.active_elapsed // self.seconds_per_rep)
        if new_reps_total > self.reps_total:
            self.reps_total = new_reps_total

            # dacă am ajuns la multiplu de 12 → pauză
            if self.reps_total % self.reps_per_set == 0:
                self._start_pause()

    def _start_pause(self):
        self.in_pause = True
        self.pause_remaining = self.pause_length
        self.pause_just_started = True

        # sunet scurt, dacă există winsound (Windows)
        if winsound is not None:
            try:
                winsound.Beep(1000, 400)
            except Exception:
                pass

    # ------------------------------------------------
    # getters folosite în UI + DB
    # ------------------------------------------------
    def start_clock(self):
        return time.strftime("%H:%M:%S", time.localtime(self.start_time))

    def get_duration(self):
        return int(self.total_elapsed)

    def get_reps_total(self):
        return self.reps_total

    def get_sets(self):
        return self.sets

    def get_state(self):
        return "pauză" if self.in_pause else "activ"

    def get_pause_remaining(self):
        return int(self.pause_remaining)

    def calories(self):
        # calorii DOAR pe timp activ, nu și pauză
        met = MET_VALUES.get(self.exercitiu, 5.0)
        durata_ore = self.active_elapsed / 3600
        calorii = met * self.greutate * durata_ore
        return round(calorii, 2)

"""
Advanced Scientific Calculator – GUI (Python / tkinter)
Run:  python calculator.py
Requires Python 3.8+ with tkinter (included in the Python standard library).
On Linux you may need:  sudo apt-get install python3-tk
"""

import math
import re
import tkinter as tk


# ── Helpers ──────────────────────────────────────────────────────────────────

def factorial(n: float) -> float:
    n = round(n)
    if n < 0:
        raise ValueError("Factorial of a negative number is undefined")
    if n > 170:
        return math.inf
    result = 1
    for i in range(2, n + 1):
        result *= i
    return float(result)


def to_rad(value: float, mode: str) -> float:
    if mode == "RAD":
        return value
    if mode == "GRAD":
        return value * math.pi / 200
    return value * math.pi / 180  # DEG


def from_rad(value: float, mode: str) -> float:
    if mode == "RAD":
        return value
    if mode == "GRAD":
        return value * 200 / math.pi
    return value * 180 / math.pi  # DEG


def fmt(val: float) -> str:
    if math.isnan(val):
        return "Error"
    if math.isinf(val):
        return "∞" if val > 0 else "-∞"
    return f"{val:.12g}"


# ── Calculator application ────────────────────────────────────────────────────

class ScientificCalculator(tk.Tk):
    # ── Colour palette ────────────────────────────────────────────────────────
    C_BG       = "#1a1a2e"
    C_DISP     = "#0d0d1a"
    C_BORDER   = "#222240"
    C_NUM      = "#1c1c30"
    C_SCI      = "#0f2040"
    C_OP       = "#1a103a"
    C_EQ       = "#7c3aed"
    C_CLR      = "#3b0a0a"
    C_MEM      = "#0a2a1a"
    C_HOVER_N  = "#252540"
    C_HOVER_S  = "#163060"
    C_HOVER_O  = "#261650"
    C_HOVER_E  = "#6d28d9"
    C_HOVER_C  = "#5a1010"
    C_HOVER_M  = "#0d3d25"
    C_WHITE    = "#e0e0e0"
    C_BLUE     = "#93c5fd"
    C_PURPLE   = "#c4b5fd"
    C_RED      = "#fca5a5"
    C_GREEN    = "#6ee7b7"
    C_GRAY     = "#7c7c9e"
    C_CYAN     = "#67e8f9"
    C_ACCENT   = "#7c3aed"
    C_MEM_IND  = "#a78bfa"

    MAX_DIGITS  = 15
    MAX_HISTORY = 50

    def __init__(self):
        super().__init__()
        self.title("Advanced Scientific Calculator")
        self.resizable(False, False)
        self.configure(bg=self.C_BG)

        # ── Calculator state ──────────────────────────────────────────────────
        self._disp       = "0"
        self._expr       = ""
        self._memory     = 0.0
        self._ans        = 0.0
        self._fresh      = True        # next digit replaces current display
        self._angle_mode = "DEG"       # DEG | RAD | GRAD
        self._power_mode = False       # waiting for exponent of xʸ
        self._history: list[dict]  = []

        # ── StringVars for labels ─────────────────────────────────────────────
        self._sv_disp = tk.StringVar(value="0")
        self._sv_expr = tk.StringVar(value="")
        self._sv_mem  = tk.StringVar(value="")

        self._build_ui()
        self._bind_keys()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        outer = tk.Frame(self, bg=self.C_BG, padx=16, pady=16)
        outer.pack()

        # Title
        tk.Label(outer, text="SCIENTIFIC CALCULATOR",
                 bg=self.C_BG, fg=self.C_GRAY,
                 font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, columnspan=5, pady=(0, 8))

        # Display
        dframe = tk.Frame(outer, bg=self.C_DISP,
                          highlightthickness=1,
                          highlightbackground=self.C_BORDER)
        dframe.grid(row=1, column=0, columnspan=5, sticky="ew",
                    pady=(0, 10), ipadx=12, ipady=8)

        tk.Label(dframe, textvariable=self._sv_expr,
                 bg=self.C_DISP, fg=self.C_GRAY,
                 font=("Segoe UI", 11), anchor="e", width=28
                 ).pack(fill="x", padx=8, pady=(4, 0))

        self._lbl_disp = tk.Label(dframe, textvariable=self._sv_disp,
                                  bg=self.C_DISP, fg=self.C_WHITE,
                                  font=("Segoe UI", 28, "bold"),
                                  anchor="e", width=28)
        self._lbl_disp.pack(fill="x", padx=8)

        tk.Label(dframe, textvariable=self._sv_mem,
                 bg=self.C_DISP, fg=self.C_MEM_IND,
                 font=("Segoe UI", 9), anchor="w", width=28
                 ).pack(fill="x", padx=8, pady=(0, 4))

        # Angle-mode bar
        mbar = tk.Frame(outer, bg=self.C_BG)
        mbar.grid(row=2, column=0, columnspan=5, sticky="ew", pady=(0, 8))

        self._mode_btns: dict[str, tk.Button] = {}
        for m in ("DEG", "RAD", "GRAD"):
            b = tk.Button(mbar, text=m, width=5,
                          command=lambda x=m: self._set_mode(x),
                          font=("Segoe UI", 9, "bold"),
                          relief="flat", cursor="hand2", bd=0)
            b.pack(side="left", padx=2)
            self._mode_btns[m] = b
        self._refresh_mode_bar()

        # History toggle
        tk.Button(mbar, text="History ▾", command=self._toggle_history,
                  bg=self.C_BG, fg=self.C_GRAY,
                  font=("Segoe UI", 9), relief="flat",
                  cursor="hand2", bd=0).pack(side="right", padx=4)

        # Button grid
        self._make_buttons(outer, start_row=3)

        # History frame (hidden until toggled)
        self._hist_frame = tk.Frame(outer, bg=self.C_DISP,
                                    highlightthickness=1,
                                    highlightbackground=self.C_BORDER)

    def _make_buttons(self, parent: tk.Frame, start_row: int):
        """Build the 10-row × 5-column button grid."""
        # fmt: (label, colspan, bg, fg, hover_bg, command)
        layout = [
            # ── Memory ──────────────────────────────────────────────────────
            ("MC",    1, self.C_MEM, self.C_GREEN,  self.C_HOVER_M, self._m_clear),
            ("MR",    1, self.C_MEM, self.C_GREEN,  self.C_HOVER_M, self._m_recall),
            ("M+",    1, self.C_MEM, self.C_GREEN,  self.C_HOVER_M, self._m_add),
            ("M−",    1, self.C_MEM, self.C_GREEN,  self.C_HOVER_M, self._m_sub),
            ("MS",    1, self.C_MEM, self.C_GREEN,  self.C_HOVER_M, self._m_store),
            # ── Trig ────────────────────────────────────────────────────────
            ("sin",   1, self.C_SCI, self.C_BLUE,   self.C_HOVER_S, lambda: self._apply_fn("sin")),
            ("cos",   1, self.C_SCI, self.C_BLUE,   self.C_HOVER_S, lambda: self._apply_fn("cos")),
            ("tan",   1, self.C_SCI, self.C_BLUE,   self.C_HOVER_S, lambda: self._apply_fn("tan")),
            ("sin⁻¹", 1, self.C_SCI, self.C_BLUE,   self.C_HOVER_S, lambda: self._apply_fn("asin")),
            ("cos⁻¹", 1, self.C_SCI, self.C_BLUE,   self.C_HOVER_S, lambda: self._apply_fn("acos")),
            ("tan⁻¹", 1, self.C_SCI, self.C_BLUE,   self.C_HOVER_S, lambda: self._apply_fn("atan")),
            ("log",   1, self.C_SCI, self.C_BLUE,   self.C_HOVER_S, lambda: self._apply_fn("log")),
            ("ln",    1, self.C_SCI, self.C_BLUE,   self.C_HOVER_S, lambda: self._apply_fn("ln")),
            ("log₂",  1, self.C_SCI, self.C_BLUE,   self.C_HOVER_S, lambda: self._apply_fn("log2")),
            ("eˣ",    1, self.C_SCI, self.C_BLUE,   self.C_HOVER_S, lambda: self._apply_fn("exp")),
            # ── Powers / roots ───────────────────────────────────────────────
            ("√x",    1, self.C_SCI, self.C_BLUE,   self.C_HOVER_S, lambda: self._apply_fn("sqrt")),
            ("∛x",    1, self.C_SCI, self.C_BLUE,   self.C_HOVER_S, lambda: self._apply_fn("cbrt")),
            ("x²",    1, self.C_SCI, self.C_BLUE,   self.C_HOVER_S, lambda: self._apply_fn("sq")),
            ("x³",    1, self.C_SCI, self.C_BLUE,   self.C_HOVER_S, lambda: self._apply_fn("cube")),
            ("xʸ",    1, self.C_SCI, self.C_BLUE,   self.C_HOVER_S, self._start_power),
            # ── Misc sci ────────────────────────────────────────────────────
            ("1/x",   1, self.C_SCI, self.C_BLUE,   self.C_HOVER_S, lambda: self._apply_fn("inv")),
            ("|x|",   1, self.C_SCI, self.C_BLUE,   self.C_HOVER_S, lambda: self._apply_fn("abs")),
            ("x!",    1, self.C_SCI, self.C_BLUE,   self.C_HOVER_S, lambda: self._apply_fn("fact")),
            ("π",     1, self.C_SCI, self.C_BLUE,   self.C_HOVER_S, lambda: self._insert_const("pi")),
            ("e",     1, self.C_SCI, self.C_BLUE,   self.C_HOVER_S, lambda: self._insert_const("e")),
            # ── Clear / op ──────────────────────────────────────────────────
            ("AC",    1, self.C_CLR, self.C_RED,    self.C_HOVER_C, self._all_clear),
            ("CE",    1, self.C_CLR, self.C_RED,    self.C_HOVER_C, self._clear_entry),
            ("⌫",     1, self.C_CLR, self.C_RED,    self.C_HOVER_C, self._backspace),
            ("%",     1, self.C_OP,  self.C_PURPLE, self.C_HOVER_O, self._input_pct),
            ("÷",     1, self.C_OP,  self.C_PURPLE, self.C_HOVER_O, lambda: self._input_op("/")),
            # ── Digits ──────────────────────────────────────────────────────
            ("7",     1, self.C_NUM, self.C_WHITE,  self.C_HOVER_N, lambda: self._input_num("7")),
            ("8",     1, self.C_NUM, self.C_WHITE,  self.C_HOVER_N, lambda: self._input_num("8")),
            ("9",     1, self.C_NUM, self.C_WHITE,  self.C_HOVER_N, lambda: self._input_num("9")),
            ("×",     1, self.C_OP,  self.C_PURPLE, self.C_HOVER_O, lambda: self._input_op("*")),
            ("mod",   1, self.C_SCI, self.C_BLUE,   self.C_HOVER_S, lambda: self._input_op("%")),
            ("4",     1, self.C_NUM, self.C_WHITE,  self.C_HOVER_N, lambda: self._input_num("4")),
            ("5",     1, self.C_NUM, self.C_WHITE,  self.C_HOVER_N, lambda: self._input_num("5")),
            ("6",     1, self.C_NUM, self.C_WHITE,  self.C_HOVER_N, lambda: self._input_num("6")),
            ("−",     1, self.C_OP,  self.C_PURPLE, self.C_HOVER_O, lambda: self._input_op("-")),
            ("+/−",   1, self.C_SCI, self.C_BLUE,   self.C_HOVER_S, self._toggle_sign),
            ("1",     1, self.C_NUM, self.C_WHITE,  self.C_HOVER_N, lambda: self._input_num("1")),
            ("2",     1, self.C_NUM, self.C_WHITE,  self.C_HOVER_N, lambda: self._input_num("2")),
            ("3",     1, self.C_NUM, self.C_WHITE,  self.C_HOVER_N, lambda: self._input_num("3")),
            ("+",     1, self.C_OP,  self.C_PURPLE, self.C_HOVER_O, lambda: self._input_op("+")),
            ("ANS",   1, self.C_SCI, self.C_CYAN,   self.C_HOVER_S, self._recall_ans),
            # ── Last row ────────────────────────────────────────────────────
            ("0",     2, self.C_NUM, self.C_WHITE,  self.C_HOVER_N, lambda: self._input_num("0")),
            (".",     1, self.C_NUM, self.C_WHITE,  self.C_HOVER_N, self._input_dot),
            ("(",     1, self.C_SCI, self.C_BLUE,   self.C_HOVER_S, self._open_paren),
            ("=",     1, self.C_EQ,  "#ffffff",     self.C_HOVER_E, self._calculate),
        ]

        col = 0
        row = start_row
        for label, span, bg, fg, hbg, cmd in layout:
            btn = tk.Button(parent, text=label, command=cmd,
                            bg=bg, fg=fg,
                            activebackground=hbg, activeforeground=fg,
                            relief="flat", cursor="hand2",
                            font=("Segoe UI", 11, "bold"),
                            bd=0, padx=0, pady=0)
            btn.grid(row=row, column=col, columnspan=span,
                     sticky="nsew", padx=3, pady=3,
                     ipadx=4, ipady=10)
            btn.bind("<Enter>", lambda e, b=btn, h=hbg: b.configure(bg=h))
            btn.bind("<Leave>", lambda e, b=btn, o=bg:  b.configure(bg=o))

            col += span
            if col >= 5:
                col = 0
                row += 1

        for c in range(5):
            parent.columnconfigure(c, weight=1, minsize=72)

    # ── Display refresh ───────────────────────────────────────────────────────

    def _refresh(self):
        self._sv_disp.set(self._disp)
        self._sv_expr.set(self._expr)
        self._sv_mem.set(f"M: {fmt(self._memory)}" if self._memory != 0 else "")

        # Shrink font for long numbers
        n = len(self._disp)
        size = 14 if n > 18 else 20 if n > 12 else 24 if n > 8 else 28
        self._lbl_disp.configure(font=("Segoe UI", size, "bold"))

    # ── Angle mode ────────────────────────────────────────────────────────────

    def _set_mode(self, mode: str):
        self._angle_mode = mode
        self._refresh_mode_bar()

    def _refresh_mode_bar(self):
        for m, b in self._mode_btns.items():
            b.configure(
                bg=self.C_ACCENT if m == self._angle_mode else self.C_DISP,
                fg="#ffffff" if m == self._angle_mode else self.C_GRAY,
            )

    # ── Digit / operator input ────────────────────────────────────────────────

    def _input_num(self, n: str):
        if self._power_mode:
            self._expr += n
            self._refresh()
            return
        if self._fresh or self._disp == "0":
            self._disp = n
            self._fresh = False
        else:
            if len(self._disp.lstrip("-")) >= self.MAX_DIGITS:
                return
            self._disp += n
        self._refresh()

    def _input_dot(self):
        if self._power_mode:
            return
        if self._fresh:
            self._disp = "0."
            self._fresh = False
        elif "." not in self._disp:
            self._disp += "."
        self._refresh()

    def _input_op(self, op: str):
        self._power_mode = False
        self._expr  = fmt(float(self._disp)) + op
        self._fresh = True
        self._refresh()

    def _input_pct(self):
        self._disp  = fmt(float(self._disp) / 100)
        self._fresh = True
        self._refresh()

    def _toggle_sign(self):
        if self._disp in ("0", "Error"):
            return
        self._disp = self._disp[1:] if self._disp.startswith("-") else "-" + self._disp
        self._refresh()

    def _open_paren(self):
        self._expr  += "("
        self._fresh  = True
        self._refresh()

    def _backspace(self):
        if self._fresh or self._disp == "Error":
            self._disp = "0"
            self._fresh = False
        elif len(self._disp) > 1:
            self._disp = self._disp[:-1]
        else:
            self._disp = "0"
        self._refresh()

    def _clear_entry(self):
        self._disp  = "0"
        self._fresh = False
        self._refresh()

    def _all_clear(self):
        self._disp       = "0"
        self._expr       = ""
        self._fresh      = True
        self._power_mode = False
        self._refresh()

    # ── Scientific functions ──────────────────────────────────────────────────

    def _apply_fn(self, fn: str):
        self._power_mode = False
        v = float(self._disp)
        fn_map = {
            "sin":  lambda x: math.sin(to_rad(x, self._angle_mode)),
            "cos":  lambda x: math.cos(to_rad(x, self._angle_mode)),
            "tan":  lambda x: math.tan(to_rad(x, self._angle_mode)),
            "asin": lambda x: from_rad(math.asin(x), self._angle_mode),
            "acos": lambda x: from_rad(math.acos(x), self._angle_mode),
            "atan": lambda x: from_rad(math.atan(x), self._angle_mode),
            "log":  lambda x: math.log10(x),
            "ln":   lambda x: math.log(x),
            "log2": lambda x: math.log2(x),
            "exp":  lambda x: math.exp(x),
            "sqrt": lambda x: math.sqrt(x),
            # math.cbrt is not available until Python 3.11; use copysign for clarity
            "cbrt": lambda x: math.copysign(abs(x) ** (1 / 3), x),
            "sq":   lambda x: x * x,
            "cube": lambda x: x ** 3,
            "inv":  lambda x: 1 / x,
            "abs":  lambda x: abs(x),
            "fact": lambda x: factorial(x),
        }
        labels = {
            "sin": "sin", "cos": "cos", "tan": "tan",
            "asin": "sin⁻¹", "acos": "cos⁻¹", "atan": "tan⁻¹",
            "log": "log", "ln": "ln", "log2": "log₂", "exp": "eˣ",
            "sqrt": "√", "cbrt": "∛", "sq": "²", "cube": "³",
            "inv": "1/", "abs": "|  |", "fact": "!",
        }
        try:
            r = fn_map[fn](v)
            self._expr = f"{labels[fn]}({fmt(v)}) ="
            self._disp = fmt(r)
            self._ans  = r
        except Exception as exc:
            self._disp = "Error"
            self._expr = str(exc)[:35]
        self._fresh = True
        self._refresh()

    def _start_power(self):
        self._power_mode = True
        self._expr  = fmt(float(self._disp)) + "^"
        self._fresh = True
        self._refresh()

    def _insert_const(self, c: str):
        self._disp  = fmt(math.pi if c == "pi" else math.e)
        self._fresh = True
        self._refresh()

    def _recall_ans(self):
        self._disp  = fmt(self._ans)
        self._fresh = True
        self._refresh()

    # ── Calculate ─────────────────────────────────────────────────────────────

    def _calculate(self):
        try:
            if self._power_mode:
                parts = self._expr.split("^", 1)
                base  = float(parts[0])
                exp   = float(self._disp)
                r     = math.pow(base, exp)
                estr  = f"{fmt(base)} ^ {fmt(exp)} ="
                self._push_history(estr, fmt(r))
                self._expr = estr
                self._disp = fmt(r)
                self._ans  = r
                self._power_mode = False
                self._fresh = True
                self._refresh()
                return

            m = re.match(r"^(-?[\d.]+(?:e[+\-]?\d+)?)([+\-*/%])$",
                         self._expr)
            if not m:
                self._ans = float(self._disp)
                self._refresh()
                return

            a  = float(m.group(1))
            op = m.group(2).strip()
            b  = float(self._disp)
            ops = {
                "+": lambda x, y: x + y,
                "-": lambda x, y: x - y,
                "*": lambda x, y: x * y,
                "/": lambda x, y: x / y if y != 0 else (math.inf if x >= 0 else -math.inf),
                "%": lambda x, y: x % y,
            }
            r    = ops[op](a, b)
            sym  = {"+": "+", "-": "−", "*": "×", "/": "÷", "%": "mod"}
            estr = f"{fmt(a)} {sym.get(op, op)} {fmt(b)} ="
            self._push_history(estr, fmt(r))
            self._expr  = estr
            self._disp  = fmt(r)
            self._ans   = r
            self._fresh = True
        except Exception as exc:
            self._disp  = "Error"
            self._expr  = str(exc)[:35]
            self._fresh = True
        self._refresh()

    # ── Memory ────────────────────────────────────────────────────────────────

    def _m_store(self):
        self._memory = float(self._disp)
        self._refresh()

    def _m_recall(self):
        self._disp  = fmt(self._memory)
        self._fresh = True
        self._refresh()

    def _m_add(self):
        self._memory += float(self._disp)
        self._refresh()

    def _m_sub(self):
        self._memory -= float(self._disp)
        self._refresh()

    def _m_clear(self):
        self._memory = 0.0
        self._refresh()

    # ── History ───────────────────────────────────────────────────────────────

    def _push_history(self, expr: str, result: str):
        self._history.insert(0, {"expr": expr, "result": result})
        while len(self._history) > self.MAX_HISTORY:
            self._history.pop()
        self._render_history()

    def _render_history(self):
        for w in self._hist_frame.winfo_children():
            w.destroy()

        tk.Label(self._hist_frame, text="CALCULATION HISTORY",
                 bg=self.C_DISP, fg=self.C_GRAY,
                 font=("Segoe UI", 9, "bold")).pack(
            fill="x", padx=8, pady=(6, 2))

        if not self._history:
            tk.Label(self._hist_frame, text="No history yet",
                     bg=self.C_DISP, fg=self.C_GRAY,
                     font=("Segoe UI", 10)).pack(pady=10)
            return

        canvas = tk.Canvas(self._hist_frame, bg=self.C_DISP,
                           highlightthickness=0, height=160)
        sb = tk.Scrollbar(self._hist_frame, orient="vertical",
                          command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=self.C_DISP)
        canvas.create_window((0, 0), window=inner, anchor="nw")

        for entry in self._history:
            row = tk.Frame(inner, bg=self.C_DISP, cursor="hand2")
            row.pack(fill="x", padx=4, pady=1)
            r_val = entry["result"]
            row.bind("<Button-1>", lambda _e, rv=r_val: self._use_history(rv))

            tk.Label(row, text=entry["expr"],
                     bg=self.C_DISP, fg=self.C_GRAY,
                     font=("Segoe UI", 9), anchor="w").pack(fill="x")
            tk.Label(row, text=entry["result"],
                     bg=self.C_DISP, fg=self.C_WHITE,
                     font=("Segoe UI", 12, "bold"), anchor="e").pack(fill="x")
            tk.Frame(row, bg=self.C_BORDER, height=1).pack(fill="x")

        inner.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    def _use_history(self, result: str):
        self._disp  = result
        self._fresh = True
        self._refresh()

    def _toggle_history(self):
        if self._hist_frame.winfo_ismapped():
            self._hist_frame.grid_forget()
        else:
            self._render_history()
            self._hist_frame.grid(row=100, column=0, columnspan=5,
                                  sticky="ew", pady=(8, 0))

    # ── Keyboard ──────────────────────────────────────────────────────────────

    def _bind_keys(self):
        self.bind("<Key>", self._on_key)
        self.focus_set()

    def _on_key(self, event: tk.Event):
        k, c = event.keysym, event.char
        if c.isdigit():
            self._input_num(c)
        elif c == ".":
            self._input_dot()
        elif c in ("+", "-", "*", "/", "%"):
            self._input_op(c)
        elif k in ("Return", "KP_Enter"):
            self._calculate()
        elif k == "BackSpace":
            self._backspace()
        elif k == "Escape":
            self._all_clear()
        elif k == "Delete":
            self._clear_entry()


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = ScientificCalculator()
    app.mainloop()

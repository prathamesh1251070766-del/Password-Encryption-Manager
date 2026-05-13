# =============================================================================
# login.py  — FIXED VERSION
# Purpose: Login and master password setup window
# Fix: Rewrote placeholder logic, fixed password masking conflicts
# =============================================================================

import tkinter as tk
from tkinter import messagebox
import database


class LoginWindow:
    """
    Login window — handles first-time setup and returning user login.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Secure Password Manager — Login")
        self.root.geometry("460x560")
        self.root.resizable(False, False)
        self._center_window(460, 560)

        # ── Colour palette ──────────────────────────────────────────────────
        self.C = {
            "bg":        "#1a1a2e",
            "card":      "#16213e",
            "blue":      "#0f3460",
            "accent":    "#e94560",
            "white":     "#eaeaea",
            "gray":      "#8888a0",
            "entry_bg":  "#0d2137",
            "success":   "#4CAF50",
            "warning":   "#FF9800",
            "border":    "#1e3a5f",
        }

        self.root.configure(bg=self.C["bg"])

        # Failed login counter
        self.failed_attempts = 0

        # Initialise DB tables
        database.initialize_database()

        # Choose which screen to show
        self._build_ui()

    # ──────────────────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────────────────

    def _center_window(self, w, h):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _clear(self):
        """Destroy every child widget (used when switching screens)."""
        for widget in self.root.winfo_children():
            widget.destroy()

    # ──────────────────────────────────────────────────────────────────────
    # Router
    # ──────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        if database.is_master_password_set():
            self._build_login_screen()
        else:
            self._build_setup_screen()

    # ──────────────────────────────────────────────────────────────────────
    # Reusable widget builders
    # ──────────────────────────────────────────────────────────────────────

    def _section_label(self, parent, text):
        """Small bold label above an entry field."""
        tk.Label(
            parent,
            text=text,
            font=("Segoe UI", 10, "bold"),
            bg=self.C["card"],
            fg=self.C["white"],
            anchor="w",
        ).pack(fill="x", padx=30, pady=(12, 2))

    def _make_password_row(self, parent, placeholder: str):
        """
        Return (frame, entry, toggle_button).

        The entry starts with show="" so the placeholder is readable.
        show is set to "•" only after the user starts typing real text.
        """
        row = tk.Frame(parent, bg=self.C["entry_bg"])
        row.pack(fill="x", padx=30, pady=(0, 4))

        entry = tk.Entry(
            row,
            font=("Segoe UI", 11),
            bg=self.C["entry_bg"],
            fg=self.C["gray"],            # gray = placeholder colour
            insertbackground=self.C["white"],
            relief="flat",
            bd=8,
            show="",                       # ← plain text so placeholder shows
        )
        entry.pack(side="left", fill="x", expand=True, ipady=6)
        entry.insert(0, placeholder)

        toggle_btn = tk.Button(
            row,
            text="👁",
            font=("Segoe UI", 10),
            bg=self.C["entry_bg"],
            fg=self.C["gray"],
            activebackground=self.C["entry_bg"],
            relief="flat",
            cursor="hand2",
            bd=0,
            padx=6,
        )
        toggle_btn.pack(side="right", padx=(0, 4))

        # ── bind focus events ───────────────────────────────────────────
        def on_focus_in(event, e=entry, ph=placeholder):
            if e.get() == ph:
                e.delete(0, tk.END)
                e.config(fg=self.C["white"], show="•")

        def on_focus_out(event, e=entry, ph=placeholder):
            if e.get() == "":
                e.config(show="")          # ← clear masking BEFORE inserting
                e.insert(0, ph)
                e.config(fg=self.C["gray"])
                toggle_btn.config(text="👁")

        entry.bind("<FocusIn>",  on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

        # ── toggle show / hide ──────────────────────────────────────────
        def toggle(e=entry, b=toggle_btn, ph=placeholder):
            # Don't toggle if placeholder is showing
            if e.get() == ph and e.cget("show") == "":
                return
            if e.cget("show") == "•":
                e.config(show="")
                b.config(text="🙈")
            else:
                e.config(show="•")
                b.config(text="👁")

        toggle_btn.config(command=toggle)

        return row, entry, toggle_btn

    def _styled_button(self, parent, text, command, bg=None):
        bg = bg or self.C["accent"]
        btn = tk.Button(
            parent,
            text=text,
            font=("Segoe UI", 11, "bold"),
            bg=bg,
            fg="white",
            activebackground=bg,
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=10,
            command=command,
        )
        btn.pack(fill="x", padx=30, pady=(14, 4))

        dark = self._darken(bg)
        btn.bind("<Enter>", lambda e: btn.config(bg=dark))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))
        return btn

    @staticmethod
    def _darken(hex_color: str) -> str:
        """Return a slightly darker version of a hex colour."""
        hex_color = hex_color.lstrip("#")
        r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r, g, b = max(0, r-30), max(0, g-30), max(0, b-30)
        return f"#{r:02x}{g:02x}{b:02x}"

    # ──────────────────────────────────────────────────────────────────────
    # SETUP SCREEN  (first-time use)
    # ──────────────────────────────────────────────────────────────────────

    def _build_setup_screen(self):
        self._clear()

        bg  = self.C["bg"]
        card = self.C["card"]

        outer = tk.Frame(self.root, bg=bg)
        outer.pack(fill="both", expand=True)

        # ── hero ────────────────────────────────────────────────────────
        hero = tk.Frame(outer, bg=bg)
        hero.pack(pady=(28, 0))

        tk.Label(hero, text="🔐", font=("Segoe UI Emoji", 46),
                 bg=bg).pack()
        tk.Label(hero, text="Password Manager",
                 font=("Segoe UI", 20, "bold"),
                 bg=bg, fg=self.C["white"]).pack(pady=(4, 0))
        tk.Label(hero, text="Your credentials, encrypted & safe",
                 font=("Segoe UI", 9),
                 bg=bg, fg=self.C["gray"]).pack()

        # ── card ─────────────────────────────────────────────────────────
        card_frame = tk.Frame(outer, bg=card)
        card_frame.pack(fill="x", padx=30, pady=22)

        tk.Label(card_frame, text="Create Master Password",
                 font=("Segoe UI", 14, "bold"),
                 bg=card, fg=self.C["accent"]).pack(pady=(18, 2))

        tk.Label(
            card_frame,
            text="This password protects your entire vault.\n"
                 "Write it down — it cannot be recovered!",
            font=("Segoe UI", 9),
            bg=card, fg=self.C["gray"],
            justify="center",
        ).pack(pady=(0, 10))

        # ── password fields ──────────────────────────────────────────────
        self._section_label(card_frame, "Master Password")
        _, self._setup_pw, _ = self._make_password_row(
            card_frame, "Enter a strong password…"
        )

        self._section_label(card_frame, "Confirm Password")
        _, self._setup_cf, _ = self._make_password_row(
            card_frame, "Re-enter the same password…"
        )

        # ── create button ────────────────────────────────────────────────
        self._styled_button(
            card_frame,
            "✅   Create Master Password",
            self._handle_setup,
        )

        tk.Frame(card_frame, bg=card, height=6).pack()   # bottom padding

        # ── warning note ─────────────────────────────────────────────────
        tk.Label(
            outer,
            text="⚠  Never share your master password with anyone.",
            font=("Segoe UI", 9),
            bg=bg, fg=self.C["warning"],
        ).pack(pady=(0, 10))

    # ──────────────────────────────────────────────────────────────────────
    # LOGIN SCREEN  (returning user)
    # ──────────────────────────────────────────────────────────────────────

    def _build_login_screen(self):
        self._clear()

        bg   = self.C["bg"]
        card = self.C["card"]

        outer = tk.Frame(self.root, bg=bg)
        outer.pack(fill="both", expand=True)

        # ── hero ────────────────────────────────────────────────────────
        hero = tk.Frame(outer, bg=bg)
        hero.pack(pady=(40, 0))

        tk.Label(hero, text="🔐", font=("Segoe UI Emoji", 52),
                 bg=bg).pack()
        tk.Label(hero, text="Welcome Back",
                 font=("Segoe UI", 22, "bold"),
                 bg=bg, fg=self.C["white"]).pack(pady=(8, 0))
        tk.Label(hero, text="Enter your master password to unlock your vault",
                 font=("Segoe UI", 9),
                 bg=bg, fg=self.C["gray"]).pack()

        # ── card ─────────────────────────────────────────────────────────
        card_frame = tk.Frame(outer, bg=card)
        card_frame.pack(fill="x", padx=30, pady=30)

        self._section_label(card_frame, "Master Password")
        _, self._login_pw, _ = self._make_password_row(
            card_frame, "Enter your master password…"
        )

        # Allow Enter key to submit
        self._login_pw.bind("<Return>", lambda e: self._handle_login())

        self._styled_button(card_frame, "🔓   Unlock Vault", self._handle_login)

        tk.Frame(card_frame, bg=card, height=6).pack()

        # ── failed-attempt label ─────────────────────────────────────────
        self._attempt_lbl = tk.Label(
            outer,
            text="",
            font=("Segoe UI", 9),
            bg=bg, fg=self.C["accent"],
        )
        self._attempt_lbl.pack()

    # ──────────────────────────────────────────────────────────────────────
    # Event handlers
    # ──────────────────────────────────────────────────────────────────────

    def _handle_setup(self):
        """Validate inputs and create the master password."""
        pw = self._setup_pw.get().strip()
        cf = self._setup_cf.get().strip()

        PLACEHOLDER_PW = "Enter a strong password…"
        PLACEHOLDER_CF = "Re-enter the same password…"

        if not pw or pw == PLACEHOLDER_PW:
            messagebox.showwarning("Empty Field",
                                   "Please enter a master password.")
            self._setup_pw.focus_set()
            return

        if not cf or cf == PLACEHOLDER_CF:
            messagebox.showwarning("Empty Field",
                                   "Please confirm your master password.")
            self._setup_cf.focus_set()
            return

        if len(pw) < 6:
            messagebox.showwarning("Too Short",
                                   "Master password must be at least 6 characters.")
            return

        if pw != cf:
            messagebox.showerror("Mismatch",
                                  "Passwords do not match. Please try again.")
            self._setup_cf.delete(0, tk.END)
            self._setup_cf.focus_set()
            return

        if database.set_master_password(pw):
            messagebox.showinfo("Success 🎉",
                                "Master password created!\n"
                                "You can now save your credentials securely.")
            self._open_dashboard()
        else:
            messagebox.showerror("Error",
                                  "Could not save master password. Please try again.")

    def _handle_login(self):
        """Verify the entered master password."""
        pw = self._login_pw.get().strip()
        PLACEHOLDER = "Enter your master password…"

        if not pw or pw == PLACEHOLDER:
            messagebox.showwarning("Empty Field",
                                   "Please enter your master password.")
            self._login_pw.focus_set()
            return

        if database.verify_master_password(pw):
            self._open_dashboard()
        else:
            self.failed_attempts += 1
            self._login_pw.delete(0, tk.END)

            if self.failed_attempts >= 3:
                self._attempt_lbl.config(
                    text=f"⚠  {self.failed_attempts} failed attempts — check CAPS LOCK"
                )

            messagebox.showerror("Wrong Password ❌",
                                  "Incorrect master password.\n\n"
                                  "Tip: check that CAPS LOCK is off.")

    def _open_dashboard(self):
        """Hide login window and open the dashboard."""
        from dashboard import DashboardWindow

        self.root.withdraw()

        dash_root = tk.Toplevel(self.root)
        dash_root.protocol("WM_DELETE_WINDOW",
                           lambda: self._on_dash_close(dash_root))
        DashboardWindow(dash_root, self.root)

    def _on_dash_close(self, dash_root):
        dash_root.destroy()
        self.root.destroy()
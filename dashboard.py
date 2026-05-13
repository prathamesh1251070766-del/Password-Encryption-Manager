# =============================================================================
# dashboard.py  — FIXED VERSION
# Purpose: Main dashboard — full credential management UI
# Fix: Corrected placeholder logic in all entry widgets
# =============================================================================

import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
import database
import encryption
from password_generator import generate_password, check_password_strength


class DashboardWindow:
    """Main dashboard window for managing credentials."""

    def __init__(self, root, login_root=None):
        self.root       = root
        self.login_root = login_root

        self.root.title("Secure Password Manager — Dashboard")
        self.root.geometry("1100x700")
        self.root.minsize(920, 600)
        self._center_window(1100, 700)

        # ── colour palette ───────────────────────────────────────────────
        self.C = {
            "bg":         "#1a1a2e",
            "card":       "#16213e",
            "blue":       "#0f3460",
            "accent":     "#e94560",
            "white":      "#eaeaea",
            "gray":       "#8888a0",
            "entry_bg":   "#0d2137",
            "success":    "#4CAF50",
            "warning":    "#FF9800",
            "danger":     "#f44336",
            "border":     "#1e3a5f",
            "sidebar":    "#12192c",
            "row_odd":    "#16213e",
            "row_even":   "#1a2744",
            "row_sel":    "#0f3460",
        }

        self.root.configure(bg=self.C["bg"])

        # State
        self.selected_id  = None
        self.edit_mode    = False
        self._pw_visible  = False   # table row password visibility

        self._configure_ttk_styles()
        self._build_ui()
        self._load_credentials()

    # ──────────────────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────────────────

    def _center_window(self, w, h):
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _configure_ttk_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(
            "Vault.Treeview",
            background=self.C["row_even"],
            foreground=self.C["white"],
            rowheight=36,
            fieldbackground=self.C["row_even"],
            borderwidth=0,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Vault.Treeview.Heading",
            background=self.C["blue"],
            foreground=self.C["white"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
        )
        style.map(
            "Vault.Treeview",
            background=[("selected", self.C["row_sel"])],
            foreground=[("selected", self.C["white"])],
        )

    # ──────────────────────────────────────────────────────────────────────
    # ENTRY FIELD HELPERS  (fixed placeholder logic)
    # ──────────────────────────────────────────────────────────────────────

    def _plain_entry(self, parent, placeholder: str, **kw):
        """
        Regular (non-password) entry with placeholder behaviour.
        Returns the Entry widget.
        """
        C = self.C
        entry = tk.Entry(
            parent,
            font=("Segoe UI", 11),
            bg=C["entry_bg"],
            fg=C["gray"],
            insertbackground=C["white"],
            relief="flat",
            bd=8,
            **kw,
        )
        entry.insert(0, placeholder)

        def _in(e):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(fg=C["white"])

        def _out(e):
            if entry.get() == "":
                entry.insert(0, placeholder)
                entry.config(fg=C["gray"])

        entry.bind("<FocusIn>",  _in)
        entry.bind("<FocusOut>", _out)
        return entry

    def _password_entry(self, parent, placeholder: str):
        """
        Password entry with show/hide toggle.
        Returns (frame, entry, toggle_button).

        Key fix: entry starts with show="" so placeholder is visible.
        show is switched to "•" only when real text is entered.
        """
        C = self.C
        frame = tk.Frame(parent, bg=C["entry_bg"])

        entry = tk.Entry(
            frame,
            font=("Segoe UI", 11),
            bg=C["entry_bg"],
            fg=C["gray"],
            insertbackground=C["white"],
            relief="flat",
            bd=8,
            show="",          # ← plain so placeholder readable
        )
        entry.pack(side="left", fill="x", expand=True, ipady=6)
        entry.insert(0, placeholder)

        btn = tk.Button(
            frame,
            text="👁",
            font=("Segoe UI", 10),
            bg=C["entry_bg"],
            fg=C["gray"],
            activebackground=C["entry_bg"],
            relief="flat",
            cursor="hand2",
            bd=0,
            padx=6,
        )
        btn.pack(side="right", padx=(0, 4))

        def _in(e):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(fg=C["white"], show="•")
                btn.config(text="👁")

        def _out(e):
            if entry.get() == "":
                entry.config(show="")       # remove masking FIRST
                entry.insert(0, placeholder)
                entry.config(fg=C["gray"])
                btn.config(text="👁")

        entry.bind("<FocusIn>",  _in)
        entry.bind("<FocusOut>", _out)

        def _toggle():
            if entry.get() == placeholder and entry.cget("show") == "":
                return                       # don't toggle placeholder
            if entry.cget("show") == "•":
                entry.config(show="")
                btn.config(text="🙈")
            else:
                entry.config(show="•")
                btn.config(text="👁")

        btn.config(command=_toggle)
        return frame, entry, btn

    # ──────────────────────────────────────────────────────────────────────
    # UI BUILDERS
    # ──────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_header()

        body = tk.Frame(self.root, bg=self.C["bg"])
        body.pack(fill="both", expand=True)

        self._build_left_panel(body)
        self._build_right_panel(body)
        self._build_status_bar()

    # ── HEADER ────────────────────────────────────────────────────────────

    def _build_header(self):
        hdr = tk.Frame(self.root, bg=self.C["blue"], height=62)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        tk.Label(
            hdr,
            text="🔐  Secure Password Manager",
            font=("Segoe UI", 15, "bold"),
            bg=self.C["blue"], fg=self.C["white"],
        ).pack(side="left", padx=20, pady=14)

        # Lock button
        lock_btn = tk.Button(
            hdr,
            text="🔒  Lock",
            font=("Segoe UI", 10, "bold"),
            bg=self.C["accent"], fg="white",
            activebackground="#c73652",
            relief="flat", cursor="hand2",
            padx=12, pady=5,
            command=self._lock_vault,
        )
        lock_btn.pack(side="right", padx=16, pady=12)

        self._count_lbl = tk.Label(
            hdr, text="0 passwords",
            font=("Segoe UI", 10),
            bg=self.C["blue"], fg=self.C["gray"],
        )
        self._count_lbl.pack(side="right", padx=12)

    # ── LEFT PANEL (form) ─────────────────────────────────────────────────

    def _build_left_panel(self, parent):
        sidebar = tk.Frame(parent, bg=self.C["sidebar"], width=340)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Make sidebar scrollable
        canvas = tk.Canvas(sidebar, bg=self.C["sidebar"],
                           highlightthickness=0)
        vsb = ttk.Scrollbar(sidebar, orient="vertical",
                             command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        inner = tk.Frame(canvas, bg=self.C["sidebar"])
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _resize(e):
            canvas.itemconfig(win_id, width=canvas.winfo_width())
        canvas.bind("<Configure>", _resize)
        inner.bind("<Configure>",
                   lambda e: canvas.configure(
                       scrollregion=canvas.bbox("all")))

        self._build_form(inner)

    def _build_form(self, parent):
        C  = self.C
        sb = C["sidebar"]

        def lbl(text):
            tk.Label(parent, text=text,
                     font=("Segoe UI", 10, "bold"),
                     bg=sb, fg=C["white"],
                     anchor="w").pack(fill="x", padx=20, pady=(14, 3))

        # ── title ────────────────────────────────────────────────────────
        self._form_title = tk.Label(
            parent,
            text="➕  Add New Credential",
            font=("Segoe UI", 13, "bold"),
            bg=sb, fg=C["accent"],
        )
        self._form_title.pack(padx=20, pady=(22, 4), anchor="w")
        tk.Frame(parent, bg=C["border"], height=1).pack(fill="x",
                                                        padx=20, pady=4)

        # ── website ───────────────────────────────────────────────────────
        lbl("🌐  Website / App")
        self._web_entry = self._plain_entry(parent, "e.g. Google, Netflix…")
        self._web_entry.pack(fill="x", padx=20, ipady=7)

        # ── username ──────────────────────────────────────────────────────
        lbl("👤  Username / Email")
        self._user_entry = self._plain_entry(parent, "e.g. user@email.com")
        self._user_entry.pack(fill="x", padx=20, ipady=7)

        # ── password ──────────────────────────────────────────────────────
        lbl("🔑  Password")
        pw_frame, self._pw_entry, self._pw_btn = self._password_entry(
            parent, "Enter or generate a password…"
        )
        pw_frame.pack(fill="x", padx=20)

        # Strength indicator
        self._strength_lbl = tk.Label(
            parent, text="",
            font=("Segoe UI", 9),
            bg=sb, fg=C["gray"],
        )
        self._strength_lbl.pack(padx=20, pady=(3, 0), anchor="w")
        self._pw_entry.bind("<KeyRelease>", self._update_strength)

        # ── generator ─────────────────────────────────────────────────────
        lbl("🎲  Password Generator")

        # Length row
        len_row = tk.Frame(parent, bg=sb)
        len_row.pack(fill="x", padx=20, pady=(0, 4))

        tk.Label(len_row, text="Length:",
                 font=("Segoe UI", 9),
                 bg=sb, fg=C["gray"]).pack(side="left")

        self._gen_len = tk.IntVar(value=16)
        self._len_disp = tk.Label(len_row, text="16",
                                  font=("Segoe UI", 9, "bold"),
                                  bg=sb, fg=C["accent"])
        self._len_disp.pack(side="right")

        slider = ttk.Scale(len_row, from_=8, to=32,
                           orient="horizontal",
                           variable=self._gen_len,
                           command=lambda v:
                               self._len_disp.config(text=str(int(float(v)))))
        slider.pack(side="left", fill="x", expand=True, padx=8)

        # Options row
        self._use_upper   = tk.BooleanVar(value=True)
        self._use_lower   = tk.BooleanVar(value=True)
        self._use_digits  = tk.BooleanVar(value=True)
        self._use_symbols = tk.BooleanVar(value=True)

        opts = tk.Frame(parent, bg=sb)
        opts.pack(fill="x", padx=20, pady=(0, 6))

        chk_cfg = dict(bg=sb, fg=C["gray"], selectcolor=C["blue"],
                       font=("Segoe UI", 9), relief="flat",
                       activebackground=sb, cursor="hand2")

        left_col  = tk.Frame(opts, bg=sb)
        right_col = tk.Frame(opts, bg=sb)
        left_col.pack(side="left")
        right_col.pack(side="left", padx=10)

        tk.Checkbutton(left_col,  text="A–Z Uppercase",
                       variable=self._use_upper,   **chk_cfg).pack(anchor="w")
        tk.Checkbutton(left_col,  text="a–z Lowercase",
                       variable=self._use_lower,   **chk_cfg).pack(anchor="w")
        tk.Checkbutton(right_col, text="0–9 Numbers",
                       variable=self._use_digits,  **chk_cfg).pack(anchor="w")
        tk.Checkbutton(right_col, text="!@# Symbols",
                       variable=self._use_symbols, **chk_cfg).pack(anchor="w")

        # Generate button
        gen_btn = tk.Button(
            parent,
            text="🎲  Generate Password",
            font=("Segoe UI", 10, "bold"),
            bg=C["blue"], fg=C["white"],
            activebackground="#1a4a80",
            relief="flat", cursor="hand2",
            padx=10, pady=8,
            command=self._generate_password,
        )
        gen_btn.pack(fill="x", padx=20, pady=(2, 8))

        # ── divider ───────────────────────────────────────────────────────
        tk.Frame(parent, bg=C["border"], height=1).pack(fill="x",
                                                        padx=20, pady=8)

        # ── save button ───────────────────────────────────────────────────
        self._save_btn = tk.Button(
            parent,
            text="💾  Save Credential",
            font=("Segoe UI", 11, "bold"),
            bg=C["success"], fg="white",
            activebackground="#388E3C",
            relief="flat", cursor="hand2",
            padx=10, pady=10,
            command=self._save_credential,
        )
        self._save_btn.pack(fill="x", padx=20, pady=(0, 6))

        # ── clear button ──────────────────────────────────────────────────
        tk.Button(
            parent,
            text="🗑  Clear Fields",
            font=("Segoe UI", 10),
            bg=C["card"], fg=C["gray"],
            activebackground=C["card"],
            relief="flat", cursor="hand2",
            padx=10, pady=8,
            command=self._clear_form,
        ).pack(fill="x", padx=20, pady=(0, 20))

    # ── RIGHT PANEL (table) ───────────────────────────────────────────────

    def _build_right_panel(self, parent):
        right = tk.Frame(parent, bg=self.C["bg"])
        right.pack(side="right", fill="both", expand=True)

        self._build_search_bar(right)
        self._build_table(right)
        self._build_action_buttons(right)

    def _build_search_bar(self, parent):
        C   = self.C
        bar = tk.Frame(parent, bg=C["card"])
        bar.pack(fill="x", padx=18, pady=(14, 6))

        tk.Label(bar, text="🔍", font=("Segoe UI Emoji", 13),
                 bg=C["card"], fg=C["gray"]).pack(side="left", padx=(10, 0))

        self._search_var = tk.StringVar()
        PLACEHOLDER = "Search by website or username…"

        self._search_entry = tk.Entry(
            bar,
            textvariable=self._search_var,
            font=("Segoe UI", 11),
            bg=C["card"], fg=C["gray"],
            insertbackground=C["white"],
            relief="flat", bd=8,
        )
        self._search_entry.pack(side="left", fill="x", expand=True, ipady=8)
        self._search_entry.insert(0, PLACEHOLDER)

        def _sin(e):
            if self._search_entry.get() == PLACEHOLDER:
                self._search_entry.delete(0, tk.END)
                self._search_entry.config(fg=C["white"])

        def _sout(e):
            if self._search_entry.get() == "":
                self._search_entry.insert(0, PLACEHOLDER)
                self._search_entry.config(fg=C["gray"])

        self._search_entry.bind("<FocusIn>",  _sin)
        self._search_entry.bind("<FocusOut>", _sout)
        self._search_var.trace("w", self._on_search)

        tk.Button(bar, text="✕", font=("Segoe UI", 11),
                  bg=C["card"], fg=C["gray"],
                  relief="flat", cursor="hand2", padx=10,
                  command=self._clear_search).pack(side="right")

    def _build_table(self, parent):
        C     = self.C
        frame = tk.Frame(parent, bg=C["bg"])
        frame.pack(fill="both", expand=True, padx=18, pady=(0, 6))

        cols = ("id", "website", "username", "password", "created")
        self._table = ttk.Treeview(frame, columns=cols,
                                   show="headings",
                                   style="Vault.Treeview",
                                   selectmode="browse")

        col_cfg = {
            "id":       ("ID",          50,  "center"),
            "website":  ("🌐 Website",   200, "w"),
            "username": ("👤 Username",  210, "w"),
            "password": ("🔑 Password",  200, "w"),
            "created":  ("📅 Created",   130, "center"),
        }
        for col, (heading, width, anchor) in col_cfg.items():
            self._table.heading(col, text=heading,
                                command=lambda c=col: self._sort(c))
            self._table.column(col, width=width, anchor=anchor, minwidth=40)

        self._table.tag_configure("odd",  background=C["row_odd"])
        self._table.tag_configure("even", background=C["row_even"])

        vsb = ttk.Scrollbar(frame, orient="vertical",
                             command=self._table.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal",
                             command=self._table.xview)
        self._table.configure(yscrollcommand=vsb.set,
                              xscrollcommand=hsb.set)

        self._table.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        self._table.bind("<<TreeviewSelect>>", self._on_select)
        self._table.bind("<Double-1>",         self._on_double_click)

        self._sort_col = None
        self._sort_rev = False

    def _build_action_buttons(self, parent):
        C   = self.C
        row = tk.Frame(parent, bg=C["bg"])
        row.pack(fill="x", padx=18, pady=(0, 10))

        def btn(text, cmd, bg, side="left", padx=(0, 8)):
            b = tk.Button(row, text=text,
                          font=("Segoe UI", 10, "bold"),
                          bg=bg, fg="white",
                          activebackground=bg,
                          relief="flat", cursor="hand2",
                          padx=14, pady=8,
                          command=cmd)
            b.pack(side=side, padx=padx)
            return b

        btn("📋  Copy Password",  self._copy_password,  C["blue"])
        btn("👤  Copy Username",  self._copy_username,  C["card"])
        self._show_pw_btn = btn(
            "👁  Show Password",  self._toggle_table_pw, C["card"])
        btn("✏️  Edit",           self._edit_credential, C["warning"])
        btn("🗑️  Delete",         self._delete_credential,
            C["danger"], side="right", padx=(0, 0))
        btn("🔄  Refresh",        self._load_credentials,
            C["card"], side="right", padx=(0, 8))

    # ── STATUS BAR ────────────────────────────────────────────────────────

    def _build_status_bar(self):
        C   = self.C
        bar = tk.Frame(self.root, bg=C["blue"], height=28)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        self._status_lbl = tk.Label(
            bar, text="✅  Ready",
            font=("Segoe UI", 9),
            bg=C["blue"], fg=C["gray"],
        )
        self._status_lbl.pack(side="left", padx=14, pady=4)

        tk.Label(
            bar,
            text="🔐  All passwords encrypted with AES-128 (Fernet)",
            font=("Segoe UI", 9),
            bg=C["blue"], fg=C["gray"],
        ).pack(side="right", padx=14, pady=4)

    # ──────────────────────────────────────────────────────────────────────
    # DATA OPERATIONS
    # ──────────────────────────────────────────────────────────────────────

    def _load_credentials(self, search=""):
        for row in self._table.get_children():
            self._table.delete(row)

        rows = (database.search_credentials(search)
                if search else database.get_all_credentials())

        for i, row in enumerate(rows):
            rid, website, username, _, created = row
            date = created[:10] if created else "—"
            tag  = "odd" if i % 2 == 0 else "even"
            self._table.insert("", "end", iid=str(rid),
                               values=(rid, website, username,
                                       "••••••••", date),
                               tags=(tag,))

        n = len(rows)
        self._count_lbl.config(
            text=f"🔐  {n} password{'s' if n != 1 else ''}")
        self._set_status(f"Loaded {n} credential(s)")
        self._show_pw_btn.config(text="👁  Show Password")

    def _save_credential(self):
        WEB_PH  = "e.g. Google, Netflix…"
        USER_PH = "e.g. user@email.com"
        PW_PH   = "Enter or generate a password…"

        web  = self._web_entry.get().strip()
        user = self._user_entry.get().strip()
        pw   = self._pw_entry.get().strip()

        # ── validation ───────────────────────────────────────────────────
        if not web or web == WEB_PH:
            messagebox.showwarning("Missing Field",
                                   "Please enter a website or app name.")
            self._web_entry.focus_set()
            return
        if not user or user == USER_PH:
            messagebox.showwarning("Missing Field",
                                   "Please enter a username or email.")
            self._user_entry.focus_set()
            return
        if not pw or pw == PW_PH:
            messagebox.showwarning("Missing Field",
                                   "Please enter or generate a password.")
            self._pw_entry.focus_set()
            return

        try:
            enc = encryption.encrypt_password(pw)
        except Exception as exc:
            messagebox.showerror("Encryption Error", str(exc))
            return

        if self.edit_mode and self.selected_id:
            ok = database.update_credential(
                self.selected_id, web, user, enc)
            if ok:
                messagebox.showinfo("Updated ✅",
                                    f"Credential for '{web}' updated.")
                self._cancel_edit()
            else:
                messagebox.showerror("Error", "Could not update credential.")
        else:
            ok = database.add_credential(web, user, enc)
            if ok:
                messagebox.showinfo(
                    "Saved ✅",
                    f"Credential for '{web}' saved.\n"
                    f"Password is encrypted before storage.")
                self._clear_form()
            else:
                messagebox.showerror("Error", "Could not save credential.")

        self._load_credentials()
        self._set_status(f"✅  Saved credential for {web}")

    def _delete_credential(self):
        sel = self._table.selection()
        if not sel:
            messagebox.showwarning("No Selection",
                                   "Select a credential to delete.")
            return

        rid     = int(sel[0])
        website = self._table.item(sel[0], "values")[1]

        if messagebox.askyesno("Confirm Delete",
                               f"Delete credential for:\n\n🌐  {website}\n\n"
                               f"This cannot be undone."):
            if database.delete_credential(rid):
                self._load_credentials()
                self._clear_form()
                self.selected_id = None
                self._set_status(f"🗑️  Deleted {website}")
            else:
                messagebox.showerror("Error", "Could not delete credential.")

    def _edit_credential(self):
        sel = self._table.selection()
        if not sel:
            messagebox.showwarning("No Selection",
                                   "Select a credential to edit.")
            return

        rid = int(sel[0])
        row = database.get_credential_by_id(rid)
        if not row:
            messagebox.showerror("Error", "Could not load credential.")
            return

        _, website, username, enc_pw = row

        try:
            plain_pw = encryption.decrypt_password(enc_pw)
        except Exception as exc:
            messagebox.showerror("Decrypt Error", str(exc))
            return

        # ── fill form ────────────────────────────────────────────────────
        self.edit_mode   = True
        self.selected_id = rid

        for entry, value in [
            (self._web_entry,  website),
            (self._user_entry, username),
        ]:
            entry.delete(0, tk.END)
            entry.insert(0, value)
            entry.config(fg=self.C["white"])

        self._pw_entry.delete(0, tk.END)
        self._pw_entry.config(show="•", fg=self.C["white"])
        self._pw_entry.insert(0, plain_pw)

        self._form_title.config(text="✏️  Edit Credential")
        self._save_btn.config(text="💾  Update Credential",
                              bg=self.C["warning"])
        self._set_status(f"✏️  Editing {website}")

        if not hasattr(self, "_cancel_btn"):
            self._cancel_btn = tk.Button(
                self._save_btn.master,
                text="✕  Cancel Edit",
                font=("Segoe UI", 10),
                bg=self.C["card"], fg=self.C["gray"],
                activebackground=self.C["card"],
                relief="flat", cursor="hand2",
                padx=10, pady=8,
                command=self._cancel_edit,
            )
            self._cancel_btn.pack(fill="x", padx=20, pady=(0, 20))

    def _cancel_edit(self):
        self.edit_mode   = False
        self.selected_id = None
        self._form_title.config(text="➕  Add New Credential")
        self._save_btn.config(text="💾  Save Credential",
                              bg=self.C["success"])
        if hasattr(self, "_cancel_btn"):
            self._cancel_btn.destroy()
            del self._cancel_btn
        self._clear_form()

    # ──────────────────────────────────────────────────────────────────────
    # COPY / SHOW PASSWORD
    # ──────────────────────────────────────────────────────────────────────

    def _copy_password(self):
        sel = self._table.selection()
        if not sel:
            messagebox.showwarning("No Selection",
                                   "Select a credential first.")
            return
        rid = int(sel[0])
        row = database.get_credential_by_id(rid)
        if not row:
            return
        try:
            plain = encryption.decrypt_password(row[3])
            pyperclip.copy(plain)
            self._set_status(f"📋  Password for '{row[1]}' copied!")
            messagebox.showinfo("Copied 📋",
                                f"Password for '{row[1]}' copied to clipboard.")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _copy_username(self):
        sel = self._table.selection()
        if not sel:
            messagebox.showwarning("No Selection",
                                   "Select a credential first.")
            return
        username = self._table.item(sel[0], "values")[2]
        pyperclip.copy(username)
        self._set_status(f"📋  Username '{username}' copied!")
        messagebox.showinfo("Copied 📋",
                            f"Username copied:\n{username}")

    def _toggle_table_pw(self):
        sel = self._table.selection()
        if not sel:
            messagebox.showwarning("No Selection",
                                   "Select a credential first.")
            return
        rid    = int(sel[0])
        row    = database.get_credential_by_id(rid)
        values = self._table.item(sel[0], "values")

        if not row:
            return
        try:
            if values[3] == "••••••••":
                plain = encryption.decrypt_password(row[3])
                self._table.item(sel[0],
                                 values=(values[0], values[1],
                                         values[2], plain, values[4]))
                self._show_pw_btn.config(text="🙈  Hide Password")
            else:
                self._table.item(sel[0],
                                 values=(values[0], values[1],
                                         values[2], "••••••••", values[4]))
                self._show_pw_btn.config(text="👁  Show Password")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    # ──────────────────────────────────────────────────────────────────────
    # GENERATOR
    # ──────────────────────────────────────────────────────────────────────

    def _generate_password(self):
        length = int(self._gen_len.get())
        pw = generate_password(
            length=length,
            use_uppercase=self._use_upper.get(),
            use_lowercase=self._use_lower.get(),
            use_digits=self._use_digits.get(),
            use_symbols=self._use_symbols.get(),
        )
        self._pw_entry.delete(0, tk.END)
        self._pw_entry.config(show="", fg=self.C["white"])
        self._pw_entry.insert(0, pw)
        pyperclip.copy(pw)
        self._update_strength()
        self._set_status(f"🎲  Generated {length}-char password (copied to clipboard)")

    def _update_strength(self, event=None):
        pw = self._pw_entry.get()
        PH = "Enter or generate a password…"
        if not pw or pw == PH:
            self._strength_lbl.config(text="")
            return
        info  = check_password_strength(pw)
        score = int(info["score"])
        bar   = "█" * score + "░" * max(0, 5 - score)
        self._strength_lbl.config(
            text=f"Strength: {info['label']}  {bar}",
            fg=info["color"],
        )

    # ──────────────────────────────────────────────────────────────────────
    # FORM HELPERS
    # ──────────────────────────────────────────────────────────────────────

    def _clear_form(self):
        """Reset all form fields back to their placeholder state."""
        pairs = [
            (self._web_entry,  "e.g. Google, Netflix…"),
            (self._user_entry, "e.g. user@email.com"),
        ]
        C = self.C
        for entry, ph in pairs:
            entry.delete(0, tk.END)
            entry.insert(0, ph)
            entry.config(fg=C["gray"])

        # Password field: clear masking BEFORE inserting placeholder
        self._pw_entry.delete(0, tk.END)
        self._pw_entry.config(show="")
        self._pw_entry.insert(0, "Enter or generate a password…")
        self._pw_entry.config(fg=C["gray"])
        self._pw_btn.config(text="👁")

        self._strength_lbl.config(text="")

    # ──────────────────────────────────────────────────────────────────────
    # SEARCH
    # ──────────────────────────────────────────────────────────────────────

    def _on_search(self, *_):
        term = self._search_var.get()
        PH   = "Search by website or username…"
        self._load_credentials("" if (not term or term == PH) else term)

    def _clear_search(self):
        PH = "Search by website or username…"
        self._search_entry.delete(0, tk.END)
        self._search_entry.insert(0, PH)
        self._search_entry.config(fg=self.C["gray"])
        self._search_var.set("")
        self._load_credentials()

    # ──────────────────────────────────────────────────────────────────────
    # TABLE EVENTS
    # ──────────────────────────────────────────────────────────────────────

    def _on_select(self, _event):
        sel = self._table.selection()
        if sel:
            self.selected_id = int(sel[0])
            v = self._table.item(sel[0], "values")
            self._set_status(
                f"Selected: {v[1]}  |  {v[2]}  |  Created: {v[4]}")
            self._show_pw_btn.config(text="👁  Show Password")

    def _on_double_click(self, _event):
        sel = self._table.selection()
        if not sel:
            return
        rid = int(sel[0])
        row = database.get_credential_by_id(rid)
        if not row:
            return
        try:
            plain = encryption.decrypt_password(row[3])
        except Exception:
            plain = "[decryption failed]"
        self._show_detail(row[1], row[2], plain)

    def _show_detail(self, website, username, password):
        """Popup showing credential detail with copy buttons."""
        C   = self.C
        pop = tk.Toplevel(self.root)
        pop.title(f"Credential — {website}")
        pop.geometry("400x310")
        pop.resizable(False, False)
        pop.configure(bg=C["bg"])
        pop.transient(self.root)
        pop.grab_set()
        pop.geometry("+%d+%d" % (
            self.root.winfo_x() + 350,
            self.root.winfo_y() + 200,
        ))

        tk.Label(pop, text=f"🌐  {website}",
                 font=("Segoe UI", 14, "bold"),
                 bg=C["bg"], fg=C["accent"]).pack(pady=(20, 10))
        tk.Frame(pop, bg=C["border"], height=1).pack(fill="x", padx=20)

        card = tk.Frame(pop, bg=C["card"])
        card.pack(fill="x", padx=20, pady=14)

        def _row(label_text, value, show=""):
            r = tk.Frame(card, bg=C["card"])
            r.pack(fill="x", padx=14, pady=6)
            tk.Label(r, text=label_text,
                     font=("Segoe UI", 10, "bold"),
                     bg=C["card"], fg=C["gray"],
                     width=10, anchor="w").pack(side="left")
            e = tk.Entry(r, font=("Segoe UI", 10),
                         bg=C["card"], fg=C["white"],
                         relief="flat", bd=0, show=show,
                         readonlybackground=C["card"])
            e.insert(0, value)
            e.config(state="readonly")
            e.pack(side="left", fill="x", expand=True)
            return e

        _row("Username:", username)
        pw_entry = _row("Password:", password, show="•")

        # Toggle show password in popup
        def _toggle_detail_pw():
            if pw_entry.cget("show") == "•":
                pw_entry.config(state="normal", show="")
                pw_entry.config(state="readonly")
            else:
                pw_entry.config(state="normal", show="•")
                pw_entry.config(state="readonly")

        btns = tk.Frame(pop, bg=C["bg"])
        btns.pack(pady=10)

        for text, cmd in [
            ("📋  Copy Password",
             lambda: [pyperclip.copy(password),
                      self._set_status("📋  Password copied!")]),
            ("👁  Show/Hide",  _toggle_detail_pw),
            ("✕  Close",      pop.destroy),
        ]:
            tk.Button(btns, text=text,
                      font=("Segoe UI", 10),
                      bg=C["blue"], fg="white",
                      activebackground="#1a4a80",
                      relief="flat", cursor="hand2",
                      padx=10, pady=6,
                      command=cmd).pack(side="left", padx=4)

    def _sort(self, col):
        items = [(self._table.set(i, col), i)
                 for i in self._table.get_children("")]
        self._sort_rev = (self._sort_col == col) and not self._sort_rev
        self._sort_col = col
        items.sort(reverse=self._sort_rev)
        for idx, (_, item) in enumerate(items):
            self._table.move(item, "", idx)
            self._table.item(item,
                             tags=("odd" if idx % 2 == 0 else "even",))

    # ──────────────────────────────────────────────────────────────────────
    # UTILITY
    # ──────────────────────────────────────────────────────────────────────

    def _set_status(self, msg: str):
        self._status_lbl.config(text=f"  {msg}")
        self.root.update_idletasks()

    def _lock_vault(self):
        if messagebox.askyesno("Lock Vault",
                               "Lock the vault and return to the login screen?"):
            self.root.destroy()
            if self.login_root:
                try:
                    self.login_root.deiconify()
                except Exception:
                    pass
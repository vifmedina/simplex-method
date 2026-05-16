import tkinter as tk
from tkinter import ttk, messagebox

from scipy.optimize import linprog

class SimplexGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Método Simplex")
        self.root.geometry("900x650")
        self.root.minsize(700, 500)

        self.opt_type = tk.StringVar(value="max")
        self.num_vars = tk.IntVar(value=2)
        self.num_constraints = tk.IntVar(value=2)

        self.obj_entries = []
        self.constraint_rows = []

        self._build_config_frame()
        self._build_form_area()
        self._build_result_frame()

        self._generate_form()

    # ------------------------------------------------------------------
    # CONSTRUÇÃO DA INTERFACE
    # ------------------------------------------------------------------
    def _build_config_frame(self):
        frame = ttk.LabelFrame(self.root, text="Configuração", padding=10)
        frame.pack(fill="x", padx=10, pady=(10, 5))

        ttk.Label(frame, text="Tipo de otimização:").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        ttk.Radiobutton(frame, text="Maximização", variable=self.opt_type, value="max").grid(row=0, column=1, padx=5)
        ttk.Radiobutton(frame, text="Minimização", variable=self.opt_type, value="min").grid(row=0, column=2, padx=5)

        ttk.Label(frame, text="Nº de variáveis:").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        ttk.Spinbox(frame, from_=1, to=20, textvariable=self.num_vars, width=5).grid(row=1, column=1, sticky="w", padx=5)

        ttk.Label(frame, text="Nº de restrições:").grid(row=1, column=2, sticky="w", padx=5, pady=4)
        ttk.Spinbox(frame, from_=1, to=20, textvariable=self.num_constraints, width=5).grid(row=1, column=3, sticky="w", padx=5)

        ttk.Button(frame, text="Gerar formulário", command=self._generate_form).grid(row=1, column=4, padx=10)

    def _build_form_area(self):
        container = ttk.Frame(self.root)
        container.pack(fill="both", expand=True, padx=10, pady=5)

        canvas = tk.Canvas(container, highlightthickness=0)
        vbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        hbar = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
        canvas.configure(yscrollcommand=vbar.set, xscrollcommand=hbar.set)

        vbar.pack(side="right", fill="y")
        hbar.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)

        self.form_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=self.form_frame, anchor="nw")
        self.form_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )

    def _build_result_frame(self):
        frame = ttk.LabelFrame(self.root, text="Resultado", padding=10)
        frame.pack(fill="x", padx=10, pady=(5, 10))

        self.result_label = ttk.Label(frame, text="—", font=("Consolas", 11), justify="left")
        self.result_label.pack(anchor="w")

    # ------------------------------------------------------------------
    # FORMULÁRIO DINÂMICO
    # ------------------------------------------------------------------
    def _generate_form(self):
        for widget in self.form_frame.winfo_children():
            widget.destroy()

        n = self.num_vars.get()
        m = self.num_constraints.get()

        obj_frame = ttk.LabelFrame(self.form_frame, text="Função Objetivo", padding=10)
        obj_frame.pack(fill="x", pady=5, padx=2)

        ttk.Label(obj_frame, text="Z =").grid(row=0, column=0, padx=5)
        self.obj_entries = []
        for j in range(n):
            entry = ttk.Entry(obj_frame, width=6, justify="right")
            entry.insert(0, "0")
            entry.grid(row=0, column=1 + j * 3, padx=2)
            self.obj_entries.append(entry)
            ttk.Label(obj_frame, text=f"·x{j+1}").grid(row=0, column=2 + j * 3)
            if j < n - 1:
                ttk.Label(obj_frame, text="+").grid(row=0, column=3 + j * 3, padx=2)

        con_frame = ttk.LabelFrame(self.form_frame, text="Restrições", padding=10)
        con_frame.pack(fill="both", expand=True, pady=5, padx=2)

        self.constraint_rows = []
        for i in range(m):
            entries = []
            for j in range(n):
                entry = ttk.Entry(con_frame, width=6, justify="right")
                entry.insert(0, "0")
                entry.grid(row=i, column=j * 3, padx=2, pady=3)
                entries.append(entry)
                ttk.Label(con_frame, text=f"·x{j+1}").grid(row=i, column=j * 3 + 1)
                if j < n - 1:
                    ttk.Label(con_frame, text="+").grid(row=i, column=j * 3 + 2, padx=2)

            op = ttk.Combobox(con_frame, values=["<=", ">=", "="], width=4, state="readonly")
            op.current(0)
            op.grid(row=i, column=n * 3, padx=8)

            rhs = ttk.Entry(con_frame, width=8, justify="right")
            rhs.insert(0, "0")
            rhs.grid(row=i, column=n * 3 + 1, padx=2)

            self.constraint_rows.append((entries, op, rhs))

        buttons_frame = ttk.Frame(self.form_frame)
        buttons_frame.pack(pady=10)

        ttk.Button(buttons_frame, text="Resolver", command=self._solve).pack(side="left", padx=5)

        ttk.Button(buttons_frame, text="Limpar campos", command=self._clear_fields).pack(side="left", padx=5)

        self.result_label.config(text="—", foreground="black")

    # ------------------------------------------------------------------
    # RESOLUÇÃO
    # ------------------------------------------------------------------
    @staticmethod
    def _parse(entry):
        text = entry.get().strip().replace(",", ".")
        if text == "":
            return 0.0
        return float(text)

    def _solve(self):
        try:
            obj_coefs = [self._parse(e) for e in self.obj_entries]
        except ValueError:
            messagebox.showerror("Erro", "Coeficientes inválidos na função objetivo.")
            return

        is_max = self.opt_type.get() == "max"
        c = [-x for x in obj_coefs] if is_max else list(obj_coefs)

        A_ub, b_ub = [], []
        A_eq, b_eq = [], []

        try:
            for idx, (entries, op_cb, rhs_e) in enumerate(self.constraint_rows, start=1):
                coefs = [self._parse(e) for e in entries]
                rhs = self._parse(rhs_e)
                op = op_cb.get()
                if op == "<=":
                    A_ub.append(coefs)
                    b_ub.append(rhs)
                elif op == ">=":
                    A_ub.append([-v for v in coefs])
                    b_ub.append(-rhs)
                else:
                    A_eq.append(coefs)
                    b_eq.append(rhs)
        except ValueError:
            messagebox.showerror("Erro", f"Coeficiente inválido na restrição {idx}.")
            return

        result = linprog(
            c=c,
            A_ub=A_ub or None,
            b_ub=b_ub or None,
            A_eq=A_eq or None,
            b_eq=b_eq or None,
            bounds=[(0, None)] * len(c),
            method="highs",
        )

        if result.success:
            lines = [f"x{i+1} = {v:.4f}" for i, v in enumerate(result.x)]
            z = -result.fun if is_max else result.fun
            tipo = "máximo" if is_max else "mínimo"
            lines.append("")
            lines.append(f"Valor {tipo} de Z = {z:.4f}")
            self.result_label.config(text="\n".join(lines), foreground="#0a6e1a")
        else:
            self.result_label.config(
                text=f"Não foi possível encontrar solução.\n{result.message}",
                foreground="#b00020",
            )

    # ------------------------------------------------------------------
    # APAGAR CAMPOS
    # ------------------------------------------------------------------
    def _clear_fields(self):
        for entry in self.obj_entries:
            entry.delete(0, tk.END)
            entry.insert(0, "0")

        for entries, op, rhs in self.constraint_rows:
            for entry in entries:
                entry.delete(0, tk.END)
                entry.insert(0, "0")

            op.current(0)

            rhs.delete(0, tk.END)
            rhs.insert(0, "0")

        self.result_label.config(text="—", foreground="black")


def main():
    root = tk.Tk()
    try:
        ttk.Style().theme_use("vista")
    except tk.TclError:
        pass
    SimplexGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

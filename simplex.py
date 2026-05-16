from scipy.optimize import linprog

print("=== MÉTODO SIMPLEX ===")

# Quantidade de variáveis
num_variaveis = int(input("Quantidade de variáveis: "))

# Quantidade de restrições
num_restricoes = int(input("Quantidade de restrições: "))

# -----------------------------
# FUNÇÃO OBJETIVO
# -----------------------------
print("\nFunção Objetivo")
print("Exemplo para Z = 3x + 5y:")
print("Digite: 3 5")

coef_objetivo = list(
    map(float, input("Coeficientes da função objetivo: ").split())
)

# linprog faz minimização
# então invertimos o sinal
c = [-x for x in coef_objetivo]

# -----------------------------
# RESTRIÇÕES
# -----------------------------
A = []
B = []

print("\nDigite as restrições")

for i in range(num_restricoes):
    print(f"\nRestrição {i+1}")

    print("Exemplo:")
    print("Para 3x + 2y <= 18")
    print("Digite: 3 2")

    coeficientes = list(
        map(float, input("Coeficientes: ").split())
    )

    resultado = float(input("Resultado da restrição: "))

    A.append(coeficientes)
    B.append(resultado)

# -----------------------------
# LIMITES DAS VARIÁVEIS
# -----------------------------
bounds = []

for i in range(num_variaveis):
    bounds.append((0, None))  # x >= 0

# -----------------------------
# RESOLVER
# -----------------------------
resultado = linprog(
    c=c,
    A_ub=A,
    b_ub=B,
    bounds=bounds,
    method="highs"
)

# -----------------------------
# RESULTADO
# -----------------------------
print("\n=== RESULTADO ===")

if resultado.success:

    for i, valor in enumerate(resultado.x):
        print(f"x{i+1} = {valor}")

    print(f"\nValor ótimo de Z = {-resultado.fun}")

else:
    print("Não foi possível encontrar solução.")
    print(resultado.message)
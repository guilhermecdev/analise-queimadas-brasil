"""
Gera um dataset sintético de focos de queimadas por estado/bioma/mês,
inspirado nos padrões públicos divulgados pelo Programa Queimadas do INPE
(concentração em Amazônia e Cerrado, pico sazonal entre agosto e outubro).

IMPORTANTE: este dataset é fictício, construído para fins didáticos. Para
dados reais, consulte o portal oficial: https://queimadas.dgi.inpe.br/queimadas/portal
"""
import numpy as np
import pandas as pd

np.random.seed(42)

# Estado -> (bioma predominante, peso relativo de focos, região)
estados_info = {
    "Pará":               ("Amazônia",     1.00, "Norte"),
    "Mato Grosso":        ("Amazônia",     0.85, "Centro-Oeste"),
    "Amazonas":           ("Amazônia",     0.55, "Norte"),
    "Tocantins":          ("Cerrado",      0.50, "Norte"),
    "Maranhão":           ("Cerrado",      0.48, "Nordeste"),
    "Acre":               ("Amazônia",     0.35, "Norte"),
    "Rondônia":           ("Amazônia",     0.40, "Norte"),
    "Bahia":              ("Caatinga",     0.30, "Nordeste"),
    "Goiás":              ("Cerrado",      0.38, "Centro-Oeste"),
    "Minas Gerais":       ("Cerrado",      0.42, "Sudeste"),
    "Mato Grosso do Sul": ("Pantanal",     0.33, "Centro-Oeste"),
    "Piauí":              ("Caatinga",     0.28, "Nordeste"),
    "São Paulo":          ("Mata Atlântica", 0.30, "Sudeste"),
    "Roraima":            ("Amazônia",     0.25, "Norte"),
    "Amapá":              ("Amazônia",     0.18, "Norte"),
}

meses = list(range(1, 13))
anos = [2020, 2021, 2022, 2023, 2024, 2025]

# Fator sazonal mensal (pico ago-out, mínimo no verão chuvoso)
fator_sazonal = {
    1: 0.35, 2: 0.30, 3: 0.28, 4: 0.30, 5: 0.40, 6: 0.55,
    7: 0.80, 8: 1.60, 9: 1.90, 10: 1.50, 11: 0.75, 12: 0.45,
}

# Fator anual (2024 foi ano recorde de seca extrema; 2020 também crítico)
fator_anual = {2020: 1.15, 2021: 0.85, 2022: 0.90, 2023: 0.80, 2024: 1.55, 2025: 1.05}

linhas = []
for ano in anos:
    for mes in meses:
        for estado, (bioma, peso, regiao) in estados_info.items():
            base = 900 * peso * fator_sazonal[mes] * fator_anual[ano]
            ruido = np.random.normal(1.0, 0.18)
            focos = max(0, int(base * ruido))

            # área estimada queimada (ha) correlacionada aos focos, com variação
            area_ha = round(focos * np.random.uniform(8, 22), 1)

            # risco de fogo médio do mês (0 a 1), maior em meses/anos críticos
            risco_fogo = np.clip(
                np.random.normal(0.3 + 0.5 * fator_sazonal[mes] / 1.9 * fator_anual[ano] / 1.55, 0.08),
                0.05, 0.99
            )

            linhas.append({
                "ano": ano,
                "mes": mes,
                "estado": estado,
                "regiao": regiao,
                "bioma": bioma,
                "focos_calor": focos,
                "area_estimada_ha": area_ha,
                "risco_fogo_medio": round(risco_fogo, 2),
            })

df = pd.DataFrame(linhas)
df.to_csv("data/queimadas_brasil.csv", index=False, encoding="utf-8")
print(f"Dataset gerado com {len(df)} registros em data/queimadas_brasil.csv")
print(f"Período: {min(anos)}-{max(anos)} | Estados: {len(estados_info)}")

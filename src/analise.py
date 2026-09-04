"""
Projeto: Análise do Índice de Queimadas no Brasil
Autor: Guilherme Cardozo de Andrade
Descrição: Análise exploratória de focos de queimadas por estado, bioma e
ano, usando pandas, numpy e matplotlib.

Fonte de inspiração: padrões públicos do Programa Queimadas (INPE).
Dataset sintético gerado em src/gerar_dados.py — para dados reais, ver
https://queimadas.dgi.inpe.br/queimadas/portal
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

plt.style.use("seaborn-v0_8-darkgrid")

# ---------------------------------------------------------------
# 1. Carga e preparação dos dados
# ---------------------------------------------------------------
df = pd.read_csv("data/queimadas_brasil.csv")
df["data_ref"] = pd.to_datetime(df["ano"].astype(str) + "-" + df["mes"].astype(str) + "-01")

print("=" * 60)
print("VISÃO GERAL DO DATASET")
print("=" * 60)
print(df.info())
print(df.select_dtypes(include=[np.number]).describe().round(2))

# ---------------------------------------------------------------
# 2. Indicadores gerais (numpy)
# ---------------------------------------------------------------
total_focos = np.sum(df["focos_calor"])
total_area = np.sum(df["area_estimada_ha"])
media_focos_mes = np.mean(df.groupby("data_ref")["focos_calor"].sum())
desvio_focos_mes = np.std(df.groupby("data_ref")["focos_calor"].sum())

print("\n" + "=" * 60)
print("INDICADORES GERAIS (2020-2025)")
print("=" * 60)
print(f"Total de focos de calor ........ {total_focos:,.0f}")
print(f"Área estimada queimada (ha) ..... {total_area:,.0f}")
print(f"Média de focos por mês (Brasil) . {media_focos_mes:,.0f}")
print(f"Desvio padrão mensal ............ {desvio_focos_mes:,.0f}")

# ---------------------------------------------------------------
# 3. Agregações principais
# ---------------------------------------------------------------
focos_por_ano = df.groupby("ano")["focos_calor"].sum()
focos_por_bioma = df.groupby("bioma")["focos_calor"].sum().sort_values(ascending=False)
focos_por_estado = df.groupby("estado")["focos_calor"].sum().sort_values(ascending=False)
focos_por_mes = df.groupby("mes")["focos_calor"].sum()
focos_mensal_serie = df.groupby("data_ref")["focos_calor"].sum().sort_index()

top10_estados = focos_por_estado.head(10)

# ---------------------------------------------------------------
# 4. Detecção de meses críticos (outliers via z-score, numpy)
# ---------------------------------------------------------------
serie = focos_mensal_serie.values
z_scores = (serie - np.mean(serie)) / np.std(serie)
meses_criticos = focos_mensal_serie[z_scores > 1.5]

print("\n" + "=" * 60)
print("TOP 5 ESTADOS EM FOCOS DE CALOR (2020-2025)")
print("=" * 60)
print(top10_estados.head(5))

print(f"\nMeses classificados como críticos (z-score > 1.5): {len(meses_criticos)}")
print(meses_criticos.round(0))

# ---------------------------------------------------------------
# 5. Visualizações
# ---------------------------------------------------------------

def formata_milhar(x, _):
    return f"{x/1000:.0f}k"


# 5.1 Série temporal mensal de focos (linha)
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(focos_mensal_serie.index, focos_mensal_serie.values, color="#dc2626", linewidth=1.5)
ax.fill_between(focos_mensal_serie.index, focos_mensal_serie.values, alpha=0.15, color="#dc2626")
ax.set_title("Focos de Calor por Mês — Brasil (2020-2025)", fontsize=14, fontweight="bold")
ax.set_xlabel("Data")
ax.set_ylabel("Focos de calor")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(formata_milhar))
plt.tight_layout()
plt.savefig("images/serie_temporal_focos.png", dpi=150)
plt.close()

# 5.2 Total de focos por ano (barras)
fig, ax = plt.subplots(figsize=(8, 5))
cores = ["#f87171" if ano != 2024 else "#991b1b" for ano in focos_por_ano.index]
ax.bar(focos_por_ano.index.astype(str), focos_por_ano.values, color=cores)
ax.set_title("Total de Focos de Calor por Ano", fontsize=14, fontweight="bold")
ax.set_ylabel("Focos de calor")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(formata_milhar))
for i, v in enumerate(focos_por_ano.values):
    ax.text(i, v + max(focos_por_ano.values) * 0.01, f"{v/1000:.0f}k", ha="center", fontsize=9)
plt.tight_layout()
plt.savefig("images/focos_por_ano.png", dpi=150)
plt.close()

# 5.3 Distribuição por bioma (pizza)
fig, ax = plt.subplots(figsize=(7, 7))
ax.pie(
    focos_por_bioma.values,
    labels=focos_por_bioma.index,
    autopct="%1.1f%%",
    startangle=90,
    colors=plt.cm.Oranges(np.linspace(0.35, 0.9, len(focos_por_bioma))),
)
ax.set_title("Distribuição de Focos de Calor por Bioma", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("images/focos_por_bioma.png", dpi=150)
plt.close()

# 5.4 Top 10 estados (barras horizontais)
fig, ax = plt.subplots(figsize=(9, 6))
ax.barh(top10_estados.index[::-1], top10_estados.values[::-1], color="#ea580c")
ax.set_title("Top 10 Estados em Focos de Calor (2020-2025)", fontsize=14, fontweight="bold")
ax.set_xlabel("Focos de calor")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(formata_milhar))
plt.tight_layout()
plt.savefig("images/top_estados.png", dpi=150)
plt.close()

# 5.5 Sazonalidade média mensal (barras)
fig, ax = plt.subplots(figsize=(9, 5))
nomes_meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
cores_mes = plt.cm.YlOrRd(focos_por_mes.values / focos_por_mes.values.max())
ax.bar(nomes_meses, focos_por_mes.values, color=cores_mes)
ax.set_title("Sazonalidade — Total de Focos por Mês (soma 2020-2025)", fontsize=14, fontweight="bold")
ax.set_ylabel("Focos de calor")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(formata_milhar))
plt.tight_layout()
plt.savefig("images/sazonalidade_mensal.png", dpi=150)
plt.close()

print("\nGráficos salvos na pasta 'images/'.")
print("Análise concluída com sucesso!")

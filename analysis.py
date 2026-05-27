#!/usr/bin/env python3
"""
Простой анализ financial_statements.csv
Датасет: Kaggle – Financial Statements of Major Companies (2009–2023)

1) Этот файл (analysis.py) и financial_statements.csv должны лежать в одной папке.
2) Запуск: python analysis.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore")

print("=" * 55)
print("АНАЛИЗ ФИНАНСОВОЙ ОТЧЁТНОСТИ КОМПАНИЙ")
print("=" * 55)

# 1. Загрузка данных
df = pd.read_csv("financial_statements.csv")

# Переименуем странные названия колонок в удобные
df.rename(
    columns={
        "Company ": "Company",          # убрать пробел в конце
        "Net Profit Margin": "Net_Margin_%",
        "ROA": "ROA_%",
    },
    inplace=True,
)

print("\n[1] Общая информация")
print(f"  Строк: {len(df)}")
print(f"  Колонки: {list(df.columns)}")
print(f"  Период: {df['Year'].min()} – {df['Year'].max()}")
print(f"  Компаний: {df['Company'].nunique()}")

# 2. Очистка
df = df.dropna(subset=["Revenue", "Net Income"])
df = df[df["Revenue"] > 0]

for col in ["Net_Margin_%", "ROA_%"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

print(f"  После очистки строк: {len(df)}")

# 3. Топ-10 компаний по выручке за последний год
last_year = df["Year"].max()
top10_revenue = (
    df[df["Year"] == last_year]
    .nlargest(10, "Revenue")[["Company", "Revenue", "Net Income", "Net_Margin_%"]]
    .reset_index(drop=True)
)
top10_revenue.index += 1

print(f"\n[2] ТОП-10 компаний по выручке ({last_year}):")
print(top10_revenue.to_string())

# 4. Средние показатели по годам
yearly = (
    df.groupby("Year")
    .agg(
        Avg_Revenue=("Revenue", "mean"),
        Avg_Net_Margin=("Net_Margin_%", "mean"),
        Avg_ROA=("ROA_%", "mean"),
        Companies=("Company", "nunique"),
    )
    .reset_index()
    .round(2)
)

print("\n[3] Средние значения по годам:")
print(yearly.to_string(index=False))

# 5. Топ-10 по ROA (если есть колонка)
top10_roa = None
if "ROA_%" in df.columns:
    tmp = df[(df["Year"] == last_year) & df["ROA_%"].notna()]
    if not tmp.empty:
        top10_roa = (
            tmp.nlargest(10, "ROA_%")[["Company", "ROA_%", "Net_Margin_%"]]
            .reset_index(drop=True)
        )
        top10_roa.index += 1
        print(f"\n[4] ТОП-10 компаний по ROA ({last_year}):")
        print(top10_roa.to_string())
    else:
        print("\n[4] Нет данных по ROA для последнего года.")
else:
    print("\n[4] Колонка ROA отсутствует в датасете.")

# 6. Графики
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Анализ финансовой отчётности", fontsize=14, fontweight="bold")

# График 1: Топ-10 по выручке
ax1 = axes[0, 0]
if not top10_revenue.empty:
    revenue_scaled = top10_revenue["Revenue"] / 1_000  # просто масштабируем
    bars = ax1.barh(top10_revenue["Company"], revenue_scaled, color="steelblue")
    ax1.set_xlabel("Выручка (x 1 000 единиц)")
    ax1.set_title(f"Топ-10 по выручке ({last_year})")
    ax1.invert_yaxis()
else:
    ax1.text(0.5, 0.5, "Нет данных", ha="center", va="center")

# График 2: Средняя рентабельность по годам
ax2 = axes[0, 1]
ax2.plot(yearly["Year"], yearly["Avg_Net_Margin"], marker="o", color="green")
ax2.axhline(y=0, color="red", linestyle="--", alpha=0.5)
ax2.set_xlabel("Год")
ax2.set_ylabel("Net Margin (%)")
ax2.set_title("Средняя рентабельность по годам")
ax2.grid(True, alpha=0.3)

# График 3: Топ-10 по ROA
ax3 = axes[1, 0]
if top10_roa is not None and not top10_roa.empty:
    colors = ["#2196F3" if x > 0 else "#F44336" for x in top10_roa["ROA_%"]]
    ax3.bar(range(len(top10_roa)), top10_roa["ROA_%"], color=colors)
    ax3.set_xticks(range(len(top10_roa)))
    ax3.set_xticklabels(top10_roa["Company"], rotation=45, ha="right", fontsize=8)
    ax3.set_ylabel("ROA (%)")
    ax3.set_title(f"Топ-10 по ROA ({last_year})")
    ax3.grid(True, alpha=0.3, axis="y")
else:
    ax3.text(0.5, 0.5, "Нет данных по ROA", ha="center", va="center")

# График 4: связь выручки и рентабельности
ax4 = axes[1, 1]
sample = df[df["Year"] == last_year].copy()
ax4.scatter(sample["Revenue"], sample["Net_Margin_%"], alpha=0.5, color="purple", s=30)
ax4.set_xlabel("Выручка")
ax4.set_ylabel("Net Margin (%)")
ax4.set_title(f"Выручка vs Net Margin ({last_year})")
ax4.axhline(y=0, color="red", linestyle="--", alpha=0.5)
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("financial_analysis_dashboard.png", dpi=150, bbox_inches="tight")
print("\n[5] График сохранён: financial_analysis_dashboard.png")

# 7. Сохранение результатов
yearly.to_csv("yearly_trends.csv", index=False)
top10_revenue.to_csv("top10_by_revenue.csv", index=False)
if top10_roa is not None and not top10_roa.empty:
    top10_roa.to_csv("top10_by_roa.csv", index=False)

print("\n[6] Готово.")
print("✅ Анализ завершён успешно.")
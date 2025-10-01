import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Business Plan Scuola", layout="wide")
st.title("Business Plan Scuola Superiore — Versione Avanzata")

# --- SCENARIO ---
scenario = st.selectbox("Seleziona scenario", ["Pessimistico", "Atteso", "Ottimistico"])
growth_modifier = {"Pessimistico": 0.8, "Atteso": 1.0, "Ottimistico": 1.2}[scenario]

# --- INPUT PRINCIPALI ---
col1, col2 = st.columns(2)

with col1:
    years = st.slider("Anni di proiezione", 3, 12, 7)
    initial_students = st.number_input("Studenti iniziali", 5, 200, 25)
    annual_growth = st.slider("Crescita % annua studenti", 0, 50, 15)
    tuition = st.number_input("Retta annua per studente (€)", 1000, 10000, 5500)
    teaching_hours_per_student = st.number_input("Ore didattiche per studente/anno", 50, 300, 150)

with col2:
    teachers_first_year = st.number_input("Insegnanti primo anno", 1, 50, 5)
    hours_per_teacher_week = st.number_input("Ore/settimana per insegnante", 6, 40, 20)
    weeks_per_year = st.number_input("Settimane/anno", 1, 52, 36)
    cost_per_teacher_hour = st.number_input("Costo/ora insegnante (€)", 10, 200, 30)

# --- COSTI ---
fixed_costs = st.number_input("Costi fissi annui (€)", 10000, 500000, 80000)
variable_cost_per_student = st.number_input("Costi variabili per studente (€)", 0, 2000, 300)

# --- FINANZIAMENTO ---
initial_investment = st.number_input("Investimento iniziale (€)", 0, 1000000, 200000)
loan_rate = st.number_input("Tasso annuo (%)", 0.0, 10.0, 4.5)
loan_years = st.number_input("Anni rimborso", 1, 20, 7)

# --- FUNZIONI ---
def annual_loan_payment(amount, rate_pct, n_years):
    if n_years == 0 or amount <= 0:
        return 0
    r = rate_pct / 100
    return (r * amount) / (1 - (1 + r)**(-n_years))

loan_payment = annual_loan_payment(initial_investment, loan_rate, loan_years)

# --- CALCOLI ---
data = []
students = initial_students
cash_cum = -initial_investment

for y in range(1, years+1):
    revenue = students * tuition

    # ore totali necessarie e insegnanti richiesti
    teaching_hours_needed = students * teaching_hours_per_student
    hours_per_teacher_year = hours_per_teacher_week * weeks_per_year
    required_teachers = max(1, int(np.ceil(teaching_hours_needed / hours_per_teacher_year)))

    payroll = required_teachers * hours_per_teacher_year * cost_per_teacher_hour
    var_costs = students * variable_cost_per_student
    financing = loan_payment if y <= loan_years else 0
    total_costs = payroll + var_costs + fixed_costs + financing
    ebit = revenue - total_costs
    cash_cum += ebit

    data.append({
        "Anno": y,
        "Studenti": round(students),
        "Insegnanti": required_teachers,
        "Ricavi": round(revenue),
        "Payroll": round(payroll),
        "CostiVariabili": round(var_costs),
        "CostiFissi": round(fixed_costs),
        "Finanziamento": round(financing),
        "TotaleCosti": round(total_costs),
        "EBIT": round(ebit),
        "CashCumulato": round(cash_cum)
    })

    students *= (1 + annual_growth / 100 * growth_modifier)

df = pd.DataFrame(data)

# --- OUTPUT ---
st.subheader("Tabella Proiezioni")
st.dataframe(df)

# --- GRAFICI ---
st.subheader("Grafico Ricavi vs Costi vs EBIT")
fig1, ax1 = plt.subplots(figsize=(8,4))
ax1.plot(df["Anno"], df["Ricavi"], label="Ricavi")
ax1.plot(df["Anno"], df["TotaleCosti"], label="Totale Costi")
ax1.plot(df["Anno"], df["EBIT"], label="EBIT")
ax1.set_xlabel("Anno")
ax1.set_ylabel("€")
ax1.legend()
st.pyplot(fig1)

st.subheader("Composizione Costi per anno")
fig2, ax2 = plt.subplots(figsize=(8,4))
ax2.bar(df["Anno"], df["Payroll"], label="Payroll")
ax2.bar(df["Anno"], df["CostiFissi"], bottom=df["Payroll"], label="Fissi")
ax2.bar(df["Anno"], df["CostiVariabili"], bottom=df["Payroll"]+df["CostiFissi"], label="Variabili")
ax2.set_xlabel("Anno")
ax2.set_ylabel("€")
ax2.legend()
st.pyplot(fig2)

st.subheader("Cash Flow Cumulato")
fig3, ax3 = plt.subplots(figsize=(8,4))
ax3.plot(df["Anno"], df["CashCumulato"], marker='o')
ax3.axhline(0, color='red', linestyle='--')
ax3.set_xlabel("Anno")
ax3.set_ylabel("€")
st.pyplot(fig3)

# --- DOWNLOAD CSV ---
csv = df.to_csv(index=False)
st.download_button("Scarica CSV", data=csv, file_name="school_projections.csv", mime="text/csv")

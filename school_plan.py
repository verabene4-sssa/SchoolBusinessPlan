import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- CONFIG ---
st.set_page_config(page_title="Business Plan Scuola Internazionale", layout="wide")

# --- BLOCCO PASSWORD ---
PASSWORD = "Scuola123"
if "password_correct" not in st.session_state:
    st.session_state.password_correct = False

def check_password():
    if st.session_state.password_input == PASSWORD:
        st.session_state.password_correct = True
    else:
        st.error("❌ Password errata!")

if not st.session_state.password_correct:
    st.sidebar.title("🔑 Login")
    st.sidebar.text_input("Inserisci password:", type="password", key="password_input")
    st.sidebar.button("Login", on_click=check_password)

else:
    st.title("🏫 Modello Business Plan - Scuola Internazionale")
    st.markdown("Un modello interattivo per proiezioni e analisi economico-finanziarie 📊")

    # --- SIDEBAR: Input Condizioni principali ---
    st.sidebar.header("⚙️ Condizioni principali")
    inputs = {
        "Numero studenti primo anno": st.sidebar.number_input("👩‍🎓 Numero studenti", 1, 500, 15),
        "Crescita annua (%)": st.sidebar.slider("📈 Crescita annua (%)", 0, 100, 50),
        "Retta/studente (€)": st.sidebar.number_input("💶 Retta per studente", 1000, 20000, 4000),
        "Ore/settimana per insegnante": st.sidebar.number_input("⏱ Ore/settimana insegnante", 1, 40, 25),
        "Settimane/anno": st.sidebar.number_input("📅 Settimane annue", 1, 52, 33),
        "Costo/ora insegnante (€)": st.sidebar.number_input("💰 Costo orario insegnante", 10, 200, 30),
        "Costi fissi annui (€)": st.sidebar.number_input("🏢 Costi fissi annui", 0, 1_000_000, 50000),
        "Investimento iniziale (€)": st.sidebar.number_input("💵 Investimento iniziale", 0, 5_000_000, 5000000)
    }

    # --- CALCOLI ---
    years = 7
    students_year = inputs["Numero studenti primo anno"]
    data = []

    for y in range(1, years+1):
        revenue = students_year * inputs["Retta/studente (€)"]

        # 📌 Insegnanti: rapporto 10,4 studenti per docente, minimo 4
        required_teachers = max(4, int(np.ceil(students_year / 10.4)))
        hours_per_teacher_year = inputs["Ore/settimana per insegnante"] * inputs["Settimane/anno"]
        payroll = required_teachers * hours_per_teacher_year * inputs["Costo/ora insegnante (€)"]

        variable_costs = students_year * 300
        fixed_costs = inputs["Costi fissi annui (€)"]
        total_costs = payroll + variable_costs + fixed_costs
        ebit = revenue - total_costs

        data.append({
            "Anno": y,
            "Studenti": round(students_year),
            "Insegnanti": required_teachers,
            "Ricavi": round(revenue),
            "Stipendi": round(payroll),
            "Costi Variabili": round(variable_costs),
            "Costi Fissi": round(fixed_costs),
            "Totale Costi": round(total_costs),
            "EBIT": round(ebit)
        })

        students_year *= (1 + inputs["Crescita annua (%)"] / 100)

    df_result = pd.DataFrame(data)

    # --- KPI CARDS ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👩‍🎓 Studenti 1° anno", inputs["Numero studenti primo anno"])
    col2.metric("💶 Retta per studente", f"€ {inputs['Retta/studente (€)']:,}")
    col3.metric("📈 EBIT anno 7", f"€ {df_result.iloc[-1]['EBIT']:,}")
    col4.metric("🏢 Costi fissi annui", f"€ {inputs['Costi fissi annui (€)']:,}")

    # --- TABS ---
    tab1, tab2, tab3 = st.tabs(["📊 Proiezioni", "📈 Grafici", "📑 Conto Economico"])

    # --- TAB 1 ---
    with tab1:
        st.subheader("📊 Proiezioni finanziarie")
        st.dataframe(df_result, use_container_width=True)

    # --- TAB 2 ---
    with tab2:
        st.subheader("📈 Andamento Ricavi / Costi / EBIT")
        fig_line = px.line(df_result, x="Anno", y=["Ricavi", "Totale Costi", "EBIT"], markers=True)
        st.plotly_chart(fig_line, use_container_width=True)

        st.subheader("📊 Struttura costi")
        fig_bar = px.bar(df_result, x="Anno", y=["Stipendi", "Costi Fissi", "Costi Variabili"], barmode="stack")
        st.plotly_chart(fig_bar, use_container_width=True)

        st.subheader("📉 Rapporto studenti/insegnante")
        df_result["Studenti per Insegnante"] = df_result["Studenti"] / df_result["Insegnanti"]
        fig_ratio = px.line(df_result, x="Anno", y="Studenti per Insegnante", markers=True)
        st.plotly_chart(fig_ratio, use_container_width=True)

    # --- TAB 3 ---
    with tab3:
        st.subheader("📑 Conto Economico")

        # Selezione anno
        selected_year = st.selectbox("Seleziona l'anno:", df_result["Anno"].tolist())
        row = df_result[df_result["Anno"] == selected_year].iloc[0]

        # --- Calcolo conto economico strutturato ---
        students_total = row["Studenti"]
        revenue = row["Ricavi"]

        contributi = 0
        altri_proventi = 0
        totale_altri = contributi + altri_proventi
        totale_valore_produzione = revenue + totale_altri

        # Costi
        materie_prime = students_total * 50
        servizi = 20000
        godimento_beni = 0

        salari = row["Stipendi"]
        oneri_sociali = salari * 0.3
        tfr = salari * 0.05
        quiescenza = salari * 0.02
        altri_costi_personale = 1000
        totale_personale = salari + oneri_sociali + tfr + quiescenza + altri_costi_personale

        totale_costi_produzione = materie_prime + servizi + godimento_beni + totale_personale
        utile = totale_valore_produzione - totale_costi_produzione

        ce_data = {
            "Voce": [
                "A) Valore della produzione",
                "   Ricavi delle vendite e delle prestazioni",
                "   Altri ricavi e proventi",
                "      Contributi in conto esercizio",
                "      Altri proventi",
                "   Totale altri ricavi e proventi",
                "Totale valore della produzione",
                "B) Costi della produzione",
                "   Per materie prime, sussidiarie, di consumo e merci",
                "   Per servizi",
                "   Per godimento di beni di terzi",
                "   Per il personale",
                "      a) Salari e stipendi",
                "      b) Oneri sociali",
                "      c) Trattamento di fine rapporto",
                "      d) Trattamento di quiescenza",
                "      e) Altri costi del personale",
                "   Totale costi per il personale",
                "Totale costi della produzione",
                "Utile (perdita) dell'esercizio"
            ],
            "Valore (€)": [
                "", round(revenue), "", round(contributi), round(altri_proventi), round(totale_altri),
                round(totale_valore_produzione),
                "", round(materie_prime), round(servizi), round(godimento_beni), "",
                round(salari), round(oneri_sociali), round(tfr), round(quiescenza), round(altri_costi_personale),
                round(totale_personale), round(totale_costi_produzione), round(utile)
            ]
        }

        df_ce = pd.DataFrame(ce_data)
        st.dataframe(df_ce, use_container_width=True)

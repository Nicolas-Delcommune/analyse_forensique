import streamlit as st
import pandas as pd
import plotly.express as px

def detect_suspect_transactions(df):
    df['date'] = pd.to_datetime(df['date'])

    montant_mean = df['montant'].mean()
    montant_std = df['montant'].std()
    seuil_montant = montant_mean + 2 * montant_std
    flag_montant = df['montant'] > seuil_montant

    tx_freq = df.groupby(['client_id', 'date']).size().reset_index(name='nb_tx')
    tx_freq = tx_freq[tx_freq['nb_tx'] > 5]
    df = df.merge(tx_freq, on=['client_id', 'date'], how='left')
    df['nb_tx'] = df['nb_tx'].fillna(0)
    freq_ids = df['nb_tx'] > 5

    multi_cp = df.groupby(['client_id', 'date'])['code_postal'].nunique().reset_index(name='nb_cp')
    df = df.merge(multi_cp, on=['client_id', 'date'], how='left', suffixes=('', '_cp'))
    df['nb_cp'] = df['nb_cp'].fillna(1)
    geo_anomaly = df['nb_cp'] > 1

    df['key'] = df['client_id'] + '_' + df['date'].astype(str) + '_' + df['montant'].astype(str)
    duplicated = df.duplicated(subset='key', keep=False)

    # Calcul du score
    df['suspicious'] = False
    df['reason'] = ''
    df['score'] = 0

    df.loc[flag_montant, 'reason'] = df.loc[flag_montant, 'reason'] + 'Montant élevé; '
    df.loc[flag_montant, 'score'] += 40
    df.loc[flag_montant, 'suspicious'] = True

    df.loc[freq_ids, 'reason'] = df.loc[freq_ids, 'reason'] + 'Fréquence élevée; '
    df.loc[freq_ids, 'score'] += 30
    df.loc[freq_ids, 'suspicious'] = True

    df.loc[geo_anomaly, 'reason'] = df.loc[geo_anomaly, 'reason'] + 'Déplacements suspects; '
    df.loc[geo_anomaly, 'score'] += 20
    df.loc[geo_anomaly, 'suspicious'] = True

    df.loc[duplicated, 'reason'] = df.loc[duplicated, 'reason'] + 'Doublons; '
    df.loc[duplicated, 'score'] += 10
    df.loc[duplicated, 'suspicious'] = True

    return df[df['suspicious']].copy()


# Chargement des données
df = pd.read_csv('transactions.csv')
df['date'] = pd.to_datetime(df['date'])

# Titre
st.title("Dashboard Forensique - Transactions Bancaires")

# Filtres
st.sidebar.header("Filtres")

clients = st.sidebar.multiselect("Client ID", options=sorted(df['client_id'].unique()), default=None)
types = st.sidebar.multiselect("Type d'opération", options=df['type_operation'].unique(), default=None)
min_montant, max_montant = st.sidebar.slider("Montant ($)", float(df['montant'].min()), float(df['montant'].max()), (float(df['montant'].min()), float(df['montant'].max())))
dates = st.sidebar.date_input("Plage de dates", [df['date'].min(), df['date'].max()])

# Application des filtres
filtered_df = df.copy()
if clients:
    filtered_df = filtered_df[filtered_df['client_id'].isin(clients)]
if types:
    filtered_df = filtered_df[filtered_df['type_operation'].isin(types)]
filtered_df = filtered_df[(filtered_df['montant'] >= min_montant) & (filtered_df['montant'] <= max_montant)]
filtered_df = filtered_df[(filtered_df['date'] >= pd.to_datetime(dates[0])) & (filtered_df['date'] <= pd.to_datetime(dates[1]))]

st.subheader(f"{len(filtered_df)} transactions filtrées")
st.dataframe(filtered_df)

# Visualisation 1 : Montant total par type d'opération
fig1 = px.bar(filtered_df.groupby('type_operation')['montant'].sum().reset_index(),
              x='type_operation', y='montant', title="Montant total par type d'opération")
st.plotly_chart(fig1)

# Visualisation 2 : Transactions dans le temps
fig2 = px.histogram(filtered_df, x='date', nbins=30, title="Nombre de transactions par jour")
st.plotly_chart(fig2)

# Visualisation 3 : Répartition des montants par client
fig3 = px.box(filtered_df, x='client_id', y='montant', title="Répartition des montants par client")
st.plotly_chart(fig3)

#suspect transactions
st.subheader("Transactions suspectes détectées automatiquement")

suspect_df = detect_suspect_transactions(filtered_df)

if not suspect_df.empty:
    st.dataframe(suspect_df[['id_transaction', 'date', 'client_id', 'montant', 'type_operation', 'code_postal', 'reason']])
else:
    st.success("Aucune transaction suspecte détectée avec les règles actuelles.")


st.markdown("###Filtres sur les transactions suspectes")

# Liste des types de suspicion disponibles
all_reasons = ['Montant élevé', 'Fréquence élevée', 'Déplacements suspects', 'Doublons']
selected_reasons = st.multiselect("Type(s) de suspicion :", all_reasons, default=all_reasons)

score_min = st.slider("Score de suspicion minimum", 0, 100, 10, step=5)

# Filtrage
filtered_suspect_df = suspect_df[
    suspect_df['reason'].apply(lambda x: any(r in x for r in selected_reasons)) &
    (suspect_df['score'] >= score_min)
]

st.write(f"{len(filtered_suspect_df)} transaction(s) suspecte(s) après filtrage :")
st.dataframe(filtered_suspect_df[['id_transaction', 'date', 'client_id', 'montant', 'type_operation', 'code_postal', 'reason', 'score']])
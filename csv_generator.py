import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker('fr_CA')

# Configurations
nb_transactions = 1000
clients = [f"C{str(i).zfill(3)}" for i in range(1, 31)]
types_operations = ['achat', 'virement', 'retrait', 'paiement facture', 'transfert interne']
codes_postaux = ['H2X 1A4', 'H2Y 2B5', 'G1V 0A6', 'H1W 3K2', 'G1R 2L6']

# Génération de données
transactions = []

start_date = datetime(2025, 5, 1)
end_date = datetime(2025, 6, 30)

for i in range(nb_transactions):
    id_tx = f"TX{str(i+1).zfill(5)}"
    date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
    montant = round(random.uniform(5.00, 10000.00), 2)
    client = random.choice(clients)
    code_postal = random.choice(codes_postaux)
    type_op = random.choice(types_operations)

    transactions.append({
        'id_transaction': id_tx,
        'date': date.strftime('%Y-%m-%d'),
        'montant': montant,
        'client_id': client,
        'code_postal': code_postal,
        'type_operation': type_op
    })

# Création du DataFrame
df = pd.DataFrame(transactions)

fraude_transactions = [
    {
        'id_transaction': f"TXFRAUDE{i+1:03}",
        'date': '2025-06-15',
        'montant': 9999.99,  # Montant anormal
        'client_id': 'C999',
        'code_postal': random.choice(['H2X 1A4', 'G1V 0A6']),
        'type_operation': 'virement'
    }
    for i in range(5)
]

# Doublons mêmes montant/date/client
fraude_transactions += [
    {
        'id_transaction': f"TXFRAUDE{i+6:03}",
        'date': '2025-06-15',
        'montant': 222.22,
        'client_id': 'C998',
        'code_postal': 'H1W 3K2',
        'type_operation': 'retrait'
    }
    for i in range(3)
]



# Même client, même jour, codes postaux différents
fraude_transactions += [
    {
        'id_transaction': f"TXFRAUDE009",
        'date': '2025-06-20',
        'montant': 300.00,
        'client_id': 'C997',
        'code_postal': 'G1R 2L6',
        'type_operation': 'achat'
    },
    {
        'id_transaction': f"TXFRAUDE010",
        'date': '2025-06-20',
        'montant': 500.00,
        'client_id': 'C997',
        'code_postal': 'H2Y 2B5',
        'type_operation': 'achat'
    },
    {
        'id_transaction': f"TXFRAUDE011",
        'date': '2025-06-20',
        'montant': 500000000000.00,
        'client_id': 'C997',
        'code_postal': 'H2Y 2B5',
        'type_operation': 'achat'
    },
    {
        'id_transaction': f"TXFRAUDE012",
        'date': '2025-06-20',
        'montant': 500.00,
        'client_id': 'C997',
        'code_postal': 'H2Y 2B5',
        'type_operation': 'achat'
    }
]

fraude_transactions += [
    {
        'id_transaction': f"TXFRAUDE{i+13:03}",
        'date': '2025-06-15',
        'montant': 1000,
        'client_id': 'C998',
        'code_postal': 'H1W 3K2',
        'type_operation': 'virement'
    }
    for i in range(7)
]

# Ajouter au DataFrame existant
df_fraude = pd.DataFrame(fraude_transactions)
df = pd.concat([df, df_fraude], ignore_index=True)

df.to_csv('transactions.csv', index=False)
print("Fichier 'transactions.csv' généré.")

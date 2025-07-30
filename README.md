# Analyse Forensique - Générateur de Données Financières

Ce projet de test contient des outils pour générer et visualiser des données de transactions financières à des fins d'analyse forensique.

### `csv_generator.py`
**Description :** Script de génération de données de transactions financières fictives.

**Fonctionnalités :**
- Génère 1000 transactions avec des données réalistes
- Utilise des codes postaux canadiens
- Types d'opérations : achat, virement, retrait, paiement facture, transfert interne
- Sortie : fichier `transactions.csv`

**Utilisation :**
```bash
python csv_generator.py
```

### `visualisation.py`
**Description :** Interface de visualisation interactive des données de transactions utilisant Streamlit.

**Fonctionnalités :**
- Visualisation graphique des transactions
- Analyse interactive des données
- Interface web

**Utilisation :**
```bash
streamlit run visualisation.py
```

## Visualisation Power BI
- Interface de visualisation interactive des données utilisant Power BI.
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
from pandas import json_normalize
import numpy as np
import pymongo
import plotly.express as px

# Connexion à la base de données MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["gs"]
events_collection = db["events"]
competitions_collection = db["competitions"]

# Charger les données depuis la collection events
events_data = list(events_collection.find())
df_events = pd.DataFrame(events_data)

# Charger les données depuis la collection competitions
competitions_data = list(competitions_collection.find())
df_competitions = pd.DataFrame(competitions_data)

# titre de l'application Streamlit
st.title('GameStats ⚽️🏟️')

# Ajout de la séparation
st.markdown("---")

# Heatmap des passes
st.subheader('Heatmap des passes')

# Sidebar pour la sélection des matchs
selected_match = st.sidebar.selectbox('Sélectionnez un match :', df_events['match'].unique())

# Filtre des données pour le match sélectionné
df_selected_match = df_events[df_events['match'] == selected_match]

# Filtre des passes faites par l'équipe sélectionnée
df_pass = df_selected_match[df_selected_match['type_name'] == "Pass"]

# Enregistrement de la localisation de l'événement en une série à 2 colonnes
location_xy = pd.DataFrame(df_pass['location'].tolist(), columns=['x', 'y'])

# Renommer les colonnes x et y
location_xy.columns = ['x', 'y']

# Suppression des valeurs manquantes
location_xy.dropna(inplace=True)

# Création d'une figure et des sous-graphiques
fig, ax = plt.subplots(figsize=(10, 7))

# Heatmap
heatmap = ax.hist2d(location_xy['x'], location_xy['y'], bins=25, cmap='coolwarm')

# Ajouter un titre et des labels
ax.set_title('Heatmap des passes')
ax.set_xlabel('X')
ax.set_ylabel('Y')

# Afficher les graphiques Matplotlib dans Streamlit
st.pyplot(fig)

# Ajout de la séparation
st.markdown("---")

# Visualisation des actions d'un joueur sur le terrain
st.subheader('Actions des Joueurs sur le terrain')

# Créer une liste déroulante pour sélectionner un joueur
selected_player = st.selectbox('Sélectionnez un joueur :', df_events['player_name'].unique())

# Filtrer les actions du joueur sélectionné
df_selected_player = df_events[df_events['player_name'] == selected_player]

# Création d'une figure pour le terrain
fig, ax = plt.subplots(figsize=(12, 8))
ax.set_title('Actions du joueur sur le terrain')

# Heatmap
heatmap = ax.hist2d(df_selected_player['location_x'], df_selected_player['location_y'], bins=25, cmap='coolwarm')

# Ajouter un titre et des labels
ax.set_xlabel('X')
ax.set_ylabel('Y')

# Afficher les graphiques Matplotlib dans Streamlit
st.pyplot(fig)

# Ajout de la séparation
st.markdown("---")

# Définir le titre de l'application Streamlit
st.title('Relation entre données')

# Sélection de la variable pour l'axe x
x_variable = st.selectbox("Sélectionnez la variable pour l'axe x :", df_events.columns)

# Sélection de la variable pour l'axe y
y_variable = st.selectbox("Sélectionnez la variable pour l'axe y :", df_events.columns)

# Bouton pour visualiser les données avec les variables sélectionnées
if st.button("Visualiser"):
    # Affichage du nuage de points interactif avec les variables sélectionnées
    fig = px.scatter(df_events, x=x_variable, y=y_variable, color='team_name', hover_name='player_name', 
                     title='Relation entre donées', 
                     labels={x_variable: 'X', y_variable: 'Y'})
    # Afficher le nuage de points interactif
    st.plotly_chart(fig)

# Ajout de la séparation
st.markdown("---")

# Évolution de la possession de balle
st.title('Évolution de la possession de balle')

# Calculer la possession de balle pour chaque équipe à chaque minute
possession_data = df_events.groupby(['minute', 'team_name']).size().unstack(fill_value=0)

# Créer un graphique montrant l'évolution de la possession de balle des deux équipes
fig, ax = plt.subplots(figsize=(10, 6))
possession_data.plot(ax=ax)
ax.set_xlabel('Minute')
ax.set_ylabel('Possession de balle')
ax.legend(title='Équipe')

# Afficher le graphique dans Streamlit
st.pyplot(fig)

# Ajout de la séparation
st.markdown("---")

# Répartition des actions par équipe
st.title('Répartition des actions par équipe')

# Créer un DataFrame pour les actions par type et par équipe
df_actions_by_team = df_events.groupby(['team_name', 'type_name']).size().unstack(fill_value=0)

# Créer des graphiques en barres pour montrer la répartition des actions par type pour chaque équipe
for team in df_actions_by_team.index:
    team_data = df_actions_by_team.loc[[team]]
    fig, ax = plt.subplots(figsize=(12, 8))
    bar_width = 0.35  # Largeur des barres
    index = np.arange(len(team_data))  # Position des types d'action sur l'axe x

    # Plot pour chaque type d'action
    for i, action_type in enumerate(team_data.columns):
        ax.bar(index + i * bar_width, team_data[action_type], bar_width, label=action_type)

    # Définition des étiquettes et du titre
    ax.set_xlabel('Type d\'action')
    ax.set_ylabel('Nombre d\'actions')
    ax.set_xticks(index + bar_width / 2)
    ax.set_xticklabels(team_data.index)
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.5), ncol=3)  # Placer la légende en bas du graphique

    # Affichage du graphique en barres dans Streamlit
    st.pyplot(fig)

# Ajout de la séparation
st.markdown("---")

# Pied de page avec les informations de contact
st.markdown(
    """ 
    Created by [Moussa Mar](https://www.linkedin.com/in/moussamar/)<br>
    Project inspired by [StatsBomb Open Dataset Challenge](https://statsbomb.com/open-dataset-challenge/)</s>
    ---\n
    Contact : marmoussa24@gmail.com\n
    Twitter : [GameStats](https://twitter.com/GameStats)
    """
)

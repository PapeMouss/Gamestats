import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
from pandas import json_normalize
import numpy as np
from mplsoccer import Radar, FontManager, Pitch
import seaborn as sns
import plotly.express as px
import pymongo
from pymongo import MongoClient

# Charger les données JSON depuis des fichiers locaux
# events_files = {
#     'France vs Croatie CDM 2018': 'data/8658.json',
#     'Croatie vs Ruusie CDM 2018': 'data/8652.json',
#     'Belgique vs France CDM 2018': 'data/8655.json',
#     'Belgique vs Angleterre CDM 2018': 'data/8657.json'
#     # Ajouter d'autres jeux de données ici avec leur nom de match correspondant
# }

# Connexion à la base de données MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["GameStats"]

# Liste des noms de collections
events_files = ["15946", "8652", "8655", "8657", "8655",  "8658",  "competitions"]



# Sidebar pour la sélection des matchs
selected_match = st.sidebar.selectbox('Sélectionnez un match :', events_files)

# Charger les données JSON du match sélectionné
with open(events_files[selected_match], 'r') as file:
    events = json.load(file)
# Transformer JSON en DataFrame
df = json_normalize(events, sep="_")
st.title("Analyse des statistique")
# Définir le titre de l'application Streamlit
st.title('GameStats ⚽️🏟️')

# Heatmap des passes
st.subheader('Heatmap des passes')
# Filtrer les passes faites par l'équipe sélectionnée
df_pass = df.loc[(df['type_name'] == "Pass") & (df['team_name'].isin(["France", "Croatie", "Belgique", "Angleterre"]))]
# Enregistrer la localisation de l'événement en une série à 2 colonnes
location_xy = pd.DataFrame(df_pass['location'].tolist(), columns=['x', 'y'])
# Renommer les colonnes x et y
location_xy.columns = ['x', 'y']
# Supprimer les valeurs manquantes
location_xy.dropna(inplace=True)
# Créer une instance de la classe Pitch
pitch = Pitch(pitch_type='statsbomb')
# Créer une figure et des sous-graphiques
fig, ax = plt.subplots(1, 3, figsize=(20, 7))

# Heatmap spécifié
bins = [(6, 5), (1, 5), (6, 1)]
for i, bin in enumerate(bins):
    # Compter le nombre d'occurrences
    bin_statistic = pitch.bin_statistic(location_xy['x'], location_xy['y'], statistic='count', bins=bin)
    # Dessiner la heatmap
    pitch.heatmap(bin_statistic, ax=ax[i], cmap='coolwarm', edgecolors='#22321b')
    # Dessiner des points d'événements sur le terrain
    pitch.scatter(location_xy.x, location_xy.y, c='white', s=20, ax=ax[i])
    # Dessiner les étiquettes de la heatmap
    pitch.label_heatmap(bin_statistic, color='black', fontsize=18, ax=ax[i], ha='center', va='bottom')
    # Calculer les pourcentages et formater les valeurs
    percent_statistic = (bin_statistic['statistic'] / bin_statistic['statistic'].sum()) * 100
    formatted_percentages = np.around(percent_statistic, decimals=0).astype(int)
    # Convertir les valeurs formatées en chaînes avec le symbole de pourcentage
    formatted_percentages = [f"{val}%" for val in formatted_percentages]
    # Remplacer les lignes avec les pourcentages
    bin_statistic['statistic'] = formatted_percentages

# Afficher les graphiques Matplotlib dans Streamlit
st.pyplot(fig)

###############

# Ajout de la séparation
st.markdown("---")

# Visualisation des actions d'un joueur sur le terrain
st.subheader('Actions des Joueurs sur le terrain')
# Créer une liste déroulante pour sélectionner un joueur
selected_player = st.selectbox('Sélectionnez un joueur :', df['player_name'].unique())
# Filtrer les actions du joueur sélectionné
df_selected_player = df[df['player_name'] == selected_player]
# Créer une instance de la classe Pitch
pitch = Pitch(pitch_type='statsbomb')
# Créer une figure pour le terrain
fig, ax = plt.subplots(figsize=(12, 8))
# Dessiner le terrain
pitch.draw(ax=ax)
# Afficher les actions du joueur sur le terrain
for index, row in df_selected_player.iterrows():
    if row['type_name'] == 'Pass':
        ax.plot([row['location'][0], row['pass_end_location'][0]],
                [row['location'][1], row['pass_end_location'][1]], color='blue')
        ax.plot(row['location'][0], row['location'][1], 'o', color='blue')  # Marquer le départ du passe
        ax.plot(row['pass_end_location'][0], row['pass_end_location'][1], 'x', color='blue')  # Marquer la fin du passe
    elif row['type_name'] == 'Shot':
        ax.plot(row['location'][0], row['location'][1], 'o', color='red')  # Marquer l'emplacement du tir
# Afficher le terrain avec les actions du joueur
st.pyplot(fig)

######################

# Ajout de la séparation
st.markdown("---")

import plotly.express as px

# Créer un nuage de points interactif pour montrer la relation entre les passes et les tirs
fig = px.scatter(df, x='location', y='pass_aerial_won', color='team_name', hover_name='player_name', 
                 title='Relation entre les passes et les tirs', 
                 labels={'location': 'tirs_xg', 'pass_aerial_won': 'Nombre de tirs'})
# Afficher le nuage de points interactif
st.plotly_chart(fig)

###############
# Ajout de la séparation
st.markdown("---")

# Définir le titre de l'application Streamlit
st.title('Évolution de la possession de balle')

# Calculer la possession de balle pour chaque équipe à chaque minute
# Vous devrez adapter cette partie selon la structure de vos données JSON
# Ici, nous supposons que chaque événement a un champ 'team_name' indiquant l'équipe qui a la possession
# et un champ 'timestamp' indiquant le temps de l'événement
df['timestamp'] = pd.to_datetime(df['timestamp'])  # Convertir le champ timestamp en type datetime
df['minute'] = df['timestamp'].dt.minute  # Extraire la minute de l'heure
possession_data = df.groupby(['minute', 'team_name']).size().unstack(fill_value=0)

# Créer un graphique montrant l'évolution de la possession de balle des deux équipes
fig, ax = plt.subplots(figsize=(10, 6))
possession_data.plot(ax=ax)
ax.set_xlabel('Minute')
ax.set_ylabel('Possession de balle')
ax.set_title('Évolution de la possession de balle')
ax.legend(title='Équipe')

# Afficher le graphique dans Streamlit
st.pyplot(fig)


###############

# Ajout de la séparation
st.markdown("---")

# Répartition des actions par équipe
st.title('Répartition des actions par équipe')

# Créer un DataFrame pour les actions par type et par équipe
df_actions_by_team = df.groupby(['team_name', 'type_name']).size().unstack(fill_value=0)

# Créer un graphique en barres pour montrer la répartition des actions par type pour chaque équipe
for team in df_actions_by_team.index:
    team_data = df_actions_by_team.loc[[team]]
    fig, ax = plt.subplots(figsize=(12, 8))
    bar_width = 0.35  # Largeur des barres
    index = np.arange(len(team_data))  # Position des types d'action sur l'axe x

    # Plot pour chaque type d'action
    for i, action_type in enumerate(team_data.columns):
        ax.bar(index + i * bar_width, team_data[action_type], bar_width, label=action_type)

    # Définir les étiquettes et le titre
    ax.set_xlabel('Type d\'action')
    ax.set_ylabel('Nombre d\'actions')
    ax.set_xticks(index + bar_width / 2)
    ax.set_xticklabels(team_data.index)
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.5), ncol=3)  # Placer la légende en bas du graphique

    # Afficher le graphique en barres dans Streamlit
    st.pyplot(fig)


###############
st.title('Répartition des actions par équipe')

# Sélectionner une équipe
selected_team = st.selectbox('Sélectionnez une équipe :', df['team_name'].unique())

# Filtrer les données pour l'équipe sélectionnée
df_selected_team = df[df['team_name'] == selected_team]

# Calculer le nombre total d'actions pour l'équipe sélectionnée
total_actions = df_selected_team.shape[0]

# Calculer le nombre d'actions par type pour l'équipe sélectionnée
actions_counts = df_selected_team['type_name'].value_counts()

# Filtrer les types d'actions pour ne garder que les plus significatifs (par exemple, les types d'actions avec plus de 5% du total)
threshold = total_actions * 0.03
relevant_actions_counts = actions_counts[actions_counts > threshold]

# Créer un pie chart pour la répartition des actions par type (uniquement pour les types d'actions les plus significatifs)
fig, ax = plt.subplots()
ax.pie(relevant_actions_counts, labels=relevant_actions_counts.index, autopct='%1.1f%%', startangle=90)
ax.axis('equal')  # Assure que le pie chart est dessiné comme un cercle
#ax.set_title(f'Répartition des actions les plus pertinentes par type pour {selected_team}')

# Afficher le pie chart dans Streamlit
st.pyplot(fig)
######################
# Ajout de la séparation
st.markdown("---")

import json
import pandas as pd
import plotly.express as px

# Charger les données JSON
with open('data/competitions.json', 'r') as file:
    competition_data = json.load(file)

# Convertir les données en DataFrame pandas
df = pd.DataFrame(competition_data)

st.title('Répartition des actions par équipe')

# Compter le nombre de compétitions par pays
competition_counts = df['country_name'].value_counts().reset_index()
competition_counts.columns = ['Country', 'Competition Count']

# Créer une carte choroplèthe
fig = px.choropleth(competition_counts, 
                    locations="Country", 
                    locationmode='country names',
                    color="Competition Count", 
                    hover_name="Country", 
                    color_continuous_scale=px.colors.sequential.Plasma)

# Titre et mise en page de la carte
#fig.update_layout(title_text='Répartition géographique des compétitions par pays')
fig.update_geos(projection_type="orthographic", showcoastlines=True, showland=True, 
                showocean=True, oceancolor="LightBlue")

# Afficher la carte dans Streamlit
st.plotly_chart(fig)


#####################

# Ajout séparation
st.markdown("---")

# Pied de page avec les informations de contact
st.markdown(
    """
    ---\n
    Contact : marmoussa24@gmail.com\n
    Twitter : [GameStats](https://twitter.com/GameStats)
    """
)

########################


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
from pandas import json_normalize
import numpy as np
from mplsoccer import Radar, FontManager, Pitch, PyPizza, add_image
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
from PIL import Image
import pymongo

#from mplsoccer import Sbapi        #api for getting data from StatsBomb

#font 
font_normal = FontManager('https://raw.githubusercontent.com/googlefonts/roboto/main/'
                          'src/hinted/Roboto-Regular.ttf')
font_italic = FontManager('https://raw.githubusercontent.com/googlefonts/roboto/main/'
                          'src/hinted/Roboto-Italic.ttf')
font_bold = FontManager('https://raw.githubusercontent.com/google/fonts/main/apache/robotoslab/'
                        'RobotoSlab[wght].ttf')

############

# Chargement des données JSON depuis des fichiers locaux
events_files = {
    'France vs Croatie CDM 2018': '/Users/moussamar/Desktop/statsbomb_test/data/8658.json',
    'Croatie vs Ruusie CDM 2018': '/Users/moussamar/Desktop/statsbomb_test/data/8652.json',
    'Belgique vs France CDM 2018': '/Users/moussamar/Desktop/statsbomb_test/data/8655.json',
    'Belgique vs Angleterre CDM 2018': '/Users/moussamar/Desktop/statsbomb_test/data/8657.json'
    # d'autres jeux de données ici avec leur nom de match correspondant
}

# Sidebar pour la sélection des matchs
selected_match = st.sidebar.selectbox('Sélectionnez un match :', list(events_files.keys()))

#######@

# Chargement des données JSON du match sélectionné
with open(events_files[selected_match], 'r') as file:
    events = json.load(file)
# Transformation JSON en DataFrame
df = json_normalize(events, sep="_")

#######

# titre de l'application Streamlit
st.title('GameStats ⚽️🏟️')

######################################

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


##########@

# Ajout de la séparation
st.markdown("---")

# Heatmap des passes
st.subheader('Heatmap des passes')

# Sidebar pour la sélection des matchs et éléments décoratifs
with st.sidebar:
    # Logo ou image décorative
    st.image("/Users/moussamar/Desktop/statsbomb_test/l4.jpg",use_column_width=True, width=200)
    # Titre décoratif
    st.markdown("<h1 style='text-align: center;'>GameStats</h1>", unsafe_allow_html=True)
    # Ajouter un texte ou une phrase inspirante
    st.markdown("> *Analysez les statistiques des matchs de football et tirez des insights intéressants.*")
    # Ajouter une vidéo d'introduction ou une animation
    st.video("https://example.com/your-intro-video.mp4")
    # Ajouter des liens vers les réseaux sociaux ou d'autres plateformes
    st.markdown("### Suivez-nous sur les réseaux sociaux :")
    st.markdown("[Twitter](https://twitter.com/GameStats) | [Instagram](https://instagram.com/GameStats) | [Facebook](https://facebook.com/GameStats)")


# Filtre des passes faites par l'équipe sélectionnée
df_pass = df.loc[(df['type_name'] == "Pass") & (df['team_name'].isin(["France", "Croatie", "Belgique", "Angleterre"]))]
# Enregistrement de la localisation de l'événement en une série à 2 colonnes
location_xy = pd.DataFrame(df_pass['location'].tolist(), columns=['x', 'y'])
# Renommer les colonnes x et y
location_xy.columns = ['x', 'y']
# Suppression les valeurs manquantes
location_xy.dropna(inplace=True)
# Création d'une instance de la classe Pitch
pitch = Pitch(pitch_type='statsbomb')
# Création d'une figure et des sous-graphiques
fig, ax = plt.subplots(1, 3, figsize=(20, 7))

# Heatmap spécifié
bins = [(6, 5), (1, 5), (6, 1)]
for i, bin in enumerate(bins):
    # Comptage le nombre d'occurrences
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

# Définir le titre de l'application Streamlit
st.title('Relation entre données')

import plotly.express as px

# Liste des variables disponibles
variables = ['id', 'index', 'period', 'timestamp', 'minute', 'second', 'possession', 'duration', 'type_id', 'type_name', 'possession_team_id', 'possession_team_name', 'play_pattern_id', 'play_pattern_name', 'team_id', 'team_name', 'tactics_formation', 'tactics_lineup', 'related_events', 'location', 'player_id', 'player_name', 'position_id', 'position_name', 'pass_recipient_id', 'pass_recipient_name', 'pass_length', 'pass_angle', 'pass_height_id', 'pass_height_name', 'pass_end_location', 'pass_type_id', 'pass_type_name', 'pass_body_part_id', 'pass_body_part_name', 'carry_end_location', 'under_pressure', 'pass_outcome_id', 'pass_outcome_name', 'ball_receipt_outcome_id', 'ball_receipt_outcome_name', 'duel_type_id', 'duel_type_name', 'pass_aerial_won', 'duel_outcome_id', 'duel_outcome_name', 'counterpress', 'interception_outcome_id', 'interception_outcome_name', 'pass_switch', 'pass_cross', 'dribble_outcome_id', 'dribble_outcome_name', 'foul_committed_type_id', 'foul_committed_type_name', 'foul_won_defensive', 'clearance_aerial_won', 'ball_recovery_recovery_failure', 'foul_committed_advantage', 'foul_won_advantage', 'injury_stoppage_in_chain', 'pass_backheel', 'pass_assisted_shot_id', 'pass_shot_assist', 'shot_statsbomb_xg', 'shot_end_location', 'shot_key_pass_id', 'shot_technique_id', 'shot_technique_name', 'shot_type_id', 'shot_type_name', 'shot_outcome_id', 'shot_outcome_name', 'shot_body_part_id', 'shot_body_part_name', 'shot_freeze_frame', 'goalkeeper_end_location', 'goalkeeper_type_id', 'goalkeeper_type_name', 'goalkeeper_position_id', 'goalkeeper_position_name', 'goalkeeper_outcome_id', 'goalkeeper_outcome_name', 'foul_committed_card_id', 'foul_committed_card_name', 'pass_goal_assist', 'shot_deflected', 'block_deflection', 'foul_committed_penalty', 'pass_cut_back', 'shot_aerial_won', 'shot_first_time', 'goalkeeper_technique_id', 'goalkeeper_technique_name', 'goalkeeper_body_part_id', 'goalkeeper_body_part_name', 'pass_deflected', 'dribble_overrun', 'substitution_outcome_id', 'substitution_outcome_name', 'substitution_replacement_id', 'substitution_replacement_name']

# Sélection de la variable pour l'axe x
x_variable = st.selectbox("Sélectionnez la variable pour l'axe x :", variables)

# Sélection de la variable pour l'axe y
y_variable = st.selectbox("Sélectionnez la variable pour l'axe y :", variables)

# Bouton pour visualiser les données avec les variables sélectionnées
if st.button("Visualiser"):
    # Affichage du nuage de points interactif avec les variables sélectionnées
    fig = px.scatter(df, x=x_variable, y=y_variable, color='team_name', hover_name='player_name', 
                     title='Relation entre donées', 
                     labels={x_variable: 'X', y_variable: 'Y'})
    # Afficher le nuage de points interactif
    st.plotly_chart(fig)

##############

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
#ax.set_title('Évolution de la possession de balle')
ax.legend(title='Équipe')

# Afficher le graphique dans Streamlit
st.pyplot(fig)


###############

#############

# Ajout de la séparation
st.markdown("---")

# Répartition des actions par équipe
st.title('Répartition des actions par équipe')

# Création un DataFrame pour les actions par type et par équipe
df_actions_by_team = df.groupby(['team_name', 'type_name']).size().unstack(fill_value=0)

# Création d' un graphique en barres pour montrer la répartition des actions par type pour chaque équipe
for team in df_actions_by_team.index:
    team_data = df_actions_by_team.loc[[team]]
    fig, ax = plt.subplots(figsize=(12, 8))
    bar_width = 0.35  # Largeur des barres
    index = np.arange(len(team_data))  # Position des types d'action sur l'axe x

    # Plot pour chaque type d'action
    for i, action_type in enumerate(team_data.columns):
        ax.bar(index + i * bar_width, team_data[action_type], bar_width, label=action_type)

    # Définition les étiquettes et le titre
    ax.set_xlabel('Type d\'action')
    ax.set_ylabel('Nombre d\'actions')
    ax.set_xticks(index + bar_width / 2)
    ax.set_xticklabels(team_data.index)
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.5), ncol=3)  # Placer la légende en bas du graphique

    # Affichage le graphique en barres dans Streamlit
    st.pyplot(fig)


###############
# Ajout de la séparation
st.markdown("---")

st.title('Répartition des actions par équipe')

# Sélection une équipe
selected_team = st.selectbox('Sélectionnez une équipe :', df['team_name'].unique())

# Filtre les données pour l'équipe sélectionnée
df_selected_team = df[df['team_name'] == selected_team]

# Calcul du nombre total d'actions pour l'équipe sélectionnée
total_actions = df_selected_team.shape[0]

# Calcul du nombre d'actions par type pour l'équipe sélectionnée
actions_counts = df_selected_team['type_name'].value_counts()

# Filtre des types d'actions pour ne garder que les plus significatifs (par exemple, les types d'actions avec plus de 5% du total)
threshold = total_actions * 0.03
relevant_actions_counts = actions_counts[actions_counts > threshold]

# Création d'un pie chart pour la répartition des actions par type (uniquement pour les types d'actions les plus significatifs)
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

# Chargement les données JSON
with open('/Users/moussamar/Desktop/statsbomb_test/data/competitions.json', 'r') as file:
    competition_data = json.load(file)

# Convertissons des données en DataFrame pandas
df = pd.DataFrame(competition_data)

st.title('Répartition géographique des compétitions par pays')

# Comptage le nombre de compétitions par pays
competition_counts = df['country_name'].value_counts().reset_index()
competition_counts.columns = ['Country', 'Competition Count']

# Créatiiion d'une carte choroplèthe
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

# Affichage la carte dans Streamlit
st.plotly_chart(fig)
#####################
####################


# Ajout séparation
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

########################

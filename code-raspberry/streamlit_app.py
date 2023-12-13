import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import time
import paho.mqtt.client as mqtt
from threading import Thread
import os
import paramAndFunct as pmf
import paho.mqtt.client as paho
from streamlit.runtime.scriptrunner import add_script_run_ctx
from rerunner import notify


#streamlit run ./streamlit_app.py --server.port 8502 ou 8888

#paramètres du prog
os.chdir(r"C:\Users\alban\Documents\Drive_Alban\Cours\Alban\Mecatronique S9\Projet 4\prog")

#paramètres nécésaires au démarrage de streamlit
st.set_page_config(page_title='Dashboard', page_icon='📊',layout='wide')

#types et unitées
dict_unite = {"temperature": "°C", "humidite": "%", "anemometre": "km/h"}
dict_nom={"temperature": "Température", "humidite": "Humidité", "anemometre": "Vitesse du vent"}
dict_couleurs = {"temperature": "red", "humidite": "royalblue", "anemometre": "goldenrod"}

#variables globales
donnees_capteurs=pd.DataFrame
selected  =''

def setupPage():
    #Pour les icons, voir sur https://icons.getbootstrap.com/
    #Nom de la fenetre, icone de la fenêtre

    #titre de la page
    st.title(" :bar_chart: Dashboard")
    st.markdown("_Prototype V0.0.1_")
    menuPage()

@st.cache_data(ttl=5)
def load_data_db(path: str)->pd.DataFrame:
    while True:
        try:
            data= pd.read_sql('SELECT * FROM tab_sensor_data_test', 'sqlite:///db_sensors.db')
            break
        except Exception as e:
            print(f"Error while loading data from database: {e} \n Retrying in 1s...")
            time.sleep(1)
    return data

def thread_rerun():
    # while True:
    global selected
    tempo = 10
    for i in range(tempo):
        if selected != "Donnees direct":
            break
        print("reload dans "+str(tempo-i) + "s")
        time.sleep(1)
    
    print("rerun")
    notify()
    # au lieu de notify on peut reload la data?

#graphique
def plot_gauge(valeur, typeDonnees, valeurMax,seuilBas,seuilHaut):
    if typeDonnees=="anemometre":
        couleurSeuilHaut="red"
        couleurSeuilBas=None
        couleurDomaine =None
    else:
        couleurSeuilHaut=None
        couleurSeuilBas=None
        couleurDomaine ="lightgreen"
    fig = go.Figure(
        go.Indicator(
            value=valeur,
            mode="gauge+number",
            domain={"x": [0, 1], "y": [0, 1]},
            number={
                "suffix": dict_unite[typeDonnees],
                "font.size": 30,
            },
            gauge={
                "axis": {"range": [0, valeurMax], "tickwidth": 1},
                "bar": {"color": dict_couleurs[typeDonnees]},
                "steps": [
                    {"range": [0, seuilBas], "color": couleurSeuilBas},
                    {"range": [seuilBas, seuilHaut], "color": couleurDomaine},
                    {"range": [seuilHaut, valeurMax],"color": couleurSeuilHaut},
                ], 
            },
            title={
                "text": dict_nom[typeDonnees],
                "font": {"size": 28},
            },
        )
    )
    fig.update_layout(
        # paper_bgcolor="lightgrey",
        height=200,
        margin=dict(l=10, r=10, t=50, b=10, pad=8),
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_chart(data: pd.DataFrame):
    """
    Plot les données d'un capteur
    """
    for sensor in data["name"].unique():
        # Filter data for the current sensor
        st.header(dict_nom[sensor])
        sensor_data = data[data["name"] == sensor]
        fig = go.Figure(
            go.Scatter(
                x=sensor_data["date"],
                y=sensor_data["value"],
                mode="lines+markers",
                marker=dict(color=dict_couleurs[sensor]),
            )
        )
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title=dict_unite[sensor],
            margin=dict(l=10, r=10, t=50, b=10, pad=8),
        )
        tab1, tab2 = st.tabs(["📈 graph", "🗃 Data"])
        # tab1.subheader("Graphique")
        tab1.plotly_chart(fig, use_container_width=True)
        # tab2.subheader("Données")
        tab2.table(sensor_data)

        # st.plotly_chart(fig, use_container_width=True)

#onglets
def pageDonneesDirect():
    st.header("Données direct", divider="grey")
    with st.spinner("Chargement des données..."):
        global donnees_capteurs
        donnees_capteurs=load_data_db("db_sensors.db")
        time.sleep(1)
    thread_reload = Thread(target=thread_rerun)
    add_script_run_ctx(thread_reload)
    thread_reload.start()
    for greenhouse in donnees_capteurs["greenhouse"].unique():
        print("greenhouse est " +greenhouse)
        #print les jauges (hum et temp en 2 colonnes)
        col_header, col_status = st.columns(2)
        with col_header:
            st.header("Données de "+str(greenhouse))
        with col_status:
            st.write("Status de la serre")
            
        donnees_greenhouse = pmf.filtrageDonnes(donnees_capteurs,[greenhouse],None,None,None)
        df_donnees_greenhouse = pd.DataFrame(donnees_greenhouse)
        #affichage des jauges et du status de la serre
        liste_capteurs = df_donnees_greenhouse["name"].unique()
        nb_colonnes = liste_capteurs.size
        compteur = 0
        for columns in st.columns(nb_colonnes):
            with columns:
                lastline = pmf.getlatestvalue(df_donnees_greenhouse,[greenhouse],[liste_capteurs[compteur]])
                plot_gauge(lastline["value"].values[0],liste_capteurs[compteur],100,40,80)
                st.write("dummys values")
            compteur += 1

        with st.expander("Dernière semaine", expanded=False):
            
            donnees_greenhouse = pmf.filtrageDonnes(donnees_capteurs,[greenhouse],None,None,None)
            df_donnees_greenhouse = pd.DataFrame(donnees_greenhouse)
            #st.table(donnees_greenhouse)
            for capteurs in df_donnees_greenhouse["name"].unique():
                print("capteurs est " +capteurs)
                donnees_capteur = pmf.filtrageDonnes(donnees_greenhouse,None,[capteurs],None,None)
                #st.table(donnees_capteur)
                plot_chart(donnees_capteur)

def pageDonnesHistorique():
    st.header("Historique", divider="grey")
    st.write("Historique des données")
    with st.spinner("Chargement des données..."):
        global donnees_capteurs
        donnees_capteurs=load_data_db("db_sensors.db")
        time.sleep(1)
    zone_de_tri = st.form(key='zone_appercu_donnees', clear_on_submit=False)
    zone_d_enregistrement = st.form(key='zone_enregistrement_donnees', clear_on_submit=False)   
    with zone_de_tri:
 
        #zone de sélection de la période
        #pré tri de la période à extraire (1 semaine par défaut)
        date_debut= datetime.datetime.today() - datetime.timedelta(days=7)
        date_fin= pd.to_datetime(datetime.datetime.now())
        print("date de début: " + str(date_debut))
        print("type de date de début: " + str(type(date_debut)))
        print("date de fin: " + str(date_fin))
        print("type de date de fin: " + str(type(date_fin)))
        
        #Sélection de la période
        st.subheader("Selectionner une période", divider="grey")
        colonne_date_debut, colonne_date_fin = st.columns(2)
        with colonne_date_debut:
            date_debut_selectionnee = st.date_input('Date de début', date_debut)
            heure_debut_selectionnee = st.time_input('Heure de début', datetime.time(0, 0))
        with colonne_date_fin:
            date_fin_selectionnee = st.date_input('Date de fin', date_fin)
            heure_fin_selectionnee = st.time_input('Heure de fin', datetime.time(23, 59))
            
        #zone de sélection de la serre
        st.subheader("Choisir une serre : ", divider="grey")
        serre_selected = st.selectbox('blalba', donnees_capteurs['greenhouse'].unique())

        #zone de sélection des capteurs
        st.subheader("Choisir un ou plusieurs capteur(s)", divider="grey")
        capteur_selected = st.multiselect('blabla', donnees_capteurs['name'].unique())

        #zone d'apperçu des données suivant les paramètres selectionnés
        st.subheader("Apperçu des données", divider="grey")

        #bouton pour mettre à jour l'appercu des données
        bouton_afficher = st.form_submit_button(label="Afficher l'apperçu les données")
        
        #préparation de la zone d'affichage des données
        zone_affichage = st.empty()
        
        
        #zone d'enregistrement des données
        st.subheader("Enregistrer les données", divider="grey")
        colonne_saisie_nom,colonne_bouton_enregistrement = st.columns([3,1])
        with colonne_saisie_nom:
            nom_enregistrement = st.text_input(label='Entrer le nom du fichier:', placeholder="bliblablou", key='nom_fichier')
        with colonne_bouton_enregistrement:
            bouton_enregistrement = st.form_submit_button(label="Enregistrer les données en .csv")

    #si le bouton d'affichage est pressé
    if bouton_afficher:
        #recuperer les dates et heures selectionnées
        date_heure_debut_selectionnee = datetime.datetime.combine(date_debut_selectionnee, heure_debut_selectionnee)
        date_heure_fin_selectionnee = datetime.datetime.combine(date_fin_selectionnee, heure_fin_selectionnee)
        #filtrer les données suivant les paramètres selectionnés
        data_filtre_affichage = donnees_capteurs[(pd.to_datetime(donnees_capteurs['date']) >= date_heure_debut_selectionnee) & (pd.to_datetime(donnees_capteurs['date']) <= date_heure_fin_selectionnee)].copy()
        data_filtre_affichage = data_filtre_affichage[data_filtre_affichage['greenhouse']==serre_selected].copy()
        data_filtre_affichage = data_filtre_affichage[data_filtre_affichage['name'].isin(capteur_selected)].copy()
        print("data filtrée: " + str(data_filtre_affichage))
        with zone_affichage.container():
            linechart_historique = pd.DataFrame(data_filtre_affichage)
            fig_grange_anem = px.line(linechart_historique, x="date", y="value",color='name',template='gridon', height=400)
            st.plotly_chart(fig_grange_anem, use_container_width=True)
    if bouton_enregistrement:
        date_heure_debut_selectionnee = datetime.datetime.combine(date_debut_selectionnee, heure_debut_selectionnee)
        date_heure_fin_selectionnee = datetime.datetime.combine(date_fin_selectionnee, heure_fin_selectionnee)
        data_filtre_affichage = donnees_capteurs[(pd.to_datetime(donnees_capteurs['date']) >= date_heure_debut_selectionnee) & (pd.to_datetime(donnees_capteurs['date']) <= date_heure_fin_selectionnee)].copy()
        data_filtre_affichage = data_filtre_affichage[data_filtre_affichage['greenhouse']==serre_selected].copy()
        data_filtre_affichage = data_filtre_affichage[data_filtre_affichage['name'].isin(capteur_selected)].copy()
        nom_fichier_csv = nom_enregistrement+'.csv'
        data_frame_filtre_affichage = pd.DataFrame(data_filtre_affichage)
        #enregistrer les données filtrées dans un csv
        data_frame_filtre_affichage.to_csv(nom_fichier_csv)


def pageConsignesSerres():
    st.header("Consignes des serres", divider="grey")

def pageProfilsSerres():    
    st.header("Gestion des profils", divider="grey")

def menuPage(): #ok
    global selected
    selected = option_menu(
    menu_title= None,
    options=["Donnees direct", "Historique", "Consignes des serres", "Profils des serres"],
    icons=["broadcast-pin","bar-chart-fill","gear","basket2-fill","controller"],
    orientation="horizontal")
    if selected == "Donnees direct":
        pageDonneesDirect()
    if selected == "Historique":
        pageDonnesHistorique()
    if selected == "Consignes des serres":
        pageConsignesSerres()
    if selected == "Profils des serres":
        pageProfilsSerres()

def test():
    setupPage()
    plot_gauge(60, "temperature", 100,40,80)
    plot_gauge(76, "humidite", 100,20,80)
    plot_gauge(82, "anemometre", 100,20,80)
    data= load_data_db("db_sensors.db")
    plot_chart(pmf.filtrageDonnes(data, ["serre_1"],["temperature","humidite"],datetime.datetime.today()-datetime.timedelta(days=19),datetime.datetime.today()))
    #on message on fait un rerun mais on ajoute la data à la df ou alors on atends une sec et on rerun avec ducoup la nouvelle db?
    #idee faire un thread qui check si db change, si oui on rerun

def launchApp():
    setupPage()

# test()
launchApp()

 
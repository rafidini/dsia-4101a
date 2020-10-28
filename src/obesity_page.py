"""
Module pour la page obesity.
"""

# Imports
import numpy as np
import pandas as pd
import json
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go

# Imports de fichiers en local
from src.paths import obesityPath, countriesPath
from src.process_data import process_obesity

# Chargement des donnees
obesity = pd.read_csv(obesityPath, index_col=0)

with open(countriesPath) as f:
    countriesGeoJson = json.load(f)

# Traitement des donnees
obesity = process_obesity(obesity)

# Fonctions pour la page
def graph_map_obesity(year):
    """
    Retourne une carte representant le pourentage d'obesite pour
    chaque pays dans le monde pour une annee donnee.
    """

    # Filtre les donnees par rapport a l'annee
    df = obesity.query("year == {} and sex == 'B'".format(year))

    # Creation de la map
    mapObesity = px.choropleth_mapbox(
        data_frame = df,
        geojson = countriesGeoJson,
        locations = "country_code",
        color = "obesity",
        color_continuous_scale="Brwnyl",
        range_color=(obesity.obesity.min(), obesity.obesity.max()),
        mapbox_style = 'carto-darkmatter',
        center = {"lat": 33.0902, "lon": -35.7129},
        zoom = 1,
        hover_name = df.country,
        hover_data = ["obesity", "continent"]
    )

    mapObesity.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        legend_title_text='Obesity (%)',
        font=dict(
            color="white",
            size=12
        )
    )
    mapObesity.layout.coloraxis.colorbar.title = "Obesity (%)"
    mapObesity.layout.coloraxis.colorbar.x = 0.9

    return mapObesity

def graph_bar_obesity(year):
    """
    Retourne un histogramme representant la distribution des
    pourcentage d'obesite selon les pays pour une annee donnee.
    """

    # Filtre les donnees par rapport a l'annee
    df = obesity.query("year == {} and sex == 'B'".format(year))
    
    # Le pas
    step = 2.5
    
    # Creation des donnees
    hist, bins = np.histogram(
        df.obesity,
        bins = np.arange(
            obesity.obesity.min(),
            obesity.obesity.max()+step,
            step
        )
    )

    # Creation de l'histogramme
    histogramObesity = go.Figure(
        data = [
            go.Bar(
                x = [str(str(int(eBin)) + "-" + str(int(eBin+step)) + "%") for eBin in bins],
                y = hist,
                text = hist,
                marker={'color': bins,'colorscale': 'Brwnyl'}
            )
        ]
    )

    histogramObesity.update_layout(
        height=330,
        bargap=0,
        margin=dict(l=8, r=8, t=8, b=0),
        paper_bgcolor='rgba(38,38,38,1)',
        plot_bgcolor='rgba(38,38,38,1)',
        yaxis_visible=False,
        yaxis_showticklabels=False,
    )

    histogramObesity.layout.xaxis.color = 'white'
    
    histogramObesity.update_traces(
        texttemplate='%{text:.2s}',
        textposition='outside',
        textfont=dict(
            size=12,
            color="white"
        )
    )

    return histogramObesity

def graph_line_obesity_group(pMinYear, pMaxYear, pGroupType, pLocation):
    """
    Retourne un graphique avec deux courbes representant l'evolution
    de l'obesite au sein d'un pays/continent pour chaque sexe dans un
    interval donne.
    """

    # Filtre selon le groupe
    group_filter = '{} == "{}"'.format("country" if pGroupType == "Countries" else "continent", pLocation) 

    # Filtre pour l'interval
    interval_filter = "year >= {} and year <= {}".format(pMinYear, pMaxYear)

    # Filtre pour le sex
    sex_filter = "sex != 'B'"

    # Filtre les donnees
    df = obesity.query(interval_filter + " and " + group_filter + " and " + sex_filter)

    # Regroup si continent
    if pGroupType != "Countries":
        df = df.groupby(["year", "sex"]).mean().reset_index(level=['year', 'sex']).dropna()
    

    # Creation du graphique
    try:
        lineplot = px.line(
            df.replace({"sex":{"M":"Male", "F":"Female"}}),
            x="year",
            y="obesity",
            color="sex"
        )

        # Modification d'elements du graphique
        lineplot.update_layout(
            title="Evolution of obesity percentage by sex",
            legend_title="",
            margin=dict(l=4, r=4, t=40, b=4),
            paper_bgcolor='rgba(48,48,48,1)',
            plot_bgcolor='rgba(48,48,48,1)',
            font=dict(
                size=12,
                color="white"
            ),
            xaxis=dict(title="Year"),
            yaxis=dict(title="Obesity (%)")
        )


        return lineplot
    except:
        return None

def graph_pie_obesity_group(year, pGroupType, pLocation):
    """
    Retourne un graphique camenbert representant:
    - Un pays par rapport a son continent
    - Un continent par rapport au monde
    Pour une annee, type de region et la region donnee.
    """

    pie_chart = None

    # Filtre annee
    year_filter = "year == {}".format(year)

    # Filtre group
    group_filter = '{} == "{}"'.format("country" if pGroupType == "Countries" else "continent", pLocation)

    # Filtre sex
    sex_filter = "sex == 'B'"

    # Filtre les donnees
    and_space = " and "
    df = obesity.query(year_filter + and_space + group_filter + and_space + sex_filter)

    # Cas d'un pays
    if pGroupType == "Countries":
        # Donnees pour le camenbert
        try:
            obese = float(df.obesity)
        except:
            obese = 0
        
    # Cas d'un continent
    else:
        # Donnees pour le camenbert
        try:
            obese = float(df.obesity.mean())
        except:
            obese = 0
    
    labels = ["Obese", "Not obese"]
    values = [obese, 100 - obese]

    # Creation du camenbert
    pie_chart = go.Figure(data=[
        go.Pie(
            labels=labels,
            values=values,
            pull=[0.25, 0],
        ),
    ])

    # Modification d'elements du graphique
    pie_chart.update_layout(
        title="Percentage of obesity in population",
        legend_title="",
        margin=dict(l=4, r=4, t=40, b=4),
        paper_bgcolor='rgba(48,48,48,1)',
        plot_bgcolor='rgba(48,48,48,1)',
        font=dict(
            size=12,
            color="white"
        ),
    )

    pie_chart.update_traces(
        textposition='outside',
    )

    return pie_chart

def rank_obesity_group(year, pGroupType, pLocation):
    """
    Retourne un tuple (rank, n) tel que:
    - rank : le rang du pays/continent par rapport a ses confreres
    - n    : le nombre de confreres 
    La position retournee est recuperee par un tri croissant des donnees
    donc plus le rang obtenue s'approche du nombre de confreres plus le
    pourcentage d'obesite est eleve.
    """

    rank, n = None, None

    # Pre-selection
    obesitySelect = obesity.query('year == {} and sex == "B"'.format(year))

    # Tri des donnees
    obesitySelectSorted = obesitySelect.sort_values(by="obesity").copy()

    # Regroupement pour les continents
    if pGroupType == "Continents":
        obesitySelectSorted = obesitySelectSorted.groupby("continent").mean()

    # Reset l'index
    new_index = np.arange(1, obesitySelectSorted.shape[0] + 1)
    if pGroupType == "Countries":
        obesitySelectSorted = obesitySelectSorted.set_index(new_index)
    else:
        obesitySelectSorted = obesitySelectSorted[['obesity']].reset_index(level='continent').set_index(new_index)

    try:
        # Recupere le rang
        rank = obesitySelectSorted.index[obesitySelectSorted['country' if pGroupType == "Countries" else 'continent'] == pLocation].tolist()
        n = new_index.max()

        return rank[0], n

    except:
        return None, None

def generate_dropdown(dataframe, feature):
    dropdown = list()

    for element in dataframe[feature].unique():
        dropdown.append({'label': element, 'value':element})

    return dropdown


# Variables pour les elements de la page
minYear = obesity.year.min()
maxYear = obesity.year.max()
dropdown_continents = generate_dropdown(obesity, 'continent')
dropdown_countries = generate_dropdown(obesity, 'country')

# Selection du type de groupe
radioitems = dbc.FormGroup(
    [
        html.Li([dbc.Label("Select a group type")]),
        dbc.RadioItems(
            options=[
                {"label": "Country", "value": "Countries"},
                {"label": "Continent", "value": "Continents"},
            ],
            value="Countries",
            id="radioitems-obesity-group",
        ),
    ]
)

# Page pour obesite
pageObesity = html.Div([

    # Cote gauche
    html.Div(
        [
            # Titre
            html.H4("Menu"),

            # Break
            html.Br(),
            html.Hr(style={"background-color":"white"}),

            # Titre 2
            html.H5(id="label-year-obesity"),

            # Div du slider pour l'annee
            html.Div([

                html.Li([dbc.Label(["Select a year using the slider"])]),

                # Dropdown pour l'annee
                dcc.Slider(
                    id="dropdown-obesity-year",
                    value=minYear,
                    min=minYear,
                    max=maxYear,
                    step=1
                ),
            ]),

            # Separation
            html.Hr(style={"background-color":"white"}),

            # Titre 3
            html.H5("Group"),

            # Selection du type de groupe (pays/continent)
            radioitems,

            # Selection de la region specifique
            html.Li([dbc.Label(["Select a specific location"])]),
            dcc.Dropdown(
                id='dropdown-obesity-group-location',
                clearable=True,
                style={"color":"black"}
            ),
            html.Br(),
            html.Hr(style={"background-color":"white"}),

            # Confirmation de requête
            html.H5("Confirm"),
            html.Li([dbc.Label(["Press the button to confirm"])]),
            dbc.Button("Submit", id="button-obesity-group", color="light", outline=True, className="mr-1"),

            # Fenetre pour region specifiee
            dbc.Modal(
                [
                    # Fenetre: Titre
                    dbc.ModalHeader(id="header-obesity-group"),

                    # Fenetre: Corps
                    dbc.ModalBody([

                        # Gauche: Graphique obesite homme/femme
                        html.Div([
                            dbc.Card([
                                dbc.CardBody([
                                    dcc.Graph(id="lineplot-obesity-graph", style={"height":520})
                                ]),

                                dbc.CardFooter([
                                    # Label des annees du slider
                                    dbc.Label(
                                        "From {} to {}:".format(minYear, maxYear),
                                        id="label-obesity-group-graph",
                                    ),

                                    # Selection de l'interval
                                    dcc.RangeSlider(
                                        id="slider-obesity-group-graph",
                                        min=minYear,
                                        max=maxYear,
                                        value=[minYear, maxYear]
                                    )
                                ])
                            ], outline=True, color="dark")
                        ], style={"flex":3, "padding-right":5}),

                        # Droite: Graphiques divers
                        html.Div([
                            dbc.Card([

                                # Zone des graphiques
                                dbc.CardBody([
                                    dcc.Graph(id="piechart-obesity-miscellaneous", style={"height":260, "padding":0}),

                                    html.Div(
                                        html.H1([
                                            dbc.Badge(id="ranking-obesity-miscellaneous", className="ml-1", color="secondary"),
                                            html.P(id="ranking-text-obesity-miscellaneous")],
                                        style={"text-align":"center", "padding-top":260* 2/6})
                                    , style={"height":260})
                                ]),

                                # Pied de page des graphiques
                                dbc.CardFooter([
                                    # Label de l'annee selectionnee
                                    dbc.Label(
                                        "During the year {}".format(minYear),
                                        id="label-obesity-miscellaneous"
                                    ),

                                    # Selection de l'annee
                                    dcc.Slider(
                                        id="slider-obesity-miscellaneous-graph",
                                        min=minYear,
                                        max=maxYear,
                                        value=minYear
                                    )
                                ]),
                            ], color="dark", outline=True),

                        ], style={"flex":2, "padding-left":5})

                    ], style = {"display":"flex"}),

                    # Fenetre: Pied de page
                    dbc.ModalFooter(
                        dbc.Button("Close", id="close-modal-obesity-group", color="danger", outline=True,block=True, className="ml-auto")
                    ),
                ],
                id="modal-obesity-group",
                size="xl"
            ),
        ],
        style = {"flex":1, "padding":"20px"},
    ),

    # Cote droit
    html.Div(
        [
            # Graphique: Carte choropleth obesite
            html.Div([dcc.Graph(id='graph-map-obesity')], style = {}),

            # Graphique: Distribution obesite
            html.Div([dcc.Graph(id='graph-bar-obesity')], style = {}),
        ],
        style = {"flex":2, "display": "flex", "flex-direction": "column"},
    ),],
    style = {"display":"flex", " padding":"0px", "margin":"0px"}
)

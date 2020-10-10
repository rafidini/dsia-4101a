# Import
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import scipy.stats as sc
import plotly.express as px
import plotly.graph_objects as go

# Import local
from src.obesity_page import generate_dropdown
from src.process_data import process_obesity, process_employment
from src.paths import employmentPath, obesityPath

# Chargement des donnees
analytics = pd.merge(
    process_obesity(pd.read_csv(obesityPath, index_col=0)),
    process_employment(pd.read_csv(employmentPath)),
    on=['country', 'year', 'sex', 'continent', 'country_code']
) 

# Fonctions pour la page
def correlation_obesity_employment_analytics(country, activity):
    """
    Retourne la correlation entre l'obesite et les activites soit manuelles
    soit bureautiques pour une annee donnee.
    """

    # Filtrage + nettoyage
    df = analytics.query("activity != 'U' and sex == 'B'").copy()
    df = df.drop(["country_code", "min_obesity", "max_obesity", "sex", "continent"], axis=1)

    # Recuperation des chiffres de l'emploi par activite
    df['value_mean'] = df.groupby(["country", "year", "activity"]).value.transform('mean')

    # Nettoyage
    df = df.drop(["subject", "value"], axis=1).drop_duplicates()

    # Filtrage
    activities = df.query('country == "{}" and activity == "{}"'.format(country, activity))

    # Correlation
    correlation = sc.pearsonr(activities['obesity'], activities['value_mean'])

    return correlation[0]

def graph_obesity_employment_analytics(country, activity):
    """
    Retourne un graphique avec:
    - en abscisse: l'obesite
    - en ordonee : le nombre d'employes
    pour un pays et une activite donnee.
    """

    # Filtrage + nettoyage
    df = analytics.query('activity == "{}" and sex == "B" and country == "{}"'.format(activity, country)).copy()
    df = df.drop(["country_code", "min_obesity", "max_obesity", "sex", "continent", "country"], axis=1)

    # Recuperation des chiffres de l'emploi par activite
    df['value_mean'] = df.groupby(["year", "activity"]).value.transform('mean')

    # Nettoyage
    df = df.drop(["subject", "value"], axis=1).drop_duplicates()

    # Creation du graphique
    lineplot = px.scatter(
        df,
        x='obesity',
        y='value_mean',
        trendline="ols"#"lowess"
    )
    
    return lineplot

# Variables pour la page
dropdown_countries = generate_dropdown(analytics, "country")

# Page pour l'analyse des possibles correlations entre jeu de donnees
pageAnalytics = html.Div([
    # Menu
    html.Div([
        # Titre
        html.H4("Menu"),

        # Liste des options
        html.Ul([

            # Titre type de visualisation
            html.Li([
                html.H6("Correlation visualization type:")
            ]),

            # Radio pour la selection de type de visu
            dbc.RadioItems(
                options=[
                    {'label':"Lineplot", 'value':"lineplot"},
                    {'label':"Heatmap", 'value':"heatmap"}
                ],

                value="lineplot"
            ),

            # Saut de ligne
            html.Br(),

            # Titre pays a selectionner
            html.Li([
                html.H6("Country:")
            ]),

            # Dropdown pour la selection de pays
            dcc.Dropdown(
                id="dropdown-country-analytics",
                clearable=True,
                options=dropdown_countries,
                value="France",
                style={"color":"black"}
            )
       ])
    ], style = {"flex":1, "padding":"20px"}),

    # Affichage des graphiques
    html.Div([
        html.Div([dcc.Graph(id="graph-lineplot-correlationD-analytics")], style={}),
        html.Div([dcc.Graph(id="graph-lineplot-correlationM-analytics")], style={}),
    ], style = {"flex":2, "padding":"20px", "background-color":"coral", "display": "flex", "flex-direction": "column"})
], style = {"display":"flex", " padding":"0px", "margin":"0px"})


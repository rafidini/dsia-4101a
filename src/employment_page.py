"""
Module pour la page employment.
"""

# Imports
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Imports de fichiers en local
from src.paths import employmentPath
from src.process_data import process_employment
from src.obesity_page import generate_dropdown



# Chargement des donnees
employment = pd.read_csv(employmentPath)

# Traitement des donnees
employment = process_employment(employment)

# Fonctions pour la page
def check_values_available(pCountry):
    """
    Verifie s'il existe des valeurs ppur les sexes M et F pour un pays.
    """
    # Creer un vecteur qui compte le nombre de valeurs different de zero
    vector = employment.query('country == "{}"'.format(pCountry)).sex.value_counts().values

    # Retourne vrai s'il n'y a pas que des zeros
    return np.sum(np.nonzero(vector)) != 0

def generate_input(title, input_widget):
    """
    Generate an input block with
    - a title
    - an input widget (Select from dash_bootstrap for example)
    """

    return html.Div([
        # Titre de l'input
        html.Li([
            html.H6(title)
        ]),

        # Input
        input_widget
    ])

def generate_sep():
    """
    Generate a separator composed of:
    - line break
    """
    return html.Div([
        html.Br(),
    ])

def graph_line_subjects_country_range(pMinYear, pMaxYear, pCountry, pActivity, pSex):
    """
    Retourne un graphique lineplot des activites d'un pays dans un interval donne pour un sexe.
    """

    data = employment.query('year >= {} and year <= {} and country == "{}" and activity == "{}" and sex == "{}"'.format(pMinYear, pMaxYear, pCountry, pActivity, pSex))

    lineplot = px.area(
        data, 
        x="year", 
        y="value", 
        color="subject", 
        line_group="subject",
        hover_name="subject",
        color_discrete_sequence=px.colors.sequential.haline,
        height=560
    ) if data.shape[0] > 0 else go.Figure()

    lineplot.update_layout(
        title="Employment by sector between {} and {} in {}".format(pMinYear, pMaxYear, pCountry),
        showlegend=False,
        margin=dict(l=4, r=4, t=40, b=4),
        paper_bgcolor='rgba(48,48,48,1)',
        plot_bgcolor='rgba(48,48,48,1)',
        font=dict(
            size=12,
            color="white"
        ),
        xaxis=dict(title="Year"),
        yaxis=dict(title="Number of employees")
    )

    return lineplot

def graph_pie_subjects_country_year(pYear, pCountry, pActivity, pSex):
    """
    Retourne un graphique piechart des activites d'un pays pour une annee et un sexe donnes.
    """

    data = employment.query('year == {} and country == "{}" and activity == "{}" and sex == "{}"'.format(pYear, pCountry, pActivity, pSex))

    pie = px.pie(
        data,
        values='value',
        hover_name="subject",
        names='subject',
        color_discrete_sequence=px.colors.sequential.haline
    ) if data.shape[0] > 0 else go.Figure()

    pie.update_layout(
        #showlegend=False,
        margin=dict(l=4, r=4, t=4, b=4),
        paper_bgcolor='rgba(48,48,48,1)',
        plot_bgcolor='rgba(48,48,48,1)',
        font=dict(
            size=12,
            color="white"
        ),
        legend = dict(
            bgcolor = 'rgba(0, 0, 0, 0)',
            yanchor="top",
            y=0.0,
            xanchor="left",
            x=0.0
        )
    )

    return pie

def graph_line_desktop_manual_country_range(pMinYear, pMaxYear, pCountry):
    """
    Retourne un graphique lineplot des activites bureautiques et manuelles d'un pays dans un interval donne.
    """

    # Recupere le total d'employes dans chaque activite
    data = employment.query('year >= {} and year <= {} and country == "{}" and activity != "U" and sex == "{}"'.format(pMinYear, pMaxYear, pCountry, "B")).groupby(["country", "year", "activity"]).sum().reset_index(level=[0, 1]).copy()
    
    # Traitement sur l'index
    data['activity'] = data.index
    data.index = np.arange(0, data.shape[0])
    data = data.replace({"activity":{"D":"Desktop", "M":"Manual"}})
    lineplot = None

    try:
        lineplot = px.line(
            data, 
            x="year", 
            y="value", 
            color="activity", 
            hover_name="value", 
            color_discrete_sequence=px.colors.sequential.haline,
            height=620)

        lineplot.update_traces(
            line=dict(width=4),
        )

    except:
        lineplot = go.Figure()

    lineplot.update_layout(
        title="Type of activity between {} and {} in {}".format(pMinYear, pMaxYear, pCountry),
        legend_title="Type of activity",
        margin=dict(l=4, r=4, t=40, b=4),
        paper_bgcolor='rgba(48,48,48,1)',
        plot_bgcolor='rgba(48,48,48,1)',
        font=dict(
            size=12,
            color="white"
        ),
        xaxis=dict(title="Year"),
        yaxis=dict(title="Number of employees")
    )

    return lineplot

# Variables pour la page
minYear = employment.year.min()
maxYear = employment.year.max()

# Input pour le pays
input_country = dbc.Select(
    id="input-country-employment",
    options=generate_dropdown(employment, 'country'),
    value="France"
)

# Input pour l'interval des annees
input_range_year = dcc.RangeSlider(
    id="input-range-year-employment",
    min=minYear,
    max=maxYear,
    step=1,
    value=[minYear, maxYear],
)

# Input pour le sex
input_sex = dbc.RadioItems(
    id="input-sex-employment",
    options=[
        {"label":"Both", "value":"B"},
        {"label":"Male", "value":"M"},
        {"label":"Female", "value":"F"},
        ],
    value="B",
    inline=True
)

# Input pour le type d'activite
input_activity = dbc.RadioItems(
    id="input-activity-employment",
    options=[
        {"label":"Desktop", "value":"D"},
        {"label":"Manual", "value":"M"},
        ],
    value="D",
    inline=True
)

# Input pour l'annee
input_year = dcc.Slider(
    id="input-year-employment",
    min=minYear,
    max=maxYear,
    step=1,
    value=minYear
)

# Menu
menu = dbc.Col(
    html.Div([
        # Carte définissant des limites visibles
        dbc.Card(
            [
                # Titre
                html.H4("Menu"),

                # Liste des options
                html.Ul([
                    # ligne separateur
                    html.Br(),

                    # Input pays
                    generate_input("Country", input_country),
                    generate_sep(),

                    # Input interval annees
                    generate_input("Year range", input_range_year),
                    generate_sep(),

                    # Input sex
                    generate_input("Sex", input_sex),
                    generate_sep(),

                    # Input activity
                    generate_input("Activity type", input_activity),
                    generate_sep()
                ])
            ],
            body=True,
            style={'height':600}
        )
    ]),
    width=4
)

# Lineplot subjects
lineplot_subjects = dbc.Col(
    html.Div([
        dbc.Card(
            children=[dcc.Graph(id="lineplot-subjects-employment")],
            body=True,
        )
    ]),
    width=8
)

# Piechart
piecharts_subjects = dbc.Col(
    html.Div([
        dbc.Card(
            [
                dbc.CardBody(dcc.Graph(id="piecharts-subjects-employment")),
                dbc.CardFooter([dbc.Label(id="label-year-piechart-employment"), input_year])
            ],
            className="mb-3",
            style={'height':660}
        )
    ]),
    width=5
)

# Desktop/Manual lineplot
desktop_manual_graph = dbc.Col(
    html.Div([
        dbc.Card(
            dcc.Graph(id="lineplot-activity-employment"),
            body=True,
        )
    ]),
    width=7
)

# Page pour l'emploi
pageEmployment = html.Div([
    # Premiere ligne (menu, barchart subjects)
    dbc.Row([
        menu,
        lineplot_subjects
    ], style={"padding":"20px"}),

    # Deuxieme ligne (piecharts subjects, lineplot D/M)
    dbc.Row([
        piecharts_subjects,
        desktop_manual_graph
    ], style={"padding":"20px"})

])


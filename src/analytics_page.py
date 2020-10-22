"""
Module pour la page analytics.
"""

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
correlations = {
    "Pearson":sc.pearsonr,
    "Spearman":sc.spearmanr,
    "Kendall":sc.kendalltau
}

def correlation_obesity_employment_analytics(country, activity, corr_type="Pearson"):
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
    correlation = correlations[corr_type](activities['obesity'], activities['value_mean'])

    return correlation[0]

def graph_obesity_employment_analytics(country, activity, corr_type="Pearson"):
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

    # Modifications du graphique
    lineplot.update_layout(
        margin=dict(l=4, r=4, t=4, b=4),
        paper_bgcolor='rgba(34,34,34,1)',
        plot_bgcolor='rgba(34,34,34,1)',
        font=dict(
            size=12,
            color="white"
        ),
    )

    blue = "#3e5a7c"
    red = "#d75745"
    color = blue if correlation_obesity_employment_analytics(country, activity, corr_type) >= 0.0 else red

    lineplot.update_traces(
        marker=dict(
            color=color,
            size=15,
            line=dict(
                color='white',
                width=2
            )
        )
    )
    
    return lineplot

def correlation_alert_component_analytics(country, activity, corr, corr_type="Pearson"):
    """
    Retourne composant de l'interface utilisateur indiquant la correlation
    entre les emplois bureautiques et manuels par rapport a l'obesite pour
    un pays, un type d'emploi et une correlation donnes.
    """

    # Couleur de l'indicateur
    color = "primary" if corr >= 0.0 else "danger"

    # Texte de l'indicateur
    title = html.H4(html.B("{}".format(round(corr, 3))))
    body = html.H5(("Desktop" if activity == "D" else "Manual") + " jobs/Obesity correlation", className="alert-heading")
    divider = html.Hr()
    footer = html.P(html.Em("This value was computed by using the {} correlation.".format(corr_type.lower())), className="mb-0")

    # L'indicateur
    alert = dbc.Alert([title, body, divider, footer], color=color)

    return alert

def create_table_correlation_country_activity(corr_type="Pearson"):
    """
    Retourne une table avec pour:
    - index: Le nom du pays
    - colonnes:
      - D: La correlation entre les emplois bureautiques et l'obesite
      - M: La correlation entre les emplois manuels et l'obesite
    """

    analytics_copy = analytics.query("activity != 'U' and sex == 'B'").copy()
    analytics_copy = analytics_copy.drop(columns=["sex", "country_code", "continent", "min_obesity", "max_obesity"])
    analytics_copy['value_mean'] = analytics_copy.groupby(["country", "year", "activity"]).value.transform('mean')
    analytics_copy = analytics_copy.drop(["subject", "value"], axis=1).drop_duplicates()

    df_corr = analytics_copy.groupby(["country", "activity"])[["obesity","value_mean"]].corr(method=corr_type.lower())
    df_corr = df_corr.reset_index(level=[0,1])

    df_corr = df_corr.loc['obesity',:]

    df_corr = pd.pivot_table(df_corr, values='value_mean', index='country', columns='activity')

    return df_corr

def heatmap_obesity_employment_analytics(corr_type="Pearson"):
    """
    Retourne une carte de chaleur selon les correlation entre
    obesite et les emplois bureautiques et manuels.
    """
    data = create_table_correlation_country_activity(corr_type).transpose()

    heatmap = px.imshow(
        data,
        color_continuous_scale="RdBu",
        height=700
    )

    heatmap.update_layout(
        title="Heatmap of correlation between obesity and desk/manual jobs",
        yaxis=dict(title="Type of activity"),
        xaxis=dict(title="Country"),
        margin=dict(l=4, r=4, t=40, b=4),
        paper_bgcolor='rgba(34,34,34,1)',
        plot_bgcolor='rgba(34,34,34,1)',
        font=dict(
            size=16,
            color="white"
        ),
    )

    heatmap.update_xaxes(tickangle=45)
    heatmap.update_yaxes(ticktext=["Desk " , "Manual "], tickvals=["D", "M"])

    return heatmap

# Variables pour la page
dropdown_countries = generate_dropdown(analytics.query("country != 'Brazil'"), "country")
lineplot_graph = dbc.Row([
    dbc.Col(
        # Corelation bureautique-obesite
        html.Div([
            html.Div(id="alert-correlationD-analytics"),
                dcc.Graph(id="graph-lineplot-correlationD-analytics")
        ]),
        width=6
    ),

    dbc.Col(
        # Correlation manuel-obesite
        html.Div([
            html.Div(id="alert-correlationM-analytics"),
            dcc.Graph(id="graph-lineplot-correlationM-analytics")
        ]),
        width=6
    )
])
country_selection = [
    # Titre pays a selectionner
    html.Li([html.H6("Country:")]),

    # Dropdown pour la selection de pays
    dcc.Dropdown(
        id="dropdown-country-analytics",
        clearable=False,
        options=dropdown_countries,
        value="France",
        style={"color":"black"}
        )
]
radio_graph_type = dbc.RadioItems(
    id="radio-graph-type-analytics",
    options=[
        {'label':"Lineplot", 'value':"lineplot"},
        {'label':"Heatmap", 'value':"heatmap"}
    ],
    value="heatmap"
)
radio_corr_type = dbc.RadioItems(
    id="radio-corr-type-analytics",
    options=[
        {'label':"Pearson", 'value':"Pearson"},
        {'label':"Spearman", 'value':"Spearman"},
        {'label':"Kendall", 'value':"Kendall"}
    ],

    value = "Pearson"
)

# Page pour l'analyse des possibles correlations entre jeu de donnees
pageAnalytics = html.Div([
    # Menu
    html.Div([
        # Titre
        html.H4("Menu"),

        # Liste des options
        html.Ul([
            html.Hr(style={"background-color":"white"}),
            
            # Type de visualisation
            html.Div([
                # Titre type de visualisation
                html.Li([
                    html.H6("Correlation visualization type:")
                ]),

                # Radio pour la selection de type de visu
                radio_graph_type,
            ]),

            # Saud de ligne
            html.Br(),
            html.Hr(style={"background-color":"white"}),

            html.Div([
                # Titre
                html.Li([html.H6("Correlation type:")]),

                # Radio pour la selection du type de correlation
                radio_corr_type
            ]),

            # Saut de ligne
            html.Br(),
            html.Hr(style={"background-color":"white"}),

            # Pays a selectionne
            html.Div(id="ui-dropdown-country-analytics")
       ])
    ], style = {"flex":1, "padding":"20px"}),

    # Affichage des graphiques
    html.Div(id="graphs-analytics", style = {"flex":3, "padding":"20px"})
], style = {"display":"flex", " padding":"0px", "margin":"0px"})


# Imports
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

# Imports de fichiers en local
from src.paths import employmentPath
from src.process_data import process_employment


# Chargement des donnees
employment = pd.read_csv(employmentPath)

# Traitement des donnees
employment = process_employment(employment)

# Page pour l'emploi
pageEmployment = html.Div([
    html.H1("Employment")
])


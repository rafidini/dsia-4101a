# Imports
import pandas as pd
import plotly.express as px 
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Imports de fichiers en local
from src.navigation_bar import navigationBar
from src.obesity_page import pageObesity, graph_map_obesity, graph_bar_obesity, dropdown_countries, dropdown_continents, graph_line_obesity_group, graph_pie_obesity_group
from src.employment_page import pageEmployment
from src.analytics_page import pageAnalytics

# Application: Dashboard
if __name__ == '__main__':

    # Creer une application Dash
    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.DARKLY],
        suppress_callback_exceptions=True
    )

    # Corps de l'application
    app.layout = html.Div([
        navigationBar,
        dcc.Location(id='url', refresh=False),
        html.Div(id='page')
    ])

    # Interactivite: Navigation de page
    @app.callback(
        dash.dependencies.Output('page', 'children'),
        [dash.dependencies.Input('url', 'pathname')]
    )
    def display_page(pathname):
        if pathname == '/obesity':
            return pageObesity
        elif pathname == '/employment':
            return pageEmployment 
        elif pathname == '/analytics':
            return pageAnalytics    
        else:
            return pageObesity
    
    # Interactivite: Changement d'annee sur la page 'obesity'
    @app.callback(
        [dash.dependencies.Output('graph-bar-obesity', 'figure'),
        dash.dependencies.Output('graph-map-obesity', 'figure')],
        [dash.dependencies.Input('dropdown-obesity-year', 'value')]
    )
    def change_year(year):
        return [graph_bar_obesity(year), graph_map_obesity(year)]

    # Interactivite: Choix de groupe/region
    @app.callback(
        [dash.dependencies.Output('dropdown-obesity-group-location', 'options')],
        [dash.dependencies.Input('radioitems-obesity-group', 'value')]
    )
    def group_input(group_type):
        return [dropdown_countries] if group_type == "Countries" else [dropdown_continents]

    # Interactivite: Ouverture fenetre pour region specifique
    @app.callback(
        [dash.dependencies.Output("modal-obesity-group", "is_open"),
        dash.dependencies.Output("header-obesity-group", "children")],
        [dash.dependencies.Input("button-obesity-group", "n_clicks"),
        dash.dependencies.Input("close-modal-obesity-group", "n_clicks"),
        dash.dependencies.Input("dropdown-obesity-group-location", "value")],
        [dash.dependencies.State("modal-obesity-group", "is_open")]
    )
    def open_modal(n1, n2, location, is_open):
        if n1 or n2:
            return not is_open, location
        return is_open, None

    # Interactivite: Indicateur des annees pour le range slider
    @app.callback(
        dash.dependencies.Output("label-obesity-group-graph", "children"),
        dash.dependencies.Input("slider-obesity-group-graph", "value")
    )
    def change_range_slider(values):
        return "From {} to {}:".format(values[0], values[1])

    # Interactivite: Creation du graphique pour une region specifique
    @app.callback(
        dash.dependencies.Output("lineplot-obesity-graph", "figure"),
        [dash.dependencies.Input('slider-obesity-group-graph', "value"),
        dash.dependencies.Input('radioitems-obesity-group', 'value'),
        dash.dependencies.Input('dropdown-obesity-group-location', 'value')]
    )
    def create_graph_group(interval, group_type, location):
        return graph_line_obesity_group(interval[0], interval[1], group_type, location)

    # Interactivite: Indicateur des annees pour le slider
    @app.callback(
        [dash.dependencies.Output("label-obesity-miscellaneous", "children"),
        dash.dependencies.Output("piechart-obesity-miscellaneous", "figure")],
        [dash.dependencies.Input("slider-obesity-miscellaneous-graph", "value"),
        dash.dependencies.Input('radioitems-obesity-group', 'value'),
        dash.dependencies.Input('dropdown-obesity-group-location', 'value')]
    )
    def change_slider(value, group_type, location):
        return "During the year {}".format(value), graph_pie_obesity_group(value, group_type, location)

    # Titre de l'application
    app.title = "Dashboard"

    # Execute l'application Dash sur un serveur web local
    app.run_server(debug=True)

    pass


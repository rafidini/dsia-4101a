# Imports
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output

# Imports de fichiers en local
from src.analytics_page import (correlation_alert_component_analytics,
                                correlation_obesity_employment_analytics,
                                country_selection,
                                graph_obesity_employment_analytics,
                                heatmap_obesity_employment_analytics,
                                lineplot_graph, pageAnalytics)
from src.employment_page import pageEmployment

from src.navigation_bar import navigationBar
from src.obesity_page import (dropdown_continents, dropdown_countries,
                              graph_bar_obesity, graph_line_obesity_group,
                              graph_map_obesity, graph_pie_obesity_group,
                              pageObesity, rank_obesity_group)

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
    
    # OBESITY - Interactivite: Changement d'annee sur la page 'obesity'
    @app.callback(
        [dash.dependencies.Output('graph-bar-obesity', 'figure'),
        dash.dependencies.Output('graph-map-obesity', 'figure')],
        [dash.dependencies.Input('dropdown-obesity-year', 'value')]
    )
    def change_year(year):
        return [graph_bar_obesity(year), graph_map_obesity(year)]

    # OBESITY - Interactivite: Choix de groupe/region
    @app.callback(
        [dash.dependencies.Output('dropdown-obesity-group-location', 'options'),
        dash.dependencies.Output('dropdown-obesity-group-location', 'value')],
        [dash.dependencies.Input('radioitems-obesity-group', 'value')]
    )
    def group_input(group_type):
        return [dropdown_countries, "France"] if group_type == "Countries" else [dropdown_continents, "Europe"]

    # OBESITY - Interactivite: Ouverture fenetre pour region specifique
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


    # OBESITY - Interactivite: Ouverture fenetre pour region specifique bis
    @app.callback(
        dash.dependencies.Output("button-obesity-group", "n_clicks"),
        dash.dependencies.Input("close-modal-obesity-group", "n_clicks"),
    )
    def reset_button_submit(n_clicks_close):
        return None

    # OBESITY - Interactivite: Indicateur des annees pour le range slider
    @app.callback(
        dash.dependencies.Output("label-obesity-group-graph", "children"),
        dash.dependencies.Input("slider-obesity-group-graph", "value")
    )
    def change_range_slider(values):
        return "From {} to {}:".format(values[0], values[1])

    # OBESITY - Interactivite: Creation du graphique pour une region specifique
    @app.callback(
        dash.dependencies.Output("lineplot-obesity-graph", "figure"),
        [dash.dependencies.Input('slider-obesity-group-graph', "value"),
        dash.dependencies.Input('radioitems-obesity-group', 'value'),
        dash.dependencies.Input('dropdown-obesity-group-location', 'value')]
    )
    def create_graph_group(interval, group_type, location):
        return graph_line_obesity_group(interval[0], interval[1], group_type, location)

    # OBESITY - Interactivite: Creation du graphique camembert, du classement par rapport au slider des annees
    @app.callback(
        [dash.dependencies.Output("label-obesity-miscellaneous", "children"),
        dash.dependencies.Output("piechart-obesity-miscellaneous", "figure"),
        dash.dependencies.Output("ranking-obesity-miscellaneous", "children"),
        dash.dependencies.Output("ranking-text-obesity-miscellaneous", "children")],
        [dash.dependencies.Input("slider-obesity-miscellaneous-graph", "value"),
        dash.dependencies.Input('radioitems-obesity-group', 'value'),
        dash.dependencies.Input('dropdown-obesity-group-location', 'value')]
    )
    def change_slider(value, group_type, location):
        # For the rank widget
        rank, n = rank_obesity_group(value, group_type, location)
        ranktxt =  "\n among " + ("countries" if group_type == "Countries" else "continents")

        return "During the year {}".format(value), graph_pie_obesity_group(value, group_type, location), "{}/{}".format(rank, n), ranktxt

    # ANALYTICS - Interactivite: Creation du graphique lineplot, de la correlation de l'obesite par rapport aux activites
    # bureautiques ou manuelles
    @app.callback(
        [dash.dependencies.Output("graph-lineplot-correlationD-analytics", "figure"),
        dash.dependencies.Output("graph-lineplot-correlationM-analytics", "figure"),
        dash.dependencies.Output("alert-correlationD-analytics", "children"),
        dash.dependencies.Output("alert-correlationM-analytics", "children")],
        [dash.dependencies.Input("dropdown-country-analytics", "value"),
        dash.dependencies.Input("radio-corr-type-analytics", "value")]
    )
    def change_country(country, corrtype):
        corrD = correlation_obesity_employment_analytics(country, "D", corrtype)
        corrM = correlation_obesity_employment_analytics(country, "M", corrtype)
        return (graph_obesity_employment_analytics(country, "D", corrtype),
        graph_obesity_employment_analytics(country, "M", corrtype),
        correlation_alert_component_analytics(country, "D", corrD, corrtype),
        correlation_alert_component_analytics(country, "M", corrM, corrtype))

    # ANALYTICS - Interactivite: Changement du type de graphique ('lineplot', 'heatmap'), apparition 
    # de la selection de pays seulement lorsque le type de visualisation est le 'lineplot'.
    @app.callback(
        [dash.dependencies.Output("graphs-analytics", "children"),
        dash.dependencies.Output("ui-dropdown-country-analytics", "children")],
        [dash.dependencies.Input("radio-graph-type-analytics", "value"),
        dash.dependencies.Input("radio-corr-type-analytics", "value")]
    )
    def change_graph_type(gtype, corrtype):

        heatmap = dcc.Graph(figure=heatmap_obesity_employment_analytics(corrtype))

        return (heatmap, None) if gtype == "heatmap" else (lineplot_graph, country_selection)

    # Titre de l'application
    app.title = "Dashboard"

    # Execute l'application Dash sur un serveur web local
    app.run_server(debug=True)

    pass


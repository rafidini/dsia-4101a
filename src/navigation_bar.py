# Import
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

# Couleurs pour la barre de navigation
colors = {
    'theme':'dark',
    'sidebar':'#2b2b2b'
}

# Barre de navigation
navigationBar = dbc.NavbarSimple(
    brand= "Dashboard",
    brand_href="obesity",
    color=colors['theme'],
    dark=True,
    children=[
        dbc.NavItem(dbc.NavLink("Obesity", href="obesity")),
        dbc.NavItem(dbc.NavLink("Employment", href="employment")),
        dbc.NavItem(dbc.NavLink("Analytics", href="analytics")),
    ]
)

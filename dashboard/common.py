from dash import html
import dash_bootstrap_components as dbc
from config import app


def to_doc(section='', title='Consulter la documentation'):
    link = 'doc/dashboard.html' + section
    return dbc.Button(html.I(className="fa fa-info"), external_link=True,
                      href=app.get_asset_url(link), target='_blank', title=title, size='sm')


def info_header(header, section='', title='Consulter la documentation'):
    return dbc.Row([dbc.Col(header, width='auto'), dbc.Col(to_doc(section, title), width='auto')], align='center', justify='between')


def info_surface(surface):
    if surface >= 10000:
        return f'{round(surface/1000)/10} ha'
    elif surface > 0:
        return f'{round(surface)} m<sup>2</sup>'
    else:
        return ''

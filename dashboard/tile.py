from config import IGN_KEY, app, ns
import dash_leaflet as dl

IGN_OPEN_URL = (
    "https://data.geopf.fr/wmts?"
    + "SERVICE=WMTS"
    + "&REQUEST=GetTile"
    + "&VERSION=1.0.0"
    + "&EXCEPTIONS=text/xml"
    + "&STYLE=normal"
    + "&TILEMATRIXSET=PM"
    + "&FORMAT=image/jpeg"
    + "&TILEMATRIX={z}"
    + "&TILEROW={y}"
    + "&TILECOL={x}"
)


IGN_PNG_URL = (
    "https://data.geopf.fr/wmts?"
    + "SERVICE=WMTS"
    + "&REQUEST=GetTile"
    + "&VERSION=1.0.0"
    + "&EXCEPTIONS=text/xml"
    + "&STYLE=normal"
    + "&TILEMATRIXSET=PM"
    + "&FORMAT=image/png"
    + "&TILEMATRIX={z}"
    + "&TILEROW={y}"
    + "&TILECOL={x}"
)


def ign(name=None, date="2000-2005"):
    if name == "ortho":
        return dl.TileLayer(
            url=IGN_OPEN_URL + "&LAYER=HR.ORTHOIMAGERY.ORTHOPHOTOS",
            minZoom=0,
            maxZoom=19,
            tileSize=256,
            attribution="Orthophotos - Carte © IGN/Geoportail",
        )
    if name == "orthohisto":
        return dl.TileLayer(
            url=IGN_OPEN_URL + "&LAYER=ORTHOIMAGERY.ORTHOPHOTOS" + date,
            minZoom=0,
            maxZoom=19,
            tileSize=256,
            attribution="Orthophotos - Carte © IGN/Geoportail",
        )
    if name == "pngorthohisto":
        return dl.TileLayer(
            url=IGN_PNG_URL + "&LAYER=ORTHOIMAGERY.ORTHOPHOTOS" + date,
            minZoom=0,
            maxZoom=19,
            tileSize=256,
            attribution="Orthophotos - Carte © IGN/Geoportail",
        )
    if name == "carte" and IGN_KEY is not None:
        return dl.TileLayer(
            url="https://data.geopf.fr/private/wmts?"
            + "apikey="
            + IGN_KEY
            + "&REQUEST=GetTile&SERVICE=WMTS&VERSION=1.0.0"
            + "&EXCEPTIONS=text/xml"
            + "&STYLE=normal"
            + "&TILEMATRIXSET=PM"
            + "&FORMAT=image/jpeg"
            + "&LAYER=GEOGRAPHICALGRIDSYSTEMS.MAPS"
            + "&TILEMATRIX={z}"
            + "&TILEROW={y}"
            + "&TILECOL={x}",
            minZoom=0,
            maxZoom=22,
            tileSize=256,
            opacity=0.6,
            attribution="© IGN/Geoportail",
        )
    else:
        return dl.TileLayer(
            url=IGN_OPEN_URL + "&LAYER=GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2",
            minZoom=0,
            maxNativeZoom=19,
            maxZoom=22,
            tileSize=256,
            attribution="Plan IGNV2 - Carte © IGN/Geoportail",
        )


def stamen(name=None):
    if name == "toner":
        return dl.TileLayer(
            url="//stamen-tiles.a.ssl.fastly.net/toner-background/{z}/{x}/{y}.png",
            attribution="Map tiles by Stamen Design, CC BY 3.0, Map data by OpenStreetMap contributors",
        )
    return dl.TileLayer(
        url="http://{s}.tile.stamen.com/toner/{z}/{x}/{y}.png",
        attribution="Stamen",
    )

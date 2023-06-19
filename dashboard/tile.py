from config import IGN_KEY, app, ns
import dash_leaflet as dl


def ign(name=None, date="2000-2005"):
    if name == 'ortho':
        return dl.TileLayer(url="https://wxs.ign.fr/ortho/wmts?" +
                            "&REQUEST=GetTile&SERVICE=WMTS&VERSION=1.0.0" +
                            "&STYLE=normal" +
                            "&TILEMATRIXSET=PM" +
                            "&FORMAT=image/jpeg" +
                            "&LAYER=HR.ORTHOIMAGERY.ORTHOPHOTOS" +
                            "&TILEMATRIX={z}" +
                            "&TILEROW={y}" +
                            "&TILECOL={x}",
                            minZoom=0,
                            maxZoom=19,
                            tileSize=256,
                            attribution="IGN-F/Geoportail")
    if name == 'orthohisto':
        return dl.TileLayer(url="https://wxs.ign.fr/orthohisto/geoportail/wmts?" +
                            "&REQUEST=GetTile&SERVICE=WMTS&VERSION=1.0.0" +
                            "&STYLE=normal" +
                            "&TILEMATRIXSET=PM" +
                            "&FORMAT=image/jpeg" +
                            "&LAYER=ORTHOIMAGERY.ORTHOPHOTOS"+ date +
                            "&TILEMATRIX={z}" +
                            "&TILEROW={y}" +
                            "&TILECOL={x}",
                            minZoom=0,
                            maxZoom=19,
                            tileSize=256,
                            attribution="IGN-F/Geoportail")
    if name == 'WMSorthohisto':
        return dl.WMSTileLayer(url='https://wxs.ign.fr/orthohisto/geoportail/r/wms?',
                               tileSize=256,
                               layers="ORTHOIMAGERY.ORTHOPHOTOS"+ date,
                               attribution="IGN-F/Geoportail",
                               )
    if name == 'carte' and IGN_KEY is not None:
        return dl.TileLayer(url="https://wxs.ign.fr/" + IGN_KEY + "/wmts?" +
                            "&REQUEST=GetTile&SERVICE=WMTS&VERSION=1.0.0" +
                            "&STYLE=normal" +
                            "&TILEMATRIXSET=PM" +
                            "&FORMAT=image/jpeg" +
                            "&LAYER=GEOGRAPHICALGRIDSYSTEMS.MAPS" +
                            "&TILEMATRIX={z}" +
                            "&TILEROW={y}" +
                            "&TILECOL={x}",
                            minZoom=0,
                            maxZoom=18,
                            tileSize=256,
                            opacity=0.6,
                            attribution="IGN-F/Geoportail")
    else:
        return dl.TileLayer(
            url="https://wxs.ign.fr/cartes/wmts?" +
            "&REQUEST=GetTile&SERVICE=WMTS&VERSION=1.0.0" +
            "&STYLE=normal" +
            "&TILEMATRIXSET=PM" +
            "&FORMAT=image/png" +
            "&LAYER=GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2" +
            "&TILEMATRIX={z}" +
            "&TILEROW={y}" +
            "&TILECOL={x}",
            minZoom=0,
            maxZoom=19,
            tileSize=256,
            attribution="IGN-F/Geoportail",
        )


def stamen(name=None):
    if name == 'toner':
        return dl.TileLayer(
            url='//stamen-tiles.a.ssl.fastly.net/toner-background/{z}/{x}/{y}.png',
            attribution='Map tiles by Stamen Design, CC BY 3.0, Map data by OpenStreetMap contributors',
        )
    return dl.TileLayer(
        url="http://{s}.tile.stamen.com/toner/{z}/{x}/{y}.png",
        attribution="Stamen",
    )

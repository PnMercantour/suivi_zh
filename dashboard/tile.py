from config import IGN_KEY, app, ns
import dash_leaflet as dl

def ign(name=None):
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
    if name == 'carte':
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
                      attribution="IGN-F/Geoportail")
    else:
        return dl.TileLayer(url="https://wxs.ign.fr/cartes/wmts?" +
                      "&REQUEST=GetTile&SERVICE=WMTS&VERSION=1.0.0" +
                      "&STYLE=normal" +
                      "&TILEMATRIXSET=PM" +
                      "&FORMAT=image/jpeg" +
                      "&LAYER=GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2" +
                      "&TILEMATRIX={z}" +
                      "&TILEROW={y}" +
                      "&TILECOL={x}",
                      minZoom=0,
                      maxZoom=19,
                      tileSize=256,
                      attribution="IGN-F/Geoportail")
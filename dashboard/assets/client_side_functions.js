window.PNM = Object.assign({}, window.PNM, {
  zh: {
    pourChaqueVallee: (feature, layer) => {
      if (!feature.properties) {
        return;
      }
      if (feature.properties.nom) {
        layer.bindTooltip(feature.properties.nom);
      }
      if (feature.properties.nom_vallee) {
        layer.bindTooltip(feature.properties.nom_vallee);
      }
    },
    pourChaqueSite: (feature, layer) => {
      if (!feature.properties) {
        return;
      }
      if (feature.properties.nom_site) {
        layer.bindTooltip(feature.properties.nom_site);
      }
    },
    valleeFilter: (feature, context) => {
      let hideout = context.props.hideout;
      return hideout.vallee == null;
    },
    siteFilter: (feature, context) => {
      let hideout = context.props.hideout;
      return hideout.site == null && hideout.vallee != null && feature.properties.id_vallee == hideout.vallee;
    },
    zhFilter: (feature, context) => {
      let hideout = context.props.hideout;
      return hideout.site != null;
    },
    sitePointToLayer: (feature, latlng, context) => {
      const unselected = { color: "grey", radius: 8, fillOpacity: 0.8 };
      const selected = {
        radius: 8,
        color: "blue",
        fillColor: "blue",
        fillOpacity: 0.8,
      };
      let circleOptions;
      if (context.props.hideout) {
        if (context.props.hideout.site != null) {
          if (feature.properties.id == context.props.hideout.site) {
            circleOptions = selected;
          } else {
            circleOptions = unselected;
          }
        } else if (context.props.hideout.vallee != null) {
          if (feature.properties.id_vallee == context.props.hideout.vallee) {
            circleOptions = selected;
          } else {
            circleOptions = unselected;
          }
        } else {
          circleOptions = selected;
        }
      } else {
        circleOptions = selected;
      }
      return L.circleMarker(latlng, circleOptions); // send a simple circle marker.
    },
    valleeStateStyle: (feature, context) => {
      if (context.props.hideout.vallee != null) {
        return {
          color: 'white',
          fillOpacity: 0,
        }
      }
      let color = "red";
      let etat = feature.properties.etat;
      if (etat >= 2 / 3) color = "green";
      else if (etat >= 1 / 3) color = "orange";
      return {
        color:'white',
        fillColor: color,
        fillOpacity:0.8,
      }
    },
    siteStatePointToLayer: (feature, latlng, context) => {
      let color = "red";
      let etat = feature.properties.etat;
      if (etat >= 2 / 3) color = "green";
      else if (etat >= 1 / 3) color = "orange";
      return L.circleMarker(latlng, {
        radius: 14,
        color: 'white',
        fillColor: color,
        fillOpacity: 0.8,
      });
    },

    zhColor: (feature, context) => {
      const colormap = { bon: "green", moyen: "orange", mauvais: "red" };
      if (context.props.hideout.zh) {
        if (feature.properties.id == context.props.hideout.zh) {
          return {
            fillColor: colormap[feature.properties.etat_zh],
            fillOpacity: 1,
          };
        } else {
          return { color: colormap[feature.properties.etat_zh] };
        }
      } else {
        return { color: colormap[feature.properties.etat_zh], fillOpacity: 1 };
      }
    },
  },
});

console.log("PNM client side functions loaded");

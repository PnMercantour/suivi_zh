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
      return (
        hideout.site == null &&
        hideout.vallee != null &&
        feature.properties.id_vallee == hideout.vallee
      );
    },
    zhFilter: (feature, context) => {
      let hideout = context.props.hideout;
      return hideout.site != null;
    },
    defensFilter: (feature, context) => {
      let hideout = context.props.hideout;
      return hideout.site != null;
    },
    siteSituationToLayer: (feature, latlng, context) => {
      let color = "grey",
        radius = 4;
      if (feature.properties.id_site == context.props.hideout.site) {
        radius = 7;
        let etat = feature.properties.etat;
        if (etat >= 2 / 3) color = "green";
        else if (etat >= 1 / 3) color = "orange";
        else color = "red";
      } else if (
        context.props.hideout.vallee == null ||
        (feature.properties.id_site != null &&
          context.props.hideout.vallee == feature.properties.id_vallee)
      ) {
        color = "blue";
      }
      return L.circleMarker(latlng, {
        pane: "site_pane",
        color: color,
        fillColor: color,
        radius: radius,
        fillOpacity: 0.8,
      });
    },
    valleeSituationStyle: (feature, context) => {
      if (
        context.props.hideout.site != null ||
        context.props.hideout.vallee != feature.properties.id_vallee
      ) {
        return {
          color: "grey",
          fillOpacity: 0.4,
          pane: "vallee_pane",
        };
      }
      let color = "red";
      let etat = feature.properties.etat;
      if (etat >= 2 / 3) color = "green";
      else if (etat >= 1 / 3) color = "orange";
      return {
        color: color,
        fillColor: color,
        fillOpacity: 0.4,
        pane: "vallee_pane",
      };
    },
    valleeStateStyle: (feature, context) => {
      if (context.props.hideout.vallee != null) {
        return {
          color: "white",
          fillOpacity: 0,
        };
      }
      let color = "red";
      let etat = feature.properties.etat;
      if (etat >= 2 / 3) color = "green";
      else if (etat >= 1 / 3) color = "orange";
      return {
        color: "white",
        fillColor: color,
        fillOpacity: 0.8,
      };
    },
    siteStatePointToLayer: (feature, latlng, context) => {
      let color = "red";
      let etat = feature.properties.etat;
      if (etat >= 2 / 3) color = "green";
      else if (etat >= 1 / 3) color = "orange";
      return L.circleMarker(latlng, {
        radius: 14,
        color: "white",
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

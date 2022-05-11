window.PNM = Object.assign({}, window.PNM, {
  zh: {
    pourChaqueVallee: (feature, layer) => {
      layer.bindTooltip(feature.properties.nom_vallee);
    },
    pourChaqueSite: (feature, layer) => {
      layer.bindTooltip(feature.properties.nom_site);
    },
    defensTooltip: (feature, layer) => {
      console.log(feature);
      layer.bindTooltip(
        `défens ${feature.properties.nom_defens}: ${feature.properties.surface} m2 (${feature.properties.annee})`
      );
    },
    siteFilter: (feature, context) => {
      let hideout = context.props.hideout;
      return (
        hideout.site == null &&
        (hideout.vallee == null ||
          feature.properties.id_vallee == hideout.vallee)
      );
    },
    zhFilter: (feature, context) => {
      let hideout = context.props.hideout;
      return feature.properties.id_site == hideout.site;
    },
    defensFilter: (feature, context) => {
      let hideout = context.props.hideout;
      return feature.properties.id_site == hideout.site;
    },
    siteSituationToLayer: (feature, latlng, context) => {
      let color = "grey",
        radius = 4;
      if (feature.properties.id_site == context.props.hideout.site) {
        radius = 7;
        let etat = feature.properties.etat;
        if (etat == null) color = "grey";
        else if (etat >= 2 / 3) color = "green";
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
      return {
        color: "grey",
        fillOpacity: 0.8,
        pane: "vallee_pane",
      };
    },
    valleeStateStyle: (feature, context) => {
      if (context.props.hideout.vallee == null) {
        return {
          color: "white",
          fillOpacity: 0,
          pane: "detail_vallee_pane",
        };
      }
      if (context.props.hideout.site == null) {
        if (context.props.hideout.vallee == feature.properties.id_vallee) {
          return {
            color: "yellow",
            fillOpacity: 0,
            pane: "detail_vallee_pane_s",
          };
        }
      }
      return {
        color: "white",
        fillOpacity: 0,
        pane: "detail_vallee_pane",
      };
    },
    siteStatePointToLayer: (feature, latlng, context) => {
      let color = "white";
      if (feature.properties.n_defens != null) color = "black";
      let fill_color;
      let etat = feature.properties.etat;
      if (etat == null) fill_color = "grey";
      else if (etat >= 2 / 3) fill_color = "green";
      else if (etat >= 1 / 3) fill_color = "orange";
      else fill_color = "red";
      return L.circleMarker(latlng, {
        radius: 10,
        color: color,
        fillColor: fill_color,
        fillOpacity: 0.8,
        pane: "detail_site_pane",
      });
    },

    zhStyle: (feature, context) => {
      const colormap = { bon: "green", moyen: "orange", mauvais: "red" };
      if (context.props.hideout.zh != null) {
        if (feature.properties.id_zh == context.props.hideout.zh) {
          return {
            color: "yellow",
            fillColor: colormap[feature.properties.etat],
            fillOpacity: 0.8,
          };
        } else {
          return {
            color: colormap[feature.properties.etat],
            fillOpacity: 0.2,
          };
        }
      } else {
        return {
          color: colormap[feature.properties.etat],
          fillOpacity: 0.5,
        };
      }
    },
  },
});

console.log("PNM client side functions loaded");

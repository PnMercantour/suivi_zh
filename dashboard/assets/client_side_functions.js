window.PNM = Object.assign({}, window.PNM, {
  zh: {
    pourChaqueVallee: (feature, layer) => {
      layer.bindTooltip(feature.properties.nom_vallee);
    },

    // Situation map
    siteSituationFilter: (feature, context) => {
      let hideout = context.props.hideout;
      return feature.properties.id == hideout.site;
    },
    siteSituationToLayer: (feature, latlng, context) => {
      let color = "white",
        radius = 2,
        opacity = 1,
        pane = "site_pane";
      if (feature.properties.id == context.props.hideout.site) {
        radius = 4;
        pane = "selected_site_pane";
        opacity = 1;
        let etat = feature.properties.etat;
        if (etat == null) color = "black";
        else if (etat == "bon") color = "green";
        else if (etat == "moyen") color = "orange";
        else color = "red";
      }
      return L.circleMarker(latlng, {
        pane: "site_pane",
        color: color,
        fillColor: color,
        radius: radius,
        opacity: opacity,
        fillOpacity: opacity,
      });
    },
    valleeSituationStyle: (feature, context) => {
      if (
        context.props.hideout.site != null ||
        context.props.hideout.vallee != feature.properties.id
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
    // main map
    siteTooltip: (feature, layer) => {
      let defens = feature.properties.ids_defens
        ? `
<br>${feature.properties.ids_defens.length} defens sur ${feature.properties.s_defens} m<sup>2</sup>
`
        : "";
      let surface = feature.properties.s_zh
        ? `de ${feature.properties.s_zh} m<sup>2</sup>`
        : "inconnue";
      let etat = feature.properties.etat;
      let etat_descr;
      if (etat == null) etat_descr = "Etat inconnu";
      else if (etat == "bon") etat_descr = "Bon état";
      else if (etat == "moyen") etat_descr = "Etat moyen";
      else etat_descr = "Etat dégradé";
      layer.bindTooltip(`
Site <strong>${feature.properties.nom_site}</strong>
<br> Etendue ${surface}
${defens}
<br>${etat_descr}
<br><small>Id #${feature.properties.id}</small>
`);
    },

    zhTooltip: (feature, layer) => {
      let etat = feature.properties.etat;
      let etat_descr;
      if (etat == "bon") etat_descr = "Bon état";
      else if (etat == "moyen") etat_descr = "Etat moyen";
      else if (etat == "mauvais") etat_descr = "Etat dégradé";
      else etat_descr = "Etat inconnu";
      layer.bindTooltip(`
<strong>Zone humide</strong> 
<br> ${feature.properties.surface} m<sup>2</sup>
<br>${etat_descr} 
<br> <em>${feature.properties.source} (${feature.properties.annee})</em>
<br><small>Id #${feature.properties.id}</small>
`);
    },

    defensTooltip: (feature, layer) => {
      layer.bindTooltip(`
Défens <strong>${feature.properties.nom_defens}</strong>
<br> Surface de ${feature.properties.surface} m<sup>2</sup>
<br>Mis en place en ${feature.properties.annee}
<br><small>Id #${feature.properties.id}</small>
`);
    },

    ebfTooltip: (feature, layer) => {
      layer.bindTooltip(`
<strong>Espace de bon fonctionnement</strong> 
<br>Etendue de ${Math.round(feature.properties.surface / 10000)} ha
<br><small>Id #${feature.properties.id}</small>
`);
    },

    rhomeoTooltip: (feature, layer) => {
      layer.bindTooltip(`
<strong>Point de mesure Rhomeo</strong> 
<br>${feature.properties.releves} relevés
<br><em>${feature.properties.organisme}</em>
`);
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
    ebfFilter: (feature, context) => {
      let hideout = context.props.hideout;
      return hideout.vallee != null;
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
        if (context.props.hideout.vallee == feature.properties.id) {
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
      let fill_color;
      let etat = feature.properties.etat;
      if (etat == null) fill_color = "blue";
      else if (etat == "bon") fill_color = "green";
      else if (etat == "moyen") fill_color = "orange";
      else fill_color = "red";

      let radius = context.props.hideout.vallee ? 10 : 5;
      let color = feature.properties.ids_defens != null ? "black" : fill_color;

      return L.circleMarker(latlng, {
        radius: radius,
        color: color,
        fillColor: fill_color,
        fillOpacity: 1,
        pane: "detail_site_pane",
      });
    },

    rhomeoPointToLayer: (feature, latlng, context) => {
      return L.circleMarker(latlng, {
        radius: 4,
        color: "purple",
        fillOpacity: 0.8,
        pane: "rhomeo_pane",
      });
    },

    zhStyle: (feature, context) => {
      const colormap = { bon: "green", moyen: "orange", mauvais: "red" };
      if (context.props.hideout.zh != null) {
        if (feature.properties.id == context.props.hideout.zh) {
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

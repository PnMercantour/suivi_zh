window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: (feature, layer) => {
            if (!feature.properties) {
                return
            }
            if (feature.properties.nom_site) {
                layer.bindTooltip(feature.properties.nom_site)
            }
        }

    }
});
window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, latlng) {
            const flag = L.icon({
                iconUrl: `https://flagcdn.com/64x48/${feature.properties.iso2}.png`,
                iconSize: [64, 48]
            });
            return L.marker(latlng, {
                icon: flag
            });
        }
    }
});
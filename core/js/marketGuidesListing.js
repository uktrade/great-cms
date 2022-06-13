export const initializeMap = async (cognitoPoolId) => {
  const markets = JSON.parse(
    document.getElementById('market-guides-results-json').textContent
  )
  const ukCentre = [-3.425, 55.37]
  const bounds = new maplibregl.LngLatBounds()

  const map = await AmazonLocation.createMap(
    {
      identityPoolId: cognitoPoolId,
    },
    {
      container: 'market-guides-map',
      center: [0,0],
      zoom: 1,
      minZoom: 0,
      style: 'OpportunitiesListing',
      dragRotate: false,
      touchPitch: false,
      pitchWithRotate: false,
    }
  )

  map.addControl(
    new maplibregl.NavigationControl({ showCompass: false }),
    'top-right'
  )

  map.addControl(new maplibregl.FullscreenControl(), 'top-right')

  markets.forEach(function (market) {
    const lngLat = market.latlng.split(',').map(parseFloat).reverse()

    try {
      bounds.extend(lngLat)
    } catch {
      console.error('Error parsing lat/long for market:', market.heading)
      return
    }

    const el = document.createElement('div');
    el.className = 'market-guides-marker';

    let popupMarkup = '<a href="' + market.url + '">'
    popupMarkup += '<h3 class="">' + market.heading + '</h3>'
    popupMarkup += '</a>'

    new maplibregl.Marker(el)
      .setLngLat(lngLat)
      .setPopup(
        new maplibregl.Popup({ closeButton: false }).setHTML(popupMarkup)
      )
      .addTo(map)
  })

  if (bounds.length) {
    map.fitBounds(bounds, { padding: 20, maxZoom: 8 })
  }
}

export default {
  initializeMap,
}

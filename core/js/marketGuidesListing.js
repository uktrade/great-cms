const style = {
  version: 8,
  sources: {
    esri: {
      attribution:
        'Esri, HERE, Garmin, FAO, NOAA, USGS, © OpenStreetMap contributors, and the GIS User Community',
      maxzoom: 15,
      tiles: [
        'https://maps.geo.eu-west-1.amazonaws.com/maps/v0/maps/OpportunitiesListing/tiles/{z}/{x}/{y}',
      ],
      type: 'vector',
    },
  },
  sprite:
    'https://maps.geo.eu-west-1.amazonaws.com/maps/v0/maps/OpportunitiesListing/sprites/sprites',
  glyphs:
    'https://maps.geo.eu-west-1.amazonaws.com/maps/v0/maps/OpportunitiesListing/glyphs/{fontstack}/{range}.pbf',
  layers: [
    {
      filter: ['==', '_symbol', 0],
      id: 'Land',
      layout: {},
      minzoom: 0,
      paint: {
        'fill-color': '#cbd2d3',
      },
      source: 'esri',
      'source-layer': 'Land',
      type: 'fill',
    },
    {
      filter: ['==', '_symbol', 1],
      id: 'Land/Ice',
      layout: {},
      minzoom: 0,
      paint: {
        'fill-color': '#cbd2d3',
      },
      source: 'esri',
      'source-layer': 'Land',
      type: 'fill',
    },
    {
      id: 'Marine area/bathymetry depth 1',
      layout: {},
      minzoom: 0,
      paint: {
        'fill-color': '#DCF3FC',
      },
      source: 'esri',
      'source-layer': 'Marine area',
      type: 'fill',
    },
    {
      filter: ['all', ['==', '_symbol', 0]],
      id: 'Boundary line/Admin0/line',
      layout: {
        'line-cap': 'round',
        'line-join': 'round',
      },
      paint: {
        'line-color': '#bababa',
        'line-width': 1.2,
      },
      source: 'esri',
      'source-layer': 'Boundary line',
      type: 'line',
    },
  ],
  created: '0001-01-01T00:00:00Z',
  modified: '0001-01-01T00:00:00Z',
}

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
      center: ukCentre,
      zoom: 0,
      minZoom: 0,
      style: 'OpportunitiesListing',
      dragRotate: false,
      touchPitch: false,
      pitchWithRotate: false,
    }
  )

  map.addControl(
    new maplibregl.NavigationControl({ showCompass: false }),
    'bottom-right'
  )

  markets.forEach(function (market) {
    const lngLat = market.latlng.split(',').map(parseFloat).reverse()

    try {
      bounds.extend(lngLat)
    } catch {
      console.error('Error parsing lat/long for market:', market.heading)
      return
    }

    let popupMarkup = '<a href="' + market.url + '">'
    popupMarkup += '<h3 class="">' + market.heading + '</h3>'
    popupMarkup += '</a>'

    new maplibregl.Marker()
      .setLngLat(lngLat)
      .setPopup(
        new maplibregl.Popup({ closeButton: false }).setHTML(popupMarkup)
      )
      .addTo(map)
  })

  map.fitBounds(bounds, { padding: 20, maxZoom: 8 })
}

export default {
  initializeMap,
}

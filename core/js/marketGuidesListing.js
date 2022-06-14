export const listSectors = (tags, selected) => {
  let sectors = tags
  let splitAt = 2

  if (selected.length) {
    // Move non-selected sectors to the end of the list
    const selectedMatches = tags.filter(x => selected.includes(x))
    const others = tags.filter(x => !selected.includes(x))
    sectors = [...selectedMatches, ...others]
    splitAt = selectedMatches.length
  }

  const shownSectors = sectors.slice(0, splitAt)
  const hiddenSectors = sectors.slice(splitAt)

  if (hiddenSectors.length === 1) {
    shownSectors.push(hiddenSectors.pop())
  }

  if (hiddenSectors.length) {
    return `${shownSectors.join(', ')} and ${hiddenSectors.length} more`
  } else if (shownSectors.length <= 2) {
    return shownSectors.join(' and ')
  } else {
    return `${shownSectors.slice(0, - 1).join(', ')} and ${shownSectors[shownSectors.length - 1]}`
  }
}

export const initializeMap = async (cognitoPoolId, markets, selected = []) => {
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

  const bounds = new maplibregl.LngLatBounds()

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

    let popupMarkup = '<a class="markets-map-infobox" href="' + market.url + '">'
    popupMarkup += '<h3 class="heading-small">' + market.heading + '</h3>'
    if (market.tags) {
      popupMarkup += '<p>High potential in ' + listSectors(market.tags, selected) + '</p>'
    }
    popupMarkup += '</a>'

    new maplibregl.Marker(el)
      .setLngLat(lngLat)
      .setPopup(
        new maplibregl.Popup({ closeButton: false }).setHTML(popupMarkup)
      )
      .addTo(map)
  })

  if (markets.length) {
    map.fitBounds(bounds, { padding: 20, maxZoom: 8 })
  }
}

export default {
  initializeMap,
}

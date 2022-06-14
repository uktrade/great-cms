import { initializeMap, listSectors } from "../marketGuidesListing";

const mockMarkets = [
  {
    "heading": "Colombia",
    "tags": [
      "Aerospace",
      "Construction",
    ],
    "latlng": "4.0,-72.0",
    "url": "/markets/colombia/"
  },
  {
    "heading": "Denmark",
    "tags": [
      "Aerospace",
      "Cleantech",
    ],
    "latlng": "56.0,10.0",
    "url": "/markets/denmark/"
  }
]
const mocks = {
  addControl: jest.fn(),
  fitBounds: jest.fn(),
  extend: jest.fn(),
  addTo: jest.fn(),
  setPopup: jest.fn(() => ({
    addTo: mocks.addTo
  })),
  setLatLng: jest.fn(() => ({
    setPopup: mocks.setPopup
  })),
  setHTML: jest.fn()
}


beforeEach(() => {
  // Mock mock mock
  window.AmazonLocation = {
    createMap: jest.fn(async () => ({
      addControl: mocks.addControl,
      fitBounds: mocks.fitBounds
    }))
  }
  window.maplibregl = {
    LngLatBounds: jest.fn(() => ({
      extend: mocks.extend,
    })),
    NavigationControl: jest.fn(),
    FullscreenControl: jest.fn(),
    Marker: jest.fn(() => ({
      setLngLat: mocks.setLatLng
    })),
    Popup: jest.fn(() => ({
      setHTML: mocks.setHTML
    }))
  }
})

describe('Market Guides Listing', () => {
  it('sets up the map', async () => {
    await initializeMap('fooCognitoId', [], [])

    expect(AmazonLocation.createMap).toHaveBeenCalled()
    expect(AmazonLocation.createMap.mock.calls[0][0]).toEqual({
      identityPoolId: 'fooCognitoId',
    })
    expect(mocks.addControl).toHaveBeenCalledTimes(2)

    // No markets to add to map
    expect(maplibregl.Marker).not.toHaveBeenCalled()
    expect(mocks.fitBounds).not.toHaveBeenCalled()
  })

  it('adds markers to the map', async () => {
    await initializeMap('fooCognitoId', mockMarkets, [])

    expect(maplibregl.Marker).toHaveBeenCalledTimes(2)
    expect(mocks.extend).toHaveBeenCalledTimes(2)
    expect(mocks.extend.mock.calls[0][0]).toEqual([-72, 4])
    expect(mocks.setLatLng).toHaveBeenCalledTimes(2)
    expect(mocks.setLatLng.mock.calls[0][0]).toEqual([-72, 4])
    expect(mocks.setHTML).toHaveBeenCalledTimes(2)
    expect(mocks.setHTML.mock.calls[0][0]).toMatch('Colombia')
    expect(mocks.setHTML.mock.calls[0][0]).toMatch('href="/markets/colombia/"')
    expect(mocks.addTo).toHaveBeenCalledTimes(2)
    expect(mocks.fitBounds).toHaveBeenCalled()
  })

  it.each([
    // No selection
    [['Aerospace', 'Automotive'], [], 'Aerospace and Automotive'],
    [['Aerospace'], [], 'Aerospace'],
    [['Aerospace', 'Automotive', 'Foo'], [], 'Aerospace, Automotive and Foo'],
    [['Aerospace', 'Automotive', 'Foo', 'Bar'], [], 'Aerospace, Automotive and 2 more'],
    [['A', 'B', 'C', 'D', 'E', 'F', 'G'], [], 'A, B and 5 more'],
    // Selected tags should show first
    [['A', 'B', 'C', 'D', 'E', 'F', 'G'], ['B', 'D', 'G', 'E'], 'B, D, E, G and 3 more']
  ])('renders %j, %j into %j', (tags, selected, expected) => {
    expect(listSectors(tags, selected)).toEqual(expected)
  })
})

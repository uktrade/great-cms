import React from 'react'
import ReactDOM from 'react-dom'
import { act, Simulate } from 'react-dom/test-utils'
import { SectorChooser } from '@src/components/SectorChooser'

let container

beforeEach(() => {
  container = document.createElement('div')
  document.body.appendChild(container)
})

afterEach(() => {
  document.body.removeChild(container)
  container = null
})

it('shows the list of sectors and hides button on click', () => {

  const sectorList = ["Aerospace", "Advanced manufacturing", "Airports", "Agriculture, horticulture and fisheries"]

  act(() => {
    ReactDOM.render(<SectorChooser sectorList={sectorList} />, container)
  })

  const button = container.querySelector('#sector-chooser-button')

  act(() => {
    Simulate.click(button)
  })

  expect(container.querySelector('#sector-chooser-button')).toBeFalsy()

  const sectors = container.querySelector('#sector-list').children

  expect(sectors.length).toEqual(4)

})

it('shows selected sectors in sector list and shows save button', () => {

  const sectorList = ["Aerospace", "Advanced manufacturing", "Airports", "Agriculture, horticulture and fisheries"]

  act(() => {
    ReactDOM.render(<SectorChooser sectorList={sectorList} initialSelectedSectors={[]} />, container)
  })

  const sectorButton = container.querySelector('#sector-chooser-button')

  act(() => {
    Simulate.click(sectorButton)
  })

  expect(container.querySelector('#sector-chooser .g-button')).toBeFalsy()

  const aerospace = container.querySelector('#aerospace')
  const manufacturing = container.querySelector('#advanced-manufacturing')

  act(() => {
    Simulate.click(aerospace)
    Simulate.click(manufacturing)
  })

  const selected = container.querySelector('#sector-list').getElementsByClassName('selected')

  expect(selected.length).toEqual(2)

  expect(container.querySelector('#sector-chooser .g-button')).toBeTruthy()

})

it('can remove selected sectors in sector list and hide save button', () => {

  const sectorList = ["Aerospace", "Advanced manufacturing", "Airports", "Agriculture, horticulture and fisheries"]
  const selectedSectors = ["Aerospace"]

  act(() => {
    ReactDOM.render(<SectorChooser sectorList={sectorList} initialSelectedSectors={selectedSectors} />, container)
  })

  const sectorButton = container.querySelector('#sector-chooser-button')

  act(() => {
    Simulate.click(sectorButton)
  })

  const selected = container.querySelector('#sector-list').getElementsByClassName('selected')

  expect(selected.length).toEqual(1)
  expect(selected[0].id).toEqual('aerospace')
  expect(container.querySelector('#sector-chooser .g-button')).toBeTruthy()

  act(() => {
    Simulate.click(selected[0])
  })

  expect(selected.length).toEqual(0)

  expect(container.querySelector('#sector-chooser .g-button')).toBeFalsy()

})

it('renders the sector chooser button with tooltip', () => {

  act(() => {
    ReactDOM.render(<SectorChooser sectorList={[]}/>, container)
  })

  const button = container.querySelector('button')
  const tooltip = container.querySelector('.sector-list-tooltip')

  expect(button.textContent).toBe('')
  expect(tooltip.textContent).toBe('Add sectors')

  expect(tooltip.className).toEqual(expect.stringContaining('hidden'))

  act(() => {
    Simulate.mouseOver(button)
  })

  expect(tooltip.className).not.toEqual(expect.stringContaining('hidden'))
})

it('shows selected sectors', () => {

  const sectorList = ["Aerospace", "Advanced manufacturing", "Airports", "Agriculture, horticulture and fisheries"]
  const selectedSectors = ["Aerospace", "Advanced manufacturing"]

  act(() => {
    ReactDOM.render(<SectorChooser sectorList={sectorList} initialSelectedSectors={selectedSectors} />, container)
  })

  const selectedButtons = container.querySelector('#selected-sectors').getElementsByClassName('selected')

  expect(selectedButtons.length).toEqual(2)
  expect(selectedButtons[0].id).toEqual('aerospace')
  expect(selectedButtons[1].id).toEqual('advanced-manufacturing')

})

it('removes sector on click', () => {

  const sectorList = ["Aerospace", "Advanced manufacturing", "Airports", "Agriculture, horticulture and fisheries"]
  const selectedSectors = ["Aerospace", "Advanced manufacturing"]

  act(() => {
    ReactDOM.render(<SectorChooser sectorList={sectorList} initialSelectedSectors={selectedSectors} />, container)
  })

  const selectedButtons = container.getElementsByClassName('selected')

  expect(selectedButtons.length).toEqual(2)

  const aerospace = container.querySelector('#aerospace')

  act(() => {
    Simulate.click(aerospace)
  })

  expect(selectedButtons.length).toEqual(1)

})

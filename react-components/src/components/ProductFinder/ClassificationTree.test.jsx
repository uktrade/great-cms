import React from 'react'
import fetchMock from 'fetch-mock'
import { render, waitFor } from '@testing-library/react'

import Services from '@src/Services'
import ClassificationTree, { buildClassificationTree } from './ClassificationTree'

import mockScheduleCheese from './fixtures/product-schedule-cheese.json'
import mockScheduleSoftware from './fixtures/product-schedule-software.json'
import mockScheduleSausage from './fixtures/product-schedule-sausage.json'

const mockErrorResponse = {
  uom: null,
  duties: null,
  errorCode: 123,
  desc: null,
  code: null,
  errorMessage: 'Invalid code',
  id: null,
  type: null,
  children: [],
}

describe('Product tree builder', () => {
  it('returns CHAPTER, HEADING and ITEM when an exact HS6 code match is found', () => {
    const treeLines = buildClassificationTree('040630', mockScheduleCheese)

    expect(treeLines).toEqual([
      {
        type: 'CHAPTER',
        description: 'Dairy produce; birds\' eggs; natural honey; edible products of animal origin, not elsewhere specified or included',
        id: '04',
      },
      { type: 'HEADING', description: 'Cheese and curd.', id: '0406' },
      { type: 'ITEM', description: 'Processed cheese, not grated or powdered', id: '040630', leaf: true },
    ])
  })

  it('uses the ORPHAN under HEADING as ITEM if no exact match found and the orphan has no siblings', () => {
    const treeLines = buildClassificationTree('852329', mockScheduleSoftware)

    expect(treeLines).toEqual([
      {
        type: 'CHAPTER',
        description: 'Electrical machinery and equipment and parts thereof; sound recorders and reproducers, television image and sound recorders and reproducers, and parts and accessories of such articles',
        id: '85',
      },
      {
        type: 'HEADING',
        description: 'Discs, tapes, solid-state non-volatile storage devices, “smart cards” and other media for the recording of sound or of other phenomena, whether or not recorded, including matrices and masters for the production of discs, but excluding products of chapter 37.',
        id: '8523',
      },
      { type: 'ITEM', description: 'Magnetic media', id: '8523*01', leaf: true },
    ])
  })

  it('repeats the HEADING as ITEM if no exact HS6 code match and no suitable ORPHAN found', () => {
    const treeLines = buildClassificationTree('160100', mockScheduleSausage)

    expect(treeLines).toEqual([
      {
        type: 'CHAPTER',
        description: 'Preparations of meat, of fish or of crustaceans, molluscs or other aquatic invertebrates',
        id: '16',
      },
      {
        type: 'HEADING',
        description: 'Sausages and similar products, of meat, meat offal, blood or insects; food preparations based on these products.',
        id: '1601',
      },
      {
        type: 'ITEM',
        description: 'Sausages and similar products, of meat, meat offal, blood or insects; food preparations based on these products.',
        id: 'leaf',
        leaf: true,
      },
    ])
  })
})

describe('Classification tree', () => {
  beforeEach(() => {
    Services.setConfig({
      apiLookupProductScheduleUrl: '/api/lookup-product-schedule/',
    })
  })

  afterEach(() => {
    fetchMock.restore()
  })

  it('Renders a spinner while fetching schedule', async () => {
    fetchMock.get(/\/api\/lookup-product-schedule\//, mockScheduleCheese)

    const { container } = render(<ClassificationTree hsCode="040630" />)

    expect(container.querySelector('.spinner')).toBeTruthy()

    await waitFor(() => container.querySelector('.classification-tree'))

    expect(container.querySelector('.spinner')).toBeNull()
  })

  it('Renders a classification tree', async () => {
    fetchMock.get(/\/api\/lookup-product-schedule\//, mockScheduleCheese)

    const { container, queryByText } = render(<ClassificationTree hsCode="040630" />)

    await waitFor(() => {
      expect(container.querySelector('.classification-tree')).toBeTruthy()
    })

    expect(queryByText('LIVE ANIMALS; ANIMAL PRODUCTS', { exact: false })).toBeNull()

    const levels = container.querySelectorAll('.classification-tree .grid')

    expect(levels).toHaveLength(3)
    expect(levels[0].textContent).toMatch('Dairy produce; birds\' eggs; natural honey; edible products of animal origin, not elsewhere specified or included')
    expect(levels[1].textContent).toMatch('Cheese and curd.')
    expect(levels[2].textContent).toMatch('Processed cheese, not grated or powdered')
  })

  it('Renders an error', async () => {
    fetchMock.get(/\/api\/lookup-product-schedule\//, mockErrorResponse)

    const { container } = render(<ClassificationTree hsCode="123462" />)

    await waitFor(() => {
      expect(container.querySelector('.classification-tree').textContent).toMatch(
        'Unable to show classification tree',
      )
    })
  })
})

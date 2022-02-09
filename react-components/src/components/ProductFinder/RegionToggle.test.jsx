import React from 'react'
import { render, waitFor } from '@testing-library/react'
import RegionToggle from './RegionToggle'

it('Opens and closes region when expandAll is close', async () => {
  const { container } = render(
    <RegionToggle
      index={1234}
      expandAllRegions={false}
      region="Test Region"
      countries="<span><li>a</li></span><span><li>b</li></span>"
    />,
  )

  const button = container.querySelector('button')

  expect(container.querySelector('.expand-section')).toBeTruthy()

  button.click()

  await waitFor(() => {
    expect(container.querySelector('.expand-section.open')).toBeTruthy()
  })
})

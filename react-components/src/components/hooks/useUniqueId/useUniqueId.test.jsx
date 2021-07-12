import React from 'react'
import { render } from '@testing-library/react'
import useUniqueId from '@src/components/hooks/useUniqueId'

const Component=() =>{
  const id = useUniqueId('id')
  return <span>{id}</span>
}
describe('useUniqueId', () => {
  it('Should return an id', () => {
    const { getByText } = render(<><Component/><Component/></>)
    expect(getByText('id-1')).toBeTruthy()
    expect(getByText('id-2')).toBeTruthy()
  })
})

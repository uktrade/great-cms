import React from 'react'
import { render } from '@testing-library/react'

import ErrorList from '@src/components/ErrorList'

describe('ErrorList', () => {
  it('handles no errors', () => {
    const { container } = render(<ErrorList errors={[]} />)

    expect(container.innerHTML).toEqual('')
  })

  it('handles one error', () => {
    const errors = ['something went wrong']
    const { container } = render(<ErrorList errors={errors} className="edie" />)

    expect(container.querySelectorAll('.edie li')).toHaveLength(1)
    expect(container.querySelector('.edie li').textContent).toEqual(
      'something went wrong'
    )
  })

  it('handles multiple errors', () => {
    const errors = ['something went wrong', 'something else went wrong']
    const { container } = render(<ErrorList errors={errors} className="edie" />)

    const errorItems = container.querySelectorAll('.edie li')
    expect(errorItems).toHaveLength(2)
    expect(errorItems[0].textContent).toEqual('something went wrong')
    expect(errorItems[1].textContent).toEqual('something else went wrong')
  })
})

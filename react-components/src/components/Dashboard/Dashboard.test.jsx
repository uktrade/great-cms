import React from  'react'
import { render } from '@testing-library/react'

import { Dashboard } from '.'
import { props as fixtures } from '../Sidebar/Sidebar.test'

const props = { sections: fixtures.sections }

const setup = ({...data}) => {

  const utils = render(<Dashboard {...data} />)

  return {
    ...utils
  }
}

describe('Dashboard', () => {
  describe('sections', () => {
    it('Should list links', () => {
      const { getByTitle, queryAllByText } = setup(props)
      expect(getByTitle('about us')).toBeInTheDocument()
      expect(getByTitle('contact us')).toBeInTheDocument()
      expect(getByTitle('our blog')).toBeInTheDocument()
      expect(queryAllByText('Coming soon')).toHaveLength(0)
    })

    it('Should list coming soon pages', () => {

      const sections = props.sections.map(obj => {
        if(obj.disabled === false)
          return {
            ...obj,
            disabled: true,
          }
        return obj
      });

      const { queryAllByText } = setup({
        ...props,
        sections
      })

      expect(queryAllByText('Coming soon')).toHaveLength(3)
    })
  })
})

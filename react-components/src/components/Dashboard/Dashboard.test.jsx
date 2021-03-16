import React from 'react'
import { render } from '@testing-library/react'

import { Dashboard } from '.'
import { props as fixtures } from '../Sidebar/Sidebar.test'

const props = {
  sections: fixtures.sections,
  exportPlanProgress: {
    section_progress: [
      { populated: 0, total: 10, url: 'section/about-us' },
      { populated: 0, total: 5, url: 'section/contact-us' },
      { populated: 2, total: 3, url: 'section/our-blog' },
    ],
  },
}

const setup = ({ ...data }) => {
  const utils = render(<Dashboard {...data} />)

  return {
    ...utils,
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
      const sections = props.sections.map((obj) => {
        if (obj.disabled === false)
          return {
            ...obj,
            disabled: true,
          }
        return obj
      })

      const { queryAllByText } = setup({
        ...props,
        sections,
      })

      expect(queryAllByText('Coming soon')).toHaveLength(3)
    })
  })
  it('Should have tasks completed', () => {
    const { getByText } = setup(props)
    getByText('0 out of 10 questions answered')
    getByText('0 out of 5 questions answered')
    getByText('2 out of 3 questions answered')
  })
})

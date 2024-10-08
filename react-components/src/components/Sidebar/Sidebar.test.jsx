import React from  'react'
import { render, fireEvent, waitFor } from '@testing-library/react'
import { Provider } from 'react-redux'
import Services from '@src/Services'

import { Sidebar } from '.'

export const props = {
  logo: 'www.example.com/image.jpg',
  company: 'Nike',
  sections: [
    { title: 'about us', url: 'section/about-us', disabled: false },
    { title: 'contact us', url: 'section/contact-us', disabled: false },
    { title: 'our blog', url: 'section/our-blog', disabled: false },
  ],
  currentSection: {
    title: 'test',
    url: '/',
    disabled: false
  },
  epTitle: 'Export plan title'
}

const setup = ({...data}) => {

  const utils = render(<Provider store={Services.store}><Sidebar {...data} /></Provider>)

  return {
    ...utils
  }
}

describe('Sidebar', () => {
  describe('Should be collapsed', () => {
    const { getAllByRole, getByRole } = setup(props)
    const buttons = getAllByRole('button')
    const icon = buttons[0].firstChild

    it('Should have close class', () => {
      expect(getByRole('navigation')).toHaveClass('sidebar__close')
    })

    it('Should have expand icon', () => {
      expect(icon).toHaveClass('fa-angle-double-right')
    })
  })

  it('Should have a title' , () => {
    const { getByText } = setup(props)
    expect(getByText('Export plan title')).toBeInTheDocument()
  })

  describe( 'logo', () => {
    it('Should company logo', () => {
      const { getByAltText } = setup(props)
      const image = getByAltText('Nike')
      expect(image).toBeInTheDocument()
    })

    it('Should display placeholder image', () => {
      const { getByAltText } = setup({...props, logo: '', company: ''})
      const image = getByAltText('Add a business logo')
      expect(image).toBeInTheDocument()
    })
  })

  describe('sections', () => {
    it('Should list sections as links', () => {
      const { getByTitle } = setup(props)
      expect(getByTitle('about us')).toBeInTheDocument()
      expect(getByTitle('contact us')).toBeInTheDocument()
      expect(getByTitle('our blog')).toBeInTheDocument()
    })

    it('Should list sections as buttons', () => {

      const sections = props.sections.map(obj => {
        if(obj.disabled === false)
          return {
            ...obj,
            disabled: true,
          }
        return obj
      });

      const { getByRole } = setup({
        ...props,
        sections
      })
      expect(getByRole('button',{ name: 'about us'})).toBeInTheDocument()
      expect(getByRole('button',{ name: 'contact us'})).toBeInTheDocument()
      expect(getByRole('button',{ name: 'our blog'})).toBeInTheDocument()
    })
  })

  describe('Should be expanded', () => {
    it('Should be not have close class and have expanded icon',  async () => {
      const { getAllByRole, getByRole } = setup(props)
      const buttons = getAllByRole('button')
      const toggleButton = buttons[0]
      const icon = buttons[0].firstChild
      fireEvent.click(toggleButton)

      await waitFor(() => {
        expect(getByRole('navigation')).not.toHaveClass('sidebar__close')
        expect(icon).toHaveClass('fa-angle-double-left')
      })
    })
  })
})

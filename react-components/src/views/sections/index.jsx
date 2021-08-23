import React from 'react'
import ReactDOM from 'react-dom'
import { Provider } from 'react-redux'
import Services from '@src/Services'

import { Sidebar } from '@src/components/Sidebar'
import { SectionComplete } from '@src/components/SectionComplete/SectionComplete'

export const sectionSidebar = ({ element, ...params }) => {
  ReactDOM.render(<Provider store={Services.store}><Sidebar {...params} /></Provider>, element)
}

export const sectionComplete = ({ element, ...params }) => {
  ReactDOM.render(<SectionComplete {...params} />, element)
}

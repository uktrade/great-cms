import React from 'react'
import ReactDOM from 'react-dom'

import { Sidebar } from '@src/components/Sidebar'
import { SectionComplete } from '@src/components/SectionComplete/SectionComplete'

export const sectionSidebar = ({ element, ...params }) => {
  ReactDOM.render(<Sidebar {...params} />, element)
}

export const sectionComplete = ({ element, ...params }) => {
  ReactDOM.render(<SectionComplete {...params} />, element)
}

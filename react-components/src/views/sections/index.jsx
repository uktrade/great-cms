import React from 'react'
import ReactDOM from 'react-dom'

import { Sidebar } from '@src/components/Sidebar'

export const sectionSidebar = ({ element, ...params }) => {
  ReactDOM.render(<Sidebar {...params} />, element)
}

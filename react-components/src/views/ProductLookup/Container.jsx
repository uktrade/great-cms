import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'

import Component from '@src/components/AutoCompleteField'

import Services from '@src/Services'


const formatOptions = options => options.map(item => ({value: item.label, label: item.label}))
const loadOptions = (inputValue, callback) => Services.lookupProduct({q: inputValue}).then(options => callback(formatOptions(options)))


export function Container(props){
  const [products, setProducts] = React.useState([])
  return (      
    <Component
      autoFocus={true}
      loadOptions={loadOptions}
      disabled={false}
      errors={[]}
      handleChange={setProducts}
      name='products'
      value={products}
      placeholder='Start typing and select a product'
      name={props.name}
    />
    )
}

export default function({ element, ...params }) {
  ReactDOM.render(
    <Container {...params} />,
    element
  )
}

Container.propTypes = {
  name: PropTypes.string.isRequired,
}
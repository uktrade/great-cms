import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import Services from '@src/Services'
import { capitalize } from '@src/Helpers'


function ValueItem(props) {
  const { option, valueChange } = props;
  const [value, setValue] = useState(option.value)

  const changeValue = (evt) => {
    const newValue = evt.target.value || 0
    setValue(newValue)
    valueChange(option.id, newValue)
  }

  useEffect(() => {
    valueChange(option.id, value)
  }, [])

  return (
    <label htmlFor={option.id} className='m-b-xxs'>
      <input
        type="number"
        className="form-control"
        id={option.id}
        defaultValue={option.value}
        onChange={changeValue}
        style={{width:'71px'}}
      />
      <span className="text-black-50 m-f-xxs">%</span><span className="m-f-xs">{option.name}</span>
    </label>
  )
}

ValueItem.propTypes = {
  option: PropTypes.shape({
    id: PropTypes.string,
    name: PropTypes.string,
    value: PropTypes.number,
  }).isRequired,
  valueChange: PropTypes.func.isRequired
}


export default function Interaction(props) {
  const buttonEnabled = true

  const { txId, attribute, processResponse, mixedContentError } = props

  const [outputValue, setOutputValue] = useState({})

  const clickNext = () => {
    const values = Object.keys(outputValue).map((id) => {
      return { first: id, second: outputValue[id] }
    })
    processResponse(
      Services.lookupProductRefine({
        txId,
        interactionId: attribute.id,
        values
      })
    )
  }

  const valueChange = (optionId, optionValue) => {
    const newValue = {}
    newValue[optionId] = optionValue
    setOutputValue(Object.assign(outputValue, newValue))
  }

  const options = (attribute.attrs || []).map((attr) => {
    return <ValueItem key={attr.id} option={attr} valueChange={valueChange}/>
  })

  return (
    <div className="interaction grid m-v-xs" key={attribute.id}>
      <div className="c-fullwidth">
        <div className={`form-group p-v-0 ${mixedContentError ? 'form-group-error' : ''}`}>
          <span className="interaction-name h-xs p-t-0">{capitalize(attribute.label)}</span>
          { mixedContentError ? (<span className="error-message p-v-0">Total must equal 100%</span>) : '' }
          <p className="m-v-xxs">Select the best match for your product.</p>
          {options}
        </div>
        <button type="button" className="button button--secondary m-t-xxs" disabled={!buttonEnabled} onClick={clickNext} style={{float:'left',clear:'both'}}>Next</button>
      </div>
    </div>
  )
}

Interaction.propTypes = {
  txId: PropTypes.string.isRequired,
  attribute: PropTypes.shape(
    { id: PropTypes.string, 
      label: PropTypes.string,
      attrs: PropTypes.array,
    }).isRequired,
  processResponse: PropTypes.func.isRequired,
  mixedContentError: PropTypes.bool
}
Interaction.defaultProps = {
  mixedContentError: false
}

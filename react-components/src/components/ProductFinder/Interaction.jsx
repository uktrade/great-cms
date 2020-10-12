import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import Services from '@src/Services'
import { capitalize } from '@src/Helpers'

function RadioButtons(props) {
  const { attribute, valueChange } = props;
  const [selection, setSelection] = useState()

  const updateSelection = (_selection) => {
    setSelection(_selection)
    valueChange(_selection)
  }

  useEffect(() => {
    (attribute.attrs || []).map(({value, name, id}) => {
      if (value === 'true') {
        updateSelection({ name, id })
      }
      return null // for eslint only 
    })
  }, [])

  const changeVal = (evt) => {
    updateSelection({ name: evt.target.getAttribute('data-label'), id: evt.target.value })
  }

  const buttons = (attribute.attrs || []).map((option) => {
    const checked = option.id === (selection && selection.id)
    const optionName = (<span>{(option.isPart ? <span className="text-black-50">Part of </span> : '')}{capitalize(option.name, !option.isPart)}</span>)
    return (
      <label key={option.id} htmlFor={option.id} className="multiple-choice p-f-m m-v-xxs">
        <input
          type="radio"
          className="radio"
          id={option.id}
          name={attribute.id}
          value={option.id}
          data-label={option.name}
          defaultChecked={checked}
          aria-label={option.name}
        />
        {/* eslint-disable jsx-a11y/label-has-associated-control */}
        <label htmlFor={option.id}/>
        {/* eslint-enable jsx-a11y/label-has-associated-control */}
        {optionName}
      </label>
    )
  })
  return <div className="m-b-xs" onChange={changeVal}>{buttons}</div>
}

RadioButtons.propTypes = {
  attribute: PropTypes.shape({
    id: PropTypes.string,
    attrs: PropTypes.array
  }).isRequired,
  valueChange: PropTypes.func.isRequired
}



export default function Interaction(props) {
  const { txId, attribute, isItemChoice, processResponse } = props

  const [value, setValue] = useState()

  const clickNext = () => {
    if (isItemChoice) {
      processResponse(Services.lookupProduct({ q: value.name }))
    } else {
      processResponse(
        Services.lookupProductRefine({
          txId,
          interactionId: attribute.id,
          values:[{first: value.id, second: value.name}]
        })
      )
    }
  }

  const valueChange = (newValue) => {
    setValue(newValue)
  }

  return (
    <div className="interaction grid m-v-xs" key={attribute.id}>
        <div className="c-fullwidth">
          <span className="interaction-name h-s p-t-0">{capitalize(attribute.label)}</span>
          <p className="m-v-xs">Select the best match for your product.</p>
          <RadioButtons attribute={attribute} valueChange={valueChange}/>
          <button type="button" className="button button--secondary m-t-xxs" disabled={!value || !Object.keys(value).length} onClick={clickNext} style={{float:'left',clear:'both'}}>Next</button>
        </div>
    </div>
  )
}

Interaction.propTypes = {
  txId: PropTypes.string.isRequired,
  attribute: PropTypes.shape({ id: PropTypes.string, label: PropTypes.string }).isRequired,
  isItemChoice: PropTypes.bool,
  processResponse: PropTypes.func.isRequired
}

Interaction.defaultProps = {
  isItemChoice: false,
}

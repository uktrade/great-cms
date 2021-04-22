import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import ReactHtmlParser from 'react-html-parser'

export default function RadioButtons(props) {
  const { name, choices, initialSelection, valueChange } = props
  const [selection, setSelection] = useState()

  const updateSelection = (_selection) => {
    setSelection(_selection.value)
    valueChange(_selection.value)
  }

  useEffect(() => {
    setSelection(initialSelection)
  }, [name])

  const changeVal = (evt) => {
    updateSelection({ value: evt.target.value })
  }
  const buttons = choices.map(({ label, value }, idx) => {
    const checked = value === selection

    return (
      <div key={`option-${value}`} className="multiple-choice p-f-s p-b-xs">
        <input
          id={idx}
          type="radio"
          className="radio"
          name={name}
          value={value}
          checked={checked}
          onChange={changeVal}
          onClick={changeVal}
        />
        <label htmlFor={idx} className="body-l">
          {ReactHtmlParser(label)}
        </label>
      </div>
    )
  })

  return <div className="m-b-xs radio-block">{buttons}</div>
}

RadioButtons.propTypes = {
  name: PropTypes.string.isRequired,
  initialSelection: PropTypes.shape({
    label: PropTypes.string,
    value: PropTypes.string,
  }),
  choices: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string,
      value: PropTypes.string,
    })
  ).isRequired,
  valueChange: PropTypes.func.isRequired,
}

RadioButtons.defaultProps = {
  initialSelection: null,
}

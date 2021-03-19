import React, { useState } from 'react'
import PropTypes from 'prop-types'

function RadioButtons(props) {
  const { name, choices, valueChange } = props
  const [selection, setSelection] = useState()

  const updateSelection = (_selection) => {
    setSelection(_selection)
    valueChange(_selection)
  }

  const changeVal = (evt) => {
    updateSelection({ value: evt.target.value })
  }

  const buttons = choices.map(({label, value}, idx) => {
    const checked = value === (selection && selection.value)

    return (
      <div key={idx} className="multiple-choice p-f-s p-b-xs">
        <input
          id={idx}
          type="radio"
          className="radio"
          name={name}
          value={value}
          checked={checked}
          onChange={changeVal}
        />
        <label htmlFor={idx} className="body-l">
          {label}
        </label>
      </div>
    )
  })

  return <div className="m-b-xs">{buttons}</div>
}

RadioButtons.propTypes = {
  choices: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string.isRequired,
      value: PropTypes.string.isRequired,
    })
  ).isRequired,
  valueChange: PropTypes.func.isRequired,
}

export default function Interaction(props) {
  const { question, answers, processResponse } = props

  const [value, setValue] = useState()

  const clickSave = () => {
    processResponse(value)
  }

  const valueChange = (newValue) => {
    setValue(newValue)
  }

  return (
    <form className="text-blue-deep-80">
      <div className="c-fullwidth">
        <h3 className="h-s">{question.title}</h3>
        {question.content && (
          <p className="body-m m-b-xs text-blue-deep-60">
            {question.content}
          </p>
        )}
        <RadioButtons
          name={question.name}
          choices={answers}
          valueChange={valueChange}
        />
        <button
          type="button"
          className="button button--primary m-t-xxs m-b-xs"
          disabled={!value || !Object.keys(value).length}
          onClick={clickSave}
          style={{ float: 'left', clear: 'both' }}
        >
          Save
          </button>
      </div>
    </form>
  )
}

Interaction.propTypes = {
  question: PropTypes.shape({
    name: PropTypes.string.isRequired,
    title: PropTypes.string.isRequired,
    content: PropTypes.string
  }).isRequired,
  answers: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string.isRequired,
      value: PropTypes.string.isRequired,
    }),
  ).isRequired,
  processResponse: PropTypes.func.isRequired,
}

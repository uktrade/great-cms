import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import ReactHtmlParser from 'react-html-parser'
import { Select } from '@src/components/Form/Select'

function RadioButtons(props) {
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
          {ReactHtmlParser(label)}
        </label>
      </div>
    )
  })

  return <div className="m-b-xs" style={{overflow:'hidden'}}>{buttons}</div>
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
  const { question, value, setValue } = props

  const valueChange = (newValue) => {
    setValue(newValue)
  }

  const selectValueChange = (value) => {
    valueChange(Object.values(value)[0])
  }

  const choices = question.choices.options || question.choices
  const selectedChoice = choices.find((option) => option.value == value)

  return (
    <form className="text-blue-deep-80">
      <div className="c-fullwidth">
        {question.content && (
          <p className="body-m m-b-xs text-blue-deep-60">{question.content}</p>
        )}
        {question.type == 'RADIO' ? (
          <RadioButtons
            name={question.name}
            choices={choices}
            initialSelection={value}
            valueChange={valueChange}
          />
        ) : (
          ''
        )}
        {question.type in {'SLCT':1,'SELECT':1} ? (
          <Select
            label=""
            id={`question-${question.id}`}
            update={selectValueChange}
            name={question.name}
            options={choices}
            hideLabel
            placeholder={question.choices.placeholder || 'Please choose'}
            selected={[(selectedChoice && selectedChoice.label) || '']}
          />
        ) : (
          ''
        )}
      </div>
    </form>
  )
}

Interaction.propTypes = {
  question: PropTypes.shape({
    name: PropTypes.string.isRequired,
    title: PropTypes.string.isRequired,
    content: PropTypes.string,
  }).isRequired
}

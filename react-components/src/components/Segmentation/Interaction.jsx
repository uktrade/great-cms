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
  const { question, initialSelection, processResponse, goBack } = props

  const [value, setValue] = useState()

  const clickSave = () => {
    processResponse(value)
  }

  const clickBack = () => {
    goBack()
  }

  useEffect(() => {
    setValue(initialSelection)
  }, [question])

  const valueChange = (newValue) => {
    setValue(newValue)
  }

  const selectValueChange = (value) => {
    valueChange(Object.values(value)[0])
  }

  return (
    <form className="text-blue-deep-80">
      <div className="c-fullwidth">
        <h3 className="h-s">{question.title}</h3>
        {question.content && (
          <p className="body-m m-b-xs text-blue-deep-60">{question.content}</p>
        )}
        {question.type == 'RADIO' ? (
          <RadioButtons
            name={question.name}
            choices={question.choices.options || question.choices}
            initialSelection={initialSelection}
            valueChange={valueChange}
          />
        ) : (
          ''
        )}
        {question.type == 'SLCT' ? (
          <Select
            label={question.title}
            id={`question-${question.id}`}
            update={selectValueChange}
            name={question.name}
            options={question.choices.options || question.choices}
            hideLabel
            placeholder={question.choices.placeholder || 'Please choose'}
            selected={initialSelection}
          />
        ) : (
          ''
        )}
        {goBack ? (
          <button
            type="button"
            className="button button--tertiary m-t-xxs m-b-xs"
            onClick={goBack}
            style={{ float: 'left', clear: 'both' }}
          >
            Back
          </button>
        ) : (
          ''
        )}
        <button
          type="button"
          className="button button--primary m-t-xxs m-b-xs"
          disabled={!value}
          onClick={clickSave}
          style={{ float: 'right' }}
        >
          Next
        </button>
      </div>
    </form>
  )
}

Interaction.propTypes = {
  question: PropTypes.shape({
    name: PropTypes.string.isRequired,
    title: PropTypes.string.isRequired,
    content: PropTypes.string,
  }).isRequired,
  answers: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string.isRequired,
      value: PropTypes.string.isRequired,
    })
  ).isRequired,
  processResponse: PropTypes.func.isRequired,
}

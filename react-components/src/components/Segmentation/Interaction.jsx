import React from 'react'
import PropTypes from 'prop-types'
import { isArray } from '@src/Helpers'
import { Select } from '@src/components/Form/Select'
import RadioButtons from './RadioButtons'

export default function Interaction(props) {
  const { question, value, setValue } = props

  const valueChange = (newValue) => {
    setValue(newValue)
  }

  const selectValueChange = (newValue) => {
    valueChange(Object.values(newValue)[0])
  }

  const choices = isArray(question.choices)
    ? question.choices
    : question.choices.options || []

  return (
    <form className="text-blue-deep-80">
      <div className="c-fullwidth">
        {question.type === 'RADIO' ? (
          <RadioButtons
            name={question.name}
            choices={choices}
            initialSelection={value}
            valueChange={valueChange}
          />
        ) : (
          ''
        )}
        {question.type in
        { SELECT: 1, MULTI_SELECT: 1 } ? (
          <Select
            label=""
            id={`question-${question.id}`}
            update={selectValueChange}
            name={question.name}
            options={choices}
            hideLabel
            multiSelect={question.type === 'MULTI_SELECT'}
            placeholder={question.choices.placeholder || 'Please choose'}
            selected={value}
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
    type: PropTypes.string.isRequired,
    id: PropTypes.number.isRequired,
    title: PropTypes.string.isRequired,
    choices: PropTypes.oneOfType([
      PropTypes.shape({
        options: PropTypes.arrayOf(
          PropTypes.shape({
            value: PropTypes.string,
          })
        ),
        placeHolder: PropTypes.string,
      }),
      PropTypes.arrayOf(
        PropTypes.shape({
          value: PropTypes.string,
        })
      ),
    ]),
  }).isRequired,
  value: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.array
    ]),
  setValue: PropTypes.func.isRequired,
}
Interaction.defaultProps = {
  value: null,
}

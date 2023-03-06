import React from 'react'
import PropTypes from 'prop-types'
import { isArray } from '@src/Helpers'
import { Select } from '@src/components/Form/Select'
import RadioButtons from '../RadioButtons'

export default function Interaction(props) {
  const { question, setValue } = props

  const choices = isArray(question.choices)
    ? question.choices
    : question.choices.options || []

  return (
    <form>
      <fieldset className="c-fullwidth">
        <legend className="visually-hidden">{question.title}</legend>
        {question.type.toLowerCase() === 'radio' ? (
          <RadioButtons
            name={question.name}
            choices={choices}
            initialSelection={question.answer}
            valueChange={setValue}
          />
        ) : (
          ''
        )}
        {question.type.toLowerCase() in { select: 1, multi_select: 1 } ? (
          <Select
            label=""
            id={`question-${question.id}`}
            update={(newValue) => setValue(Object.values(newValue)[0])}
            name={question.name}
            options={choices}
            hideLabel
            multiSelect={question.type === 'MULTI_SELECT'}
            placeholder={question.choices.placeholder || 'Please choose'}
            selected={question.answer}
          />
        ) : (
          ''
        )}
      </fieldset>
    </form>
  )
}

Interaction.propTypes = {
  question: PropTypes.shape({
    name: PropTypes.string.isRequired,
    type: PropTypes.string.isRequired,
    id: PropTypes.number.isRequired,
    title: PropTypes.string.isRequired,
    answer: (props, propName, componentName) => {
      const { propName: data } = props
      return (
        data === null ||
        data === undefined ||
        Array.isArray(data) ||
        typeof data === 'string'
      ) ? null : new Error(`${componentName}: ${propName} type ${typeof data} is not allowed`)
    },
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
  setValue: PropTypes.func.isRequired,
}

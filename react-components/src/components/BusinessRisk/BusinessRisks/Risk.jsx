import React, { memo } from 'react'
// import PropTypes from 'prop-types'

import { TextArea } from '@src/components/Form/TextArea'
import { Learning } from '@src/components/Learning/Learning'
import { Radiogroup } from '@src/components/Form/Radiogroup/Radiogroup'
// import { Select } from '@src/components/Form/Select'

export const Risk = ({
  id,
  onChange,
  deleteRisk,
  notes,
  contingency_notes,
  index,
  likelihoodOptions,
  impactOptions,
  selected,
}) => {
  // debugger
  return (
    <>
      <tr>
        <td>
          <p className="form-label m-v-0">Risk {index}</p>
          <Learning {...notes} />
          <TextArea
            id={id}
            type="textarea"
            hideLabel
            label={notes.label}
            value={notes.value}
            onChange={(e) => onChange('input', id, e)}
            formGroupClassName="m-b-0"
          />
        </td>
      </tr>
      <tr>
        <Radiogroup
          options={likelihoodOptions}
          selected={selected.risk_likelihood_option}
          groupName={Object.keys(selected.risk_likelihood_option)}
          label="Risk likelihood"
        />
      </tr>
      <tr>
        <Radiogroup
          options={impactOptions}
          selected={selected.risk_impact_option}
          groupName={Object.keys(selected.risk_impact_option)}
          label="Risk impact"
        />
      </tr>
      <tr>
        <td>
          <p className="form-label m-v-0">{contingency_notes.label}</p>
          <Learning {...contingency_notes} />
          <TextArea
            id={id}
            type="textarea"
            hideLabel
            label={contingency_notes.label}
            hideLabel
            value={contingency_notes.value}
            onChange={(e) => onChange('input', id, e)}
            formGroupClassName="m-b-0"
          />
        </td>
      </tr>
      <tr>
        <td className="text-center" colSpan="2">
          <button
            type="button"
            title="Click to delete this funding option and its data."
            className="button button--delete button--small button--only-icon button--tertiary"
            onClick={() => deleteRisk(id)}
          >
            <i className="fas fa-trash-alt"></i>
          </button>
        </td>
      </tr>
    </>
  )
}

// Risk.propTypes = {
//   id: PropTypes.number.isRequired,
//   value: PropTypes.number.isRequired,
//   currency: PropTypes.string.isRequired,
//   selectData: PropTypes.shape({
//     id: PropTypes.string.isRequired,
//     name: PropTypes.string.isRequired,
//     options: PropTypes.array.isRequired,
//     placeholder: PropTypes.string.isRequired,
//   }).isRequired,
//   onChange: PropTypes.func.isRequired,
//   deleteRisk: PropTypes.func.isRequired,
// }

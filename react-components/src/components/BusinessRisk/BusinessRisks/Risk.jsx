import React, { memo } from 'react'
// import PropTypes from 'prop-types'

import { TextArea } from '@src/components/Form/TextArea'
import { Learning } from '@src/components/Learning/Learning'
import { Radiogroup } from '@src/components/Form/Radiogroup/Radiogroup'

export const Risk = ({
  id,
  onChange,
  deleteRisk,
  risk,
  risk_extras,
  contingency_plan,
  contingency_plan_extras,
  index,
  likelihoodOptions,
  impactOptions,
  selected,
}) => {
  return (
    <>
      <tr>
        <td>
          <p className="form-label m-v-0">Risk {index}</p>
          <Learning {...risk_extras} />
          <TextArea
            id={id}
            type="textarea"
            hideLabel
            label={risk_extras.label}
            value={risk}
            onChange={(e) =>
              onChange('input', id, { field: 'risk', value: e[id] })
            }
            formGroupClassName="m-b-0"
          />
        </td>
      </tr>
      <tr>
        <Radiogroup
          id={id}
          options={likelihoodOptions}
          selected={selected.risk_likelihood}
          groupName={Object.keys(selected)[0]}
          label="Risk likelihood"
          update={(e) => onChange('radio', id, e)}
        />
      </tr>
      <tr>
        <Radiogroup
          id={id}
          options={impactOptions}
          selected={selected.risk_impact}
          groupName={Object.keys(selected)[1]}
          label="Risk impact"
          update={(e) => onChange('radio', id, e)}
        />
      </tr>
      <tr>
        <td>
          <p className="form-label m-v-0">{contingency_plan_extras.label}</p>
          <Learning {...contingency_plan_extras} />
          <TextArea
            id={id}
            type="textarea"
            hideLabel
            label={contingency_plan_extras.label}
            hideLabel
            value={contingency_plan}
            onChange={(e) =>
              onChange('input', id, {
                field: 'contingency_plan',
                value: e[id],
              })
            }
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

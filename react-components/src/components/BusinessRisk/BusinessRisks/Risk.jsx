import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { TextArea } from '@src/components/Form/TextArea'
import { Learning } from '@src/components/Learning/Learning'
import { Radiogroup } from '@src/components/Form/Radiogroup/Radiogroup'

export const Risk = memo(
  ({
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
              id={String(id)}
              type="textarea"
              hideLabel
              label={`Risk ${index} label`}
              value={risk}
              onChange={(e) => onChange(id, { key: 'risk', value: e[id] })}
              formGroupClassName="m-b-0"
            />
          </td>
        </tr>
        <tr>
          <td>
            <Radiogroup
              id={id}
              options={likelihoodOptions}
              selected={selected.risk_likelihood}
              groupName={Object.keys(selected)[0]}
              label="Risk likelihood"
              update={(e) => onChange(id, e)}
            />
          </td>
        </tr>
        <tr>
          <td>
            <Radiogroup
              id={id}
              options={impactOptions}
              selected={selected.risk_impact}
              groupName={Object.keys(selected)[1]}
              label="Risk impact"
              update={(e) => onChange(id, e)}
            />
          </td>
        </tr>
        <tr>
          <td>
            <p className="form-label m-v-0">{contingency_plan_extras.label}</p>
            <Learning {...contingency_plan_extras} />
            <TextArea
              id={String(id)}
              type="textarea"
              hideLabel
              label={contingency_plan_extras.label}
              hideLabel
              value={contingency_plan}
              onChange={(e) =>
                onChange(id, {
                  key: 'contingency_plan',
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
)

Risk.propTypes = {
  id: PropTypes.number.isRequired,
  risk: PropTypes.string.isRequired,
  contingency_plan: PropTypes.string.isRequired,
  risk_extras: PropTypes.shape({
    example: PropTypes.shape({
      content: PropTypes.string,
    }),
    tooltip: PropTypes.shape({
      content: PropTypes.string,
    }),
  }).isRequired,
  contingency_plan_extras: PropTypes.shape({
    example: PropTypes.shape({
      content: PropTypes.string,
    }),
    label: PropTypes.string,
    tooltip: PropTypes.shape({
      content: PropTypes.string,
    }),
  }).isRequired,
  index: PropTypes.number.isRequired,
  likelihoodOptions: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string,
      value: PropTypes.string,
    })
  ).isRequired,
  impactOptions: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string,
      value: PropTypes.string,
    })
  ).isRequired,
  selected: PropTypes.shape({
    risk_impact: PropTypes.string,
    risk_likelihood: PropTypes.string,
  }).isRequired,
  onChange: PropTypes.func.isRequired,
  deleteRisk: PropTypes.func.isRequired,
}

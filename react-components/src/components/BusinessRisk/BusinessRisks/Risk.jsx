import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { TextArea } from '@src/components/Form/TextArea'
import { Learning } from '@src/components/Learning/Learning'
import { Radiogroup } from '@src/components/Form/Radiogroup/Radiogroup'
import { ConfirmModal } from '@src/components/ConfirmModal/ConfirmModal'

export const Risk = memo(
  ({
    id,
    onChange,
    deleteRisk,
    risk,
    risk_extras,
    likelihood_extras,
    impact_extras,
    contingency_plan,
    contingency_plan_extras,
    index,
    likelihoodOptions,
    impactOptions,
    selected,
  }) => {
    return (
      <div className="costs__option costs__option--border">
        <div className="costs__border">
          <h3 className="h-s p-t-0">Risk {index}</h3>
          <Learning {...risk_extras} />
          <TextArea
            id={String(id)}
            type="textarea"
            hideLabel
            label={`Risk ${index} label`}
            value={risk}
            placeholder={risk_extras.placeholder}
            onChange={(e) => onChange(id, { key: 'risk', value: e[id] })}
            formGroupClassName="m-b-0"
          />
        </div>
        <div className="costs__border">
          <Radiogroup
            id={id}
            options={likelihoodOptions}
            selected={selected.risk_likelihood}
            groupName={Object.keys(selected)[0]}
            label="Risk likelihood"
            update={(e) => onChange(id, e)}
          >
            <Learning {...likelihood_extras} />
          </Radiogroup>
        </div>
        <div className="costs__border">
          <Radiogroup
            id={id}
            options={impactOptions}
            selected={selected.risk_impact}
            groupName={Object.keys(selected)[1]}
            label="Risk impact"
            update={(e) => onChange(id, e)}
          >
            <Learning {...impact_extras} />
          </Radiogroup>
        </div>
        <div className="costs__border">
          <p className="form-label m-v-0">{contingency_plan_extras.label}</p>
          <Learning {...contingency_plan_extras} />
          <TextArea
            id={String(id)}
            type="textarea"
            hideLabel
            label={contingency_plan_extras.label}
            value={contingency_plan}
            placeholder={contingency_plan_extras.placeholder}
            onChange={(e) =>
              onChange(id, {
                key: 'contingency_plan',
                value: e[id],
              })
            }
            formGroupClassName="m-b-0"
          />
        </div>
        <div className="text-center">
          <ConfirmModal
            hasData={
              !!contingency_plan ||
              !!selected.risk_impact ||
              !!selected.risk_likelihood ||
              !!risk
            }
            deleteItem={() => deleteRisk(id)}
          />
        </div>
      </div>
    )
  }
)

Risk.propTypes = {
  id: PropTypes.number.isRequired,
  risk: PropTypes.string.isRequired,
  contingency_plan: PropTypes.string.isRequired,
  risk_extras: PropTypes.shape({
    placeholder: PropTypes.string,
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
    placeholder: PropTypes.string,
    tooltip: PropTypes.shape({
      content: PropTypes.string,
    }),
  }).isRequired,
  likelihood_extras: PropTypes.shape({
    tooltip: PropTypes.shape({
      content: PropTypes.string,
    }),
  }).isRequired,
  impact_extras: PropTypes.shape({
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

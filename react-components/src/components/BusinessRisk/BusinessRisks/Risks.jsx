import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { Risk } from './Risk'
import { AddButton } from '@src/components/ObjectivesList/AddButton/AddButton'

export const Risks = memo(
  ({
    formData,
    onChange,
    deleteRisk,
    addRisk,
    likelihoodOptions,
    impactOptions,
  }) => {
    return (
      <>
        {formData.length !== 0 && (
          <div className="costs bg-blue-deep-10 m-b-s">
            {formData
              .sort((r1, r2) => (r1.pk < r2.pk ? -1 : 1))
              .map(
                (
                  {
                    pk,
                    risk,
                    risk_extras,
                    likelihood_extras,
                    impact_extras,
                    contingency_plan,
                    contingency_plan_extras,
                    risk_likelihood,
                    risk_impact,
                  },
                  i
                ) => (
                  <Risk
                    index={i + 1}
                    key={pk}
                    id={pk}
                    risk={risk}
                    risk_extras={risk_extras}
                    likelihood_extras={likelihood_extras}
                    impact_extras={impact_extras}
                    contingency_plan={contingency_plan}
                    contingency_plan_extras={contingency_plan_extras}
                    onChange={onChange}
                    deleteRisk={deleteRisk}
                    likelihoodOptions={likelihoodOptions}
                    impactOptions={impactOptions}
                    selected={{ risk_likelihood, risk_impact }}
                  />
                )
              )}
          </div>
        )}
        <AddButton type="button" add={addRisk} cta="Add a risk" />
      </>
    )
  }
)

Risks.propTypes = {
  formData: PropTypes.arrayOf(
    PropTypes.shape({
      companyexportplan: PropTypes.number,
      contingency_plan: PropTypes.string,
      pk: PropTypes.number,
      risk: PropTypes.string,
      risk_impact: PropTypes.string,
      risk_likelihood: PropTypes.string,
      contingency_plan_extras: PropTypes.shape({
        example: PropTypes.shape({
          content: PropTypes.string,
        }),
        label: PropTypes.string,
        tooltip: PropTypes.shape({
          content: PropTypes.string,
        }),
      }),
      risk_extras: PropTypes.shape({
        example: PropTypes.shape({
          content: PropTypes.string,
        }),
        tooltip: PropTypes.shape({
          content: PropTypes.string,
        }),
      }),
      likelihood_extras: PropTypes.shape({
        tooltip: PropTypes.shape({
          content: PropTypes.string,
        }),
      }),
      impact_extras: PropTypes.shape({
        tooltip: PropTypes.shape({
          content: PropTypes.string,
        }),
      }),
    })
  ).isRequired,
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
  onChange: PropTypes.func.isRequired,
  deleteRisk: PropTypes.func.isRequired,
  addRisk: PropTypes.func.isRequired,
}

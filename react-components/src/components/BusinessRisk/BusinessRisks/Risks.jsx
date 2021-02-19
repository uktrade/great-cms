import React, { memo } from 'react'
// import PropTypes from 'prop-types'

import { Risk } from './Risk'

export const Risks = ({
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
        <div className="costs costs--risks bg-blue-deep-10 p-v-s m-b-s">
          <table className="m-v-0">
            <tbody>
              {formData.map(
                (
                  {
                    pk,
                    risk,
                    risk_extras,
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
            </tbody>
          </table>
        </div>
      )}
      <button
        type="button"
        className="button button--large button--icon"
        onClick={addRisk}
      >
        <i className="fas fa-plus-circle"></i>Add a risk
      </button>
    </>
  )
}

// Risks.propTypes = {
//   formData: PropTypes.arrayOf(
//     PropTypes.shape({
//       pk: PropTypes.number,
//     })
//   ).isRequired,
//   onChange: PropTypes.func.isRequired,
//   deleteRisk: PropTypes.func.isRequired,
//   addRisk: PropTypes.func.isRequired,
// }

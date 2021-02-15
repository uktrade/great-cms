import React, { memo, useState } from 'react'
// import PropTypes from 'prop-types'
import Services from '@src/Services'
import { useDebounce } from '@src/components/hooks/useDebounce'
import { Learning } from '@src/components/Learning/Learning'
// import { Radiogroup } from '@src/components/Form/Radiogroup/Radiogroup'
import { Risks } from './Risks'
// import { risk_likelihood_options, risk_impact_options } from './constants'

export const BusinessRisks = ({
  formData,
  companyexportplan,
  lesson,
  risk_likelihood_options,
  risk_impact_options,
}) => {
  const [risks, setRisks] = useState(formData)
  // debugger
  const addRisk = () => {
    const newRisk = {}
    newRisk.companyexportplan = companyexportplan
    newRisk.value = ''

    Services.createFundingCreditOption({ ...newRisk })
      .then((data) => setRisks([...risks, data]))
      .catch(() => {})
  }

  const deleteRisk = (id) => {
    Services.deleteFundingCreditOption(id)
      .then(() => {
        setRisks(risks.filter((x) => x.pk !== id))
      })
      .catch(() => {})
  }

  const update = (field, value) => {
    Services.updateFundingCreditOption({ ...field, ...value })
      .then(() => {})
      .catch(() => {})
  }

  const debounceUpdate = useDebounce(update)

  const onChange = (id, value) => {
    value = { value: value }
    const field = risks.find((x) => x.pk === id)
    field.companyexportplan = companyexportplan
    const updatedRisks = risks.map((x) =>
      x.pk === id ? { ...x, ...value } : x
    )
    setRisks(updatedRisks)
    debounceUpdate(field, value)
  }

  // const options_risk_likelihood = {
  //   label: 'Risk likelihood',
  //   field: 'options_risk_likelihood',
  //   selected: 'possible',
  //   options: risk_likelihood_options,
  // }
  // const options_risk_impact = {
  //   label: 'Risk impact',
  //   field: 'options_risk_impact',
  //   selected: 'minor',
  //   options: risk_impact_options,
  // }

  return (
    <>
      <h2 className="h-m m-b-xs">Risks</h2>
      <p>
        Record any risks you think your business may face in the following
        table.
      </p>
      <p>These should be specific risks your business faces when exporting.</p>
      <Learning lesson={lesson} />
      <Risks
        formData={risks}
        deleteRisk={deleteRisk}
        onChange={onChange}
        addRisk={addRisk}
        likelihoodOptions={risk_likelihood_options}
        impactOptions={risk_impact_options}
      />
    </>
  )
}

// BusinessRisks.propTypes = {
//   formData: PropTypes.arrayOf(
//     PropTypes.shape({
//       companyexportplan: PropTypes.number,
//       pk: PropTypes.number,
//     })
//   ).isRequired,
//   companyexportplan: PropTypes.number.isRequired,
// }

// BusinessRisks.defaultProps = {
//   formData: [],
// }

import React, { memo, useState } from 'react'
// import PropTypes from 'prop-types'
import Services from '@src/Services'
import { useDebounce } from '@src/components/hooks/useDebounce'
import { Learning } from '@src/components/Learning/Learning'
// import { Radiogroup } from '@src/components/Form/Radiogroup/Radiogroup'
import { Risks } from './Risks'
// import { risk_likelihood_options, risk_impact_options } from './constants'

export const BusinessRisks = ({
  formFields,
  formData,
  companyexportplan,
  lesson,
  risk_likelihood_options,
  risk_impact_options,
  model_name,
}) => {
  const [risks, setRisks] = useState(formFields)
  const addRisk = () => {
    const newRisk = {
      companyexportplan,
      model_name,
    }

    Services.apiModelObjectManage({ ...newRisk }, 'POST')
      .then((data) => setRisks([...risks, data]))
      .catch(() => {})
  }

  const deleteRisk = (id) => {
    Services.apiModelObjectManage({ model_name, pk: id }, 'DELETE')
      .then(() => {
        setRisks(risks.filter((x) => x.pk !== id))
      })
      .catch(() => {})
  }

  const update = (field, value) => {
    Services.apiModelObjectManage({ model_name, ...field, ...value }, 'PATCH')
      .then(() => {})
      .catch(() => {})
  }

  const debounceUpdate = useDebounce(update)

  const onChange = (type, id, value) => {
    const field = risks.find((x) => x.pk === id)

    if (type === 'radio') {
      value = {
        [value.key]: value.value,
      }
    }
    if (type === 'input') {
      value = {
        [value.field]: value.value,
      }
    }
    const updatedRisks = risks.map((x) =>
      x.pk === id ? { ...x, ...value } : x
    )

    setRisks(updatedRisks)
    debounceUpdate(field, value)
  }

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
        formData={risks.map((item) => ({ ...item, ...formData }))}
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

import React, { memo, useState } from 'react'
// import PropTypes from 'prop-types'
import Services from '@src/Services'
import { useDebounce } from '@src/components/hooks/useDebounce'
import { Learning } from '@src/components/Learning/Learning'

export const Risks = ({ formData, companyexportplan, lesson }) => {
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
  return (
    <>
      <h2 className="h-m m-b-xs">Risks</h2>
      <p>
        Record any risks you think your business may face in the following
        table.
      </p>
      <p>These should be specific risks your business faces when exporting.</p>
      <Learning lesson={lesson} />
      {/* <Risks
        formData={risks}
        deleteRisk={deleteRisk}
        onChange={onChange}
        addRisk={addRisk}
      /> */}
    </>
  )
}

// Risks.propTypes = {
//   formData: PropTypes.arrayOf(
//     PropTypes.shape({
//       companyexportplan: PropTypes.number,
//       pk: PropTypes.number,
//     })
//   ).isRequired,
//   companyexportplan: PropTypes.number.isRequired,
// }

// Risks.defaultProps = {
//   formData: [],
// }

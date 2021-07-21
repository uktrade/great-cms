import React, { memo, useState } from 'react'
import PropTypes from 'prop-types'
import Services from '@src/Services'
import { useDebounce } from '@src/components/hooks/useDebounce'
import { Learning } from '@src/components/Learning/Learning'
import { useUpdate } from '@src/components/hooks/useUpdate/useUpdate'
import ErrorList from '@src/components/ErrorList'
import { Risks } from './Risks'

export const BusinessRisks = memo(
  ({
    formFields,
    formData,
    companyexportplan,
    lesson,
    risk_likelihood_options,
    risk_impact_options,
    model_name,
  }) => {
    const [risks, setRisks] = useState(formFields)
    const [update, create, deleteItem, message, errors] = useUpdate(
      'business-risk'
    )

    const addRisk = () => {
      const newRisk = {
        companyexportplan,
        model_name,
      }

      create({ ...newRisk }).then((data) => setRisks([...risks, data]))
    }

    const deleteRisk = (id) => {
      deleteItem({ model_name, pk: id }).then(() => {
        setRisks(risks.filter((x) => x.pk !== id))
      })
    }

    const request = (field, value) => update({ model_name, ...field, ...value })

    const debounceUpdate = useDebounce(request)

    const onChange = (id, { key, value }) => {
      const field = risks.find((x) => x.pk === id)
      const data = { [key]: value }

      const updatedRisks = risks.map((x) =>
        x.pk === id ? { ...x, ...data } : x
      )

      setRisks(updatedRisks)
      debounceUpdate(field, data)
    }

    return (
      <>
        <h2 className="h-m m-b-xs">Risks</h2>
        <p>
          Record any risks you think your business might face in the table below.
        </p>
        <Learning lesson={lesson} />
        <Risks
          formData={risks.map((item) => ({ ...item, ...formData }))}
          deleteRisk={deleteRisk}
          onChange={onChange}
          addRisk={addRisk}
          likelihoodOptions={risk_likelihood_options}
          impactOptions={risk_impact_options}
        />
        <ErrorList errors={errors.__all__ || []} className="m-t-s" />
      </>
    )
  }
)

BusinessRisks.propTypes = {
  formData: PropTypes.shape({
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
  }).isRequired,
  formFields: PropTypes.arrayOf(
    PropTypes.shape({
      companyexportplan: PropTypes.number,
      contingency_plan: PropTypes.string,
      pk: PropTypes.number,
      risk: PropTypes.string,
      risk_impact: PropTypes.string,
      risk_likelihood: PropTypes.string,
    })
  ),
  companyexportplan: PropTypes.number.isRequired,
  lesson: PropTypes.shape({
    category: PropTypes.string,
    duration: PropTypes.string,
    title: PropTypes.string,
    url: PropTypes.string,
  }),
  risk_likelihood_options: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string,
      value: PropTypes.string,
    })
  ).isRequired,
  risk_impact_options: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string,
      value: PropTypes.string,
    })
  ).isRequired,
  model_name: PropTypes.string.isRequired,
}

BusinessRisks.defaultProps = {
  formFields: [],
  lesson: {},
}

import React, { memo, useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { useDebounce } from '@src/components/hooks/useDebounce'
import { Learning } from '@src/components/Learning/Learning'
import { formatLessonLearned } from '@src/Helpers'
import { useUpdate } from '@src/components/hooks/useUpdate/useUpdate'
import ErrorList from '@src/components/ErrorList'
import { Total } from '../../CostsAndPricing/Costs/Total'
import { Options } from './Options'

export const FundingCreditOptions = memo(
  ({
    formData,
    currency,
    companyexportplan,
    fundingCreditOptions,
    lessonDetails,
    currentSection,
    model_name,
  }) => {
    const [funding, setFunding] = useState(formData)
    const [fundingTotal, setFundingTotal] = useState(null)
    const lesson = formatLessonLearned(lessonDetails, currentSection, 1)
    const [update, create, deleteItem, message, errors] = useUpdate(
      'travel-plan'
    )

    const calclatedTotal = () =>
      Math.round(funding.reduce((acc, curr) => acc + Number(curr.amount), 0))

    useEffect(() => {
      setFundingTotal(calclatedTotal)
      return () => {}
    }, [funding])

    const addFunding = () => {
      const newFunding = {}
      newFunding.companyexportplan = companyexportplan

      create({ ...newFunding, model_name })
        .then((data) => setFunding([...funding, data]))
        .then(() => {
          const newElement = document.getElementById(
            `Funding ${funding.length + 1}`
          ).parentNode
          newElement.scrollIntoView()
        })
    }

    const deleteFunding = (id) => {
      deleteItem({ model_name, pk: id }).then(() => {
        setFunding(funding.filter((x) => x.pk !== id))
      })
    }

    const request = (field, selected) =>
      update({ ...field, ...selected, model_name })

    const debounceUpdate = useDebounce(request)

    const onChange = (type, id, selected) => {
      if (type === 'input') {
        selected = { amount: selected[id] }
      }
      const field = funding.find((x) => x.pk === id)
      field.companyexportplan = companyexportplan
      const updatedFunding = funding.map((x) =>
        x.pk === id ? { ...x, ...selected } : x
      )
      setFunding(updatedFunding)
      debounceUpdate(field, selected)
    }
    return (
      <>
        <Learning lesson={lesson} />
        <Options
          formData={funding}
          currency={currency}
          selectData={fundingCreditOptions}
          deleteFunding={deleteFunding}
          onChange={onChange}
          addFunding={addFunding}
        />
        <Total label="Total funding" currency={currency} total={fundingTotal} />
        <ErrorList errors={errors.__all__ || []} className="m-0" />
      </>
    )
  }
)

FundingCreditOptions.propTypes = {
  formData: PropTypes.arrayOf(
    PropTypes.shape({
      amount: PropTypes.number,
      companyexportplan: PropTypes.number.isRequired,
      funding_option: PropTypes.string,
      pk: PropTypes.number.isRequired,
    })
  ).isRequired,
  companyexportplan: PropTypes.number.isRequired,
  fundingCreditOptions: PropTypes.shape({
    id: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    options: PropTypes.array.isRequired,
    placeholder: PropTypes.string.isRequired,
  }).isRequired,
  lessonDetails: PropTypes.oneOfType([PropTypes.string]).isRequired,
  currentSection: PropTypes.shape({
    url: PropTypes.string,
    lessons: PropTypes.arrayOf(PropTypes.string).isRequired,
  }).isRequired,
  model_name: PropTypes.string.isRequired,
}

FundingCreditOptions.defaultProps = {
  formData: [],
}

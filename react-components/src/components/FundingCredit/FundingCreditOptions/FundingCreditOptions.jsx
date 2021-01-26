import React, { memo, useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import Services from '@src/Services'
import { Total } from './Total'
import { Options } from './Options'
import { useDebounce } from '@src/components/hooks/useDebounce'

export const FundingCreditOptions = memo(
  ({ formData, currency, companyexportplan, fundingCreditOptions }) => {
    const [funding, setFunding] = useState(formData)
    const [fundingTotal, setFundingTotal] = useState(null)

    const calclatedTotal = () =>
      funding.reduce((acc, curr) => acc + Number(curr.amount), 0)

    useEffect(() => {
      setFundingTotal(calclatedTotal)
      return () => {}
    }, [funding])

    const addFunding = () => {
      const newFunding = {}
      newFunding.companyexportplan = companyexportplan
      newFunding.amount = 0

      Services.createFundingCreditOption({ ...newFunding })
        .then((data) => setFunding([...funding, data]))
        .then(() => {
          const newElement = document.getElementById(
            `Funding ${funding.length + 1}`
          ).parentNode
          newElement.scrollIntoView()
        })
        .catch(() => {})
    }

    const deleteFunding = (id) => {
      Services.deleteFundingCreditOption(id)
        .then(() => {
          setFunding(funding.filter((x) => x.pk !== id))
        })
        .catch(() => {})
    }

    const update = (field, selected) => {
      Services.updateFundingCreditOption({ ...field, ...selected })
        .then(() => {})
        .catch(() => {})
    }

    const debounceUpdate = useDebounce(update)

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
        <Options
          formData={funding}
          currency={currency}
          selectData={fundingCreditOptions}
          deleteFunding={deleteFunding}
          onChange={onChange}
          addFunding={addFunding}
        />
        <Total label="Total funding" currency={currency} total={fundingTotal} />
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
  fundingCreditOptions: PropTypes.objectOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      name: PropTypes.string.isRequired,
      options: PropTypes.array.isRequired,
      placeholder: PropTypes.string.isRequired,
    })
  ),
}

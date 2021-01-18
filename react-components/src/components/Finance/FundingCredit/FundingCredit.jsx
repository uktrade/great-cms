import React, { memo, useState, useEffect } from 'react'
// import PropTypes from 'prop-types'
import Services from '@src/Services'
import { Total } from './Total'
import { Options } from './Options'
import { fundingCreditOptions } from '../constants'
import { useDebounce } from '@src/components/hooks/useDebounce'

export const FundingCredit = memo(
  ({ formFields, currency, companyexportplan }) => {
    const [funding, setFunding] = useState(formFields)
    const [fundingTotal, setFundingTotal] = useState(null)

    const calclatedTotal = () =>
      funding.reduce((acc, curr) => acc + curr.value, 0)

    useEffect(() => {
      setFundingTotal(calclatedTotal)
      return () => {}
    }, [funding])

    const addFunding = () => {
      const newFunding = {}
      newFunding.value = 0

      Services.createRouteToMarket({ ...newFunding })
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
      Services.deleteRouteToMarket(id)
        .then(() => {
          setFunding(funding.filter((x) => x.pk !== id))
        })
        .catch(() => {})
    }

    const update = (field, selected) => {
      Services.updateRouteToMarket({ ...field, ...selected })
        .then(() => {})
        .catch(() => {})
    }

    const debounceUpdate = useDebounce(update)

    const onChange = (type, id, selected) => {
      const field = funding.find((x) => x.pk === id)
      const updatedFunding = funding.map((x) =>
        x.pk === id ? { ...x, ...selected } : x
      )
      setFunding(updatedFunding)
      debounceUpdate(field, selected)
    }
    // debugger
    return (
      <>
        <Options
          formFields={funding}
          currency={currency}
          selectData={fundingCreditOptions}
          deleteFunding={deleteFunding}
          onChange={onChange}
        />
        <button
          type="button"
          className="button button--large button--icon"
          onClick={addFunding}
        >
          <i className="fas fa-plus-circle" />
          Add funding option
        </button>
        <Total label="Total funding" currency={currency} total={fundingTotal} />
      </>
    )
  }
)

// FundingCredit.propTypes = {
//   costs: PropTypes.arrayOf(
//     PropTypes.shape({
//       label: PropTypes.string.isRequired,
//       id: PropTypes.string.isRequired,
//       heading: PropTypes.string.isRequired,
//       description: PropTypes.string.isRequired,
//     })
//   ).isRequired,
//   currency: PropTypes.string.isRequired,
//   data: PropTypes.objectOf(PropTypes.number).isRequired,
//   update: PropTypes.func.isRequired,
// }

import React, { memo, useState } from 'react'
// import PropTypes from 'prop-types'
import Services from '@src/Services'
import { Trips } from './Trips'
import { useDebounce } from '@src/components/hooks/useDebounce'

export const PlannedTravel = ({ formData, companyexportplan }) => {
  const [trips, setTrips] = useState(formData)

  const addTrip = () => {
    const newTrip = {}
    newTrip.companyexportplan = companyexportplan
    newTrip.value = ''

    Services.createFundingCreditOption({ ...newTrip })
      .then((data) => setTrips([...trips, data]))
      .then(() => {
        const newElement = document.getElementById(`Trip ${trips.length + 1}`)
          .parentNode
        newElement.scrollIntoView()
      })
      .catch(() => {})
  }

  const deleteTrip = (id) => {
    Services.deleteFundingCreditOption(id)
      .then(() => {
        setTrips(funding.filter((x) => x.pk !== id))
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
    const field = trips.find((x) => x.pk === id)
    field.companyexportplan = companyexportplan
    const updatedTrips = trips.map((x) =>
      x.pk === id ? { ...x, ...value } : x
    )
    setTrips(updatedTrips)
    debounceUpdate(field, value)
  }
  return (
    <>
      <h3 className="h-s">Planned travel</h3>
      <Trips
        formData={trips}
        deleteTrip={deleteTrip}
        onChange={onChange}
        addTrip={addTrip}
      />
    </>
  )
}

// FundingCreditOptions.propTypes = {
//   formData: PropTypes.arrayOf(
//     PropTypes.shape({
//       amount: PropTypes.number,
//       companyexportplan: PropTypes.number.isRequired,
//       funding_option: PropTypes.string,
//       pk: PropTypes.number.isRequired,
//     })
//   ).isRequired,
//   companyexportplan: PropTypes.number.isRequired,
//   fundingCreditOptions: PropTypes.shape({
//     id: PropTypes.string.isRequired,
//     name: PropTypes.string.isRequired,
//     options: PropTypes.array.isRequired,
//     placeholder: PropTypes.string.isRequired,
//   }).isRequired,
// }

// FundingCreditOptions.defaultProps = {
//   formData: [],
// }

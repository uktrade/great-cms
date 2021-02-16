import React, { memo, useState } from 'react'
// import PropTypes from 'prop-types'
import Services from '@src/Services'
import { useDebounce } from '@src/components/hooks/useDebounce'
import { Learning } from '@src/components/Learning/Learning'
import { Trips } from './Trips'

export const PlannedTravel = ({
  formData,
  companyexportplan,
  lesson,
  tooltip,
  model_name,
}) => {
  const [trips, setTrips] = useState(formData)

  const addTrip = () => {
    const newTrip = {
      companyexportplan,
      model_name,
      note: '',
    }

    Services.apiModelObjectManage({ ...newTrip }, 'POST')
      .then((data) => setTrips([...trips, data]))
      .catch(() => {})
  }

  const deleteTrip = (id) => {
    Services.apiModelObjectManage({ model_name, pk: id }, 'DELETE')
      .then(() => {
        setTrips(trips.filter((x) => x.pk !== id))
      })
      .catch(() => {})
  }

  const update = (field, value) => {
    Services.apiModelObjectManage({ model_name, ...field, ...value }, 'PATCH')
      .then(() => {})
      .catch(() => {})
  }

  const debounceUpdate = useDebounce(update)

  const onChange = (id, value) => {
    value = { note: value }
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
      <h2 className="h-m m-b-xs">Planned travel</h2>
      <p>
        It is likely you will have to go on business trips to your chosen
        markets to build relationships and seal those all important deals.
      </p>
      <p>
        Add all your upcoming trips and important information about them in the
        following tool.
      </p>
      <Learning tooltip={tooltip} lesson={lesson} />
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

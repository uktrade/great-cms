import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { AddButton } from '@src/components/ObjectivesList/AddButton/AddButton'
import { Trip } from './Trip'

export const Trips = memo(({ formData, onChange, deleteTrip, addTrip }) => {
  const isDisabled = formData.length
    ? !formData[formData.length - 1].note
    : false
  return (
    <>
      {formData.length !== 0 && (
        <div className="costs bg-blue-deep-10 m-b-s">
          {formData.map(({ pk, note }, i) => (
            <Trip
              index={i + 1}
              key={pk}
              id={pk}
              note={note}
              onChange={onChange}
              deleteTrip={deleteTrip}
            />
          ))}
        </div>
      )}
      <AddButton add={addTrip} cta="Add a trip" isDisabled={isDisabled} />
    </>
  )
})

Trips.propTypes = {
  formData: PropTypes.arrayOf(
    PropTypes.shape({
      note: PropTypes.string,
      companyexportplan: PropTypes.number,
      pk: PropTypes.number,
    })
  ).isRequired,
  onChange: PropTypes.func.isRequired,
  deleteTrip: PropTypes.func.isRequired,
  addTrip: PropTypes.func.isRequired,
}

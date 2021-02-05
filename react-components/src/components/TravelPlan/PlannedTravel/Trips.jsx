import React, { memo } from 'react'
// import PropTypes from 'prop-types'

import { Trip } from './Trip'

export const Trips = ({ formData, onChange, deleteTrip, addTrip }) => {
  return (
    <div className="costs costs--funding bg-blue-deep-10 p-v-s">
      <table className="m-b-0">
        <tbody>
          {formData.map(({ pk, value }) => (
            <Trip
              key={pk}
              id={pk}
              value={value}
              onChange={onChange}
              deleteTrip={deleteTrip}
            />
          ))}
        </tbody>
      </table>
      <button
        type="button"
        className="button button--secondary button--icon button--small button--add"
        onClick={addTrip}
      >
        <i className="fas fa-plus-circle" />
        <span>Add a trip</span>
      </button>
    </div>
  )
}

// Options.propTypes = {
//   formData: PropTypes.arrayOf(
//     PropTypes.shape({
//       amount: PropTypes.number,
//       companyexportplan: PropTypes.number.isRequired,
//       funding_option: PropTypes.string,
//       pk: PropTypes.number.isRequired,
//     })
//   ).isRequired,
//   selectData: PropTypes.shape({
//     id: PropTypes.string.isRequired,
//     name: PropTypes.string.isRequired,
//     options: PropTypes.array.isRequired,
//     placeholder: PropTypes.string.isRequired,
//   }).isRequired,
//   currency: PropTypes.string.isRequired,
//   onChange: PropTypes.func.isRequired,
//   deleteFunding: PropTypes.func.isRequired,
//   addFunding: PropTypes.func.isRequired,
// }

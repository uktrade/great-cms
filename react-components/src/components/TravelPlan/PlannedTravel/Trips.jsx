import React, { memo } from 'react'
// import PropTypes from 'prop-types'

import { Trip } from './Trip'

export const Trips = ({ formData, onChange, deleteTrip, addTrip }) => {
  return (
    <>
      {formData.length !== 0 && (
        <div className="costs costs--trips bg-blue-deep-10 p-v-s m-b-s">
          <table className="m-v-0">
            <tbody>
              {formData.map(({ pk, value }, i) => (
                <Trip
                  index={i + 1}
                  key={pk}
                  id={pk}
                  value={value}
                  onChange={onChange}
                  deleteTrip={deleteTrip}
                />
              ))}
            </tbody>
          </table>
        </div>
      )}
      <button
        type="button"
        className="button button--large button--icon"
        onClick={addTrip}
      >
        <i class="fas fa-plus-circle"></i>Add a trip
      </button>
    </>
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

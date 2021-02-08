import React, { memo } from 'react'
// import PropTypes from 'prop-types'

import { TextArea } from '@src/components/Form/TextArea'

export const Trip = ({ id, value, onChange, deleteTrip, index }) => {
  return (
    <>
      <tr className="border-none">
        <td>
          <p className="body-l m-v-xs m-b-s">Trip {index}</p>
          <TextArea
            id={id.toString()}
            type="text"
            label={'label'}
            hideLabel
            value={value}
            onChange={(e) => onChange(id, e[id])}
            formGroupClassName="m-b-0"
          />
        </td>
      </tr>
      <tr>
        <td className="text-center" colSpan="2">
          <button
            type="button"
            title="Click to delete this funding option and its data."
            className="button button--delete button--small button--only-icon button--tertiary"
            onClick={() => deleteTrip(id)}
          >
            <i className="fas fa-trash-alt"></i>
          </button>
        </td>
      </tr>
    </>
  )
}

// Trip.propTypes = {
//   index: PropTypes.number.isRequired,
//   id: PropTypes.number.isRequired,
//   value: PropTypes.string.isRequired,
//   onChange: PropTypes.func.isRequired,
//   deleteFunding: PropTypes.func.isRequired,
// }

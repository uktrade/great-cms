import React, { memo } from 'react'
// import PropTypes from 'prop-types'

import { TextArea } from '@src/components/Form/TextArea'

export const Trip = ({ id, value, onChange, deleteTrip }) => {
  return (
    <>
      <tr className="border-none">
        <td>
          <TextArea
            id={id}
            type="text"
            label={'label'}
            hideLabel
            value={value}
            onChange={(e) => onChange(id, { value: e[id] })}
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

// Option.propTypes = {
//   id: PropTypes.number.isRequired,
//   value: PropTypes.number.isRequired,
//   currency: PropTypes.string.isRequired,
//   selectData: PropTypes.shape({
//     id: PropTypes.string.isRequired,
//     name: PropTypes.string.isRequired,
//     options: PropTypes.array.isRequired,
//     placeholder: PropTypes.string.isRequired,
//   }).isRequired,
//   onChange: PropTypes.func.isRequired,
//   deleteFunding: PropTypes.func.isRequired,
// }

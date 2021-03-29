import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { TextArea } from '@src/components/Form/TextArea'
import { ConfirmModal } from '@src/components/ConfirmModal/ConfirmModal'

export const Trip = memo(({ id, note, onChange, deleteTrip, index }) => {
  return (
    <>
      <tr className="border-none">
        <td>
          <p className="body-l m-v-xs m-b-s">Trip {index}</p>
          <TextArea
            id={id.toString()}
            type="text"
            label="label"
            hideLabel
            value={note}
            onChange={(e) => onChange(id, e[id])}
            formGroupClassName="m-b-0"
          />
        </td>
      </tr>
      <tr>
        <td className="text-center" colSpan="2">
          <ConfirmModal hasData={!!note} deleteItem={() => deleteTrip(id)} />
        </td>
      </tr>
    </>
  )
})

Trip.propTypes = {
  id: PropTypes.number.isRequired,
  note: PropTypes.string.isRequired,
  index: PropTypes.number.isRequired,
  onChange: PropTypes.func.isRequired,
  deleteTrip: PropTypes.func.isRequired,
}

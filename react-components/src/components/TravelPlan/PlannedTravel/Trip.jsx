import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { TextArea } from '@src/components/Form/TextArea'
import { ConfirmModal } from '@src/components/ConfirmModal/ConfirmModal'

export const Trip = memo(({ id, note, onChange, deleteTrip, index }) => {
  return (
    <div className="costs__option costs__option--border">
      <div className="costs__border">
        <h3 className="body-l-b">Trip {index}</h3>
        <TextArea
          id={id.toString()}
          type="text"
          label="label"
          hideLabel
          value={note}
          onChange={(e) => onChange(id, e[id])}
          formGroupClassName="m-b-0"
        />
      </div>
      <div className="text-center p-t-xs">
        <ConfirmModal hasData={!!note} deleteItem={() => deleteTrip(id)} />
      </div>
    </div>
  )
})

Trip.propTypes = {
  id: PropTypes.number.isRequired,
  note: PropTypes.string.isRequired,
  index: PropTypes.number.isRequired,
  onChange: PropTypes.func.isRequired,
  deleteTrip: PropTypes.func.isRequired,
}

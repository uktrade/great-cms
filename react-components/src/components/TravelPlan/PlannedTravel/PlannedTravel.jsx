import React, { memo, useState } from 'react'
import PropTypes from 'prop-types'
import { useDebounce } from '@src/components/hooks/useDebounce'
import { Learning } from '@src/components/Learning/Learning'
import { useUpdate } from '@src/components/hooks/useUpdate/useUpdate'
import ErrorList from '@src/components/ErrorList'
import { Trips } from './Trips'

export const PlannedTravel = memo(
  ({ formData, companyexportplan, lesson, tooltip, model_name }) => {
    const [trips, setTrips] = useState(formData)
    const [update, create, deleteItem, message, errors] = useUpdate(
      'travel-plan'
    )

    const addTrip = () => {
      const newTrip = {
        companyexportplan,
        model_name,
        note: '',
      }

      create({ ...newTrip }).then((data) => setTrips([...trips, data]))
    }

    const deleteTrip = (id) => {
      deleteItem({ model_name, pk: id }).then(() => {
        setTrips(trips.filter((x) => x.pk !== id))
      })
    }

    const request = (field, value) => {
      update({ model_name, ...field, ...value })
    }

    const debounceUpdate = useDebounce(request)

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
          It's likely you'll need to visit your chosen markets to build business
          relationships and seal important deals.
        </p>
        <Learning tooltip={tooltip} lesson={lesson} className="m-b-xs" />
        <Trips
          formData={trips}
          deleteTrip={deleteTrip}
          onChange={onChange}
          addTrip={addTrip}
        />
        <ErrorList errors={errors.__all__ || []} className="m-t-s" />
      </>
    )
  }
)

PlannedTravel.propTypes = {
  formData: PropTypes.arrayOf(
    PropTypes.shape({
      note: PropTypes.string,
      companyexportplan: PropTypes.number,
      pk: PropTypes.number,
    })
  ),
  companyexportplan: PropTypes.number.isRequired,
  lesson: PropTypes.shape({
    category: PropTypes.string,
    duration: PropTypes.string,
    title: PropTypes.string,
    url: PropTypes.string,
  }).isRequired,
  tooltip: PropTypes.shape({
    content: PropTypes.string,
  }).isRequired,
  model_name: PropTypes.string.isRequired,
}

PlannedTravel.defaultProps = {
  formData: [],
}

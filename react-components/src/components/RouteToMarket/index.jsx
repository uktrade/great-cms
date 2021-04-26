import React, { useState, memo } from 'react'
import PropTypes from 'prop-types'

import { RouteToMarketSection } from '@src/components/RouteToMarket/RouteToMarketSection'
import { objectHasValue } from '@src/Helpers'
import { useDebounce } from '@src/components/hooks/useDebounce'
import { AddButton } from '@src/components/ObjectivesList/AddButton/AddButton'
import { useUpdate } from '@src/components/hooks/useUpdate/useUpdate'

export const RouteToMarket = memo(
  ({ fields, formData, formFields, model_name }) => {
    const [routes, setRoutes] = useState(fields)

    const { companyexportplan, pk, ...lastField } = routes.length
      ? routes[routes.length - 1]
      : {}
    const [update, create, deleteItem] = useUpdate('route-to-market')

    const addTable = () => {
      create({ ...formFields })
        .then((data) => setRoutes([...routes, data]))
        .then(() => {
          const newElement = document.getElementById(
            `Route to market ${routes.length + 1}`
          ).parentNode
          newElement.scrollIntoView()
        })
    }

    const deleteTable = (id) => {
      deleteItem({ pk: id, model_name }).then(() => {
        setRoutes(routes.filter((x) => x.pk !== id))
      })
    }

    const request = (field, selected) =>
      update({ ...field, ...selected, model_name })

    const debounceUpdate = useDebounce(request)

    const onChange = (id, selected) => {
      const field = routes.find((x) => x.pk === id)
      const updatedRoutes = routes.map((x) =>
        x.pk === id ? { ...x, ...selected } : x
      )

      setRoutes(updatedRoutes)
      debounceUpdate(field, selected)
    }

    return (
      <>
        {routes.length >= 1 &&
          routes.map((field, id) => (
            <RouteToMarketSection
              key={field.pk}
              {...formData}
              data={formData.data.map((x) =>
                x.name === 'route' ? { ...x, label: `${x.label} ${id + 1}` } : x
              )}
              field={field}
              onChange={onChange}
              deleteTable={deleteTable}
            />
          ))}
        <AddButton
          add={addTable}
          isDisabled={routes.length ? !objectHasValue(lastField) : false}
          cta="Add route to market"
        />
      </>
    )
  }
)

RouteToMarket.propTypes = {
  fields: PropTypes.arrayOf(
    PropTypes.objectOf(
      PropTypes.oneOfType([PropTypes.string, PropTypes.number])
    ).isRequired
  ).isRequired,
  formData: PropTypes.shape({
    data: PropTypes.arrayOf(
      PropTypes.shape({
        name: PropTypes.string,
        label: PropTypes.string,
        options: PropTypes.arrayOf(
          PropTypes.shape({
            value: PropTypes.string,
            label: PropTypes.string,
          })
        ).isRequired,
      }).isRequired
    ).isRequired,
    example: PropTypes.string.isRequired,
    label: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
  }).isRequired,
  formFields: PropTypes.objectOf(
    PropTypes.oneOfType([PropTypes.string, PropTypes.number])
  ).isRequired,
  model_name: PropTypes.string.isRequired,
}

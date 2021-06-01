import React, { memo, useState } from 'react'
import PropTypes from 'prop-types'

import ErrorList from '@src/components/ErrorList'
import { objectHasValue } from '@src/Helpers'
import { useDebounce } from '@src/components/hooks/useDebounce'
import { AddButton } from '@src/components/ObjectivesList/AddButton/AddButton'
import { useUpdate } from '@src/components/hooks/useUpdate/useUpdate'
import { Objective } from './Objective'

export const ObjectivesList = memo(
  ({ exportPlanID, objectives: initialObjectives, model_name }) => {
    const [objectives, setObjectives] = useState(initialObjectives || [])
    const [update, create, deleteItem, message, errors] = useUpdate(
      'Objectives'
    )
    const {
      companyexportplan,
      start_date,
      end_date,
      pk,
      ...lastField
    } = objectives.length ? objectives[objectives.length - 1] : {}
    const limit = 5

    const request = (data) => update({ model_name, ...data })
    const debounceUpdate = useDebounce(request)

    const createObjective = () => {
      const date = new Date()
      const today = `${date.getFullYear().toString()}-${(date.getMonth() + 1)
        .toString()
        .padStart(2, 0)}-${date.getDate().toString().padStart(2, 0)}`

      create({
        description: '',
        owner: '',
        planned_reviews: '',
        start_date: today,
        end_date: today,
        companyexportplan: exportPlanID,
        model_name,
      }).then((data) => {
        setObjectives([...objectives, { ...data }])
      })
    }

    const deleteObjective = (id) => {
      deleteItem({ pk: id, model_name }).then(() => {
        const updatedObjectives = objectives.filter(
          (objective) => objective.pk !== id
        )
        setObjectives(updatedObjectives)
      })
    }

    const updateObjective = (data) => {
      const updatedObjectives = objectives.map((item) =>
        item.pk === data.pk ? { ...item, ...data } : item
      )
      setObjectives(updatedObjectives)
      debounceUpdate(data)
    }

    return (
      <div className="form-table bg-white br-xs m-b-m">
        {objectives.map((objective, i) => (
          <Objective
            key={objective.pk}
            id={i}
            isLoading={objective.isLoading}
            errors={objective.errors}
            data={objective}
            number={i + 1}
            handleChange={updateObjective}
            deleteObjective={deleteObjective}
          />
        ))}
        {message && <p id="objective-saved-message" role="status">Changes saved.</p>}
        <AddButton
          isDisabled={objectives.length ? !objectHasValue(lastField) : false}
          numberOfItems={objectives.length}
          add={createObjective}
          field={lastField}
          cta={`Add goal ${objectives.length + 1} of ${limit}`}
        />
        <ErrorList errors={errors.__all__ || []} className="m-0" />
      </div>
    )
  }
)

ObjectivesList.propTypes = {
  objectives: PropTypes.arrayOf(
    PropTypes.shape({
      description: PropTypes.string,
      owner: PropTypes.string,
      planned_reviews: PropTypes.string,
      start_date: PropTypes.string,
      end_date: PropTypes.string,
      companyexportplan: PropTypes.number,
      pk: PropTypes.number,
      showSavedMessage: PropTypes.bool,
      errors: PropTypes.shape({
        __all__: PropTypes.arrayOf(PropTypes.string),
      }),
    }).isRequired
  ),
  exportPlanID: PropTypes.number.isRequired,
  model_name: PropTypes.string.isRequired,
}

ObjectivesList.defaultProps = {
  objectives: [],
}

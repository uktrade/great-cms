import React, { memo, useState, useRef } from 'react'
import PropTypes from 'prop-types'

import ErrorList from '@src/components/ErrorList'
import { objectHasValue } from '@src/Helpers'
import { useDebounce } from '@src/components/hooks/useDebounce'
import { AddButton } from '@src/components/ObjectivesList/AddButton/AddButton'
import { useUpdate } from '@src/components/hooks/useUpdate/useUpdate'
import { Objective } from './Objective'

export const ObjectivesList = memo(
  // eslint-disable-next-line camelcase
  ({ exportPlanID, objectives: initialObjectives, model_name, example }) => {
    const [objectives, setObjectives] = useState(initialObjectives || [])
    const [update, create, deleteItem, message, errors] =
      useUpdate('Objectives')
    const objectiveElementList = useRef([])
    const {
      companyexportplan,
      // eslint-disable-next-line camelcase
      end_month,
      // eslint-disable-next-line camelcase
      end_year,
      pk,
      ...lastField
    } = objectives.length ? objectives[objectives.length - 1] : {}
    const limit = 5

    const request = (data) => update({ model_name, ...data })
    const debounceUpdate = useDebounce(request)

    const createObjective = () => {
      const today = new Date()
      const month = `${today.getMonth() + 1}`
      const year = `${today.getFullYear()}`
      create({
        description: '',
        owner: '',
        planned_reviews: '',
        end_month: month,
        end_year: year,
        companyexportplan: exportPlanID,
        model_name,
      }).then((data) => {
        setObjectives([...objectives, { ...data }])
        objectiveElementList.current[
          objectiveElementList.current.length - 1
        ].focus()
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
            key={objective.pk || `objective-${i}`}
            id={i}
            isLoading={objective.isLoading}
            errors={objective.errors}
            data={objective}
            number={i + 1}
            handleChange={updateObjective}
            deleteObjective={deleteObjective}
            ref={(element) => {
              objectiveElementList.current[i] = element
            }}
            example={i === 0 ? example : {}}
          />
        ))}
        {message && (
          <p id="objective-saved-message" role="status">
            Changes saved.
          </p>
        )}
        <AddButton
          isDisabled={objectives.length ? !objectHasValue(lastField) : false}
          numberOfItems={objectives.length}
          add={createObjective}
          field={lastField}
          cta={`Add objective ${objectives.length + 1} of ${limit}`}
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
      end_month: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
      end_year: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
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
  example: PropTypes.shape({
    content: PropTypes.string,
  }),
}

ObjectivesList.defaultProps = {
  objectives: [],
  example: {},
}

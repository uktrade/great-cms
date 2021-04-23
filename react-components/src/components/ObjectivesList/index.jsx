import React, { memo, useState } from 'react'
import PropTypes from 'prop-types'

import ErrorList from '@src/components/ErrorList'
import { analytics, objectHasValue } from '@src/Helpers'
import { useDebounce } from '@src/components/hooks/useDebounce'
import { AddButton } from '@src/components/ObjectivesList/AddButton/AddButton'
import { Objective } from './Objective'
import Services from '../../Services'

export const ObjectivesList = memo(
  ({ exportPlanID, objectives: initialObjectives, model_name }) => {
    const [errors, setErrors] = useState({})
    const [objectives, setObjectives] = useState(initialObjectives || [])
    const [message, setMessage] = useState(false)
    const debounceMessage = useDebounce(setMessage)
    const {
      companyexportplan,
      start_date,
      end_date,
      pk,
      ...lastField
    } = objectives.length ? objectives[objectives.length - 1] : {}
    const limit = 5

    const update = (data) => {
      Services.apiModelObjectManage({ model_name, ...data }, 'PATCH')
        .then(() => {
          setMessage(true)
        })
        .then(() => {
          analytics({
            event: 'planSectionSaved',
            sectionTitle: 'Objectives',
          })
        })
        .catch((err) => {
          setErrors(err)
        })
        .finally(() => {
          setErrors({})
          debounceMessage(false)
        })
    }

    const debounceUpdate = useDebounce(update)

    const createObjective = () => {
      const date = new Date()
      const today = `${date.getFullYear().toString()}-${(date.getMonth() + 1)
        .toString()
        .padStart(2, 0)}-${date.getDate().toString().padStart(2, 0)}`

      Services.apiModelObjectManage(
        {
          description: '',
          owner: '',
          planned_reviews: '',
          start_date: today,
          end_date: today,
          companyexportplan: exportPlanID,
          model_name,
        },
        'POST'
      )
        .then((response) => {
          response.json().then((data) => {
            setObjectives([...objectives, { ...data }])
            setErrors({})
          })
        })
        .catch((err) => {
          setErrors({ err })
        })
    }

    const deleteObjective = (id) => {
      Services.apiModelObjectManage({ pk: id, model_name })
        .then(() => {
          const updatedObjectives = objectives.filter(
            (objective) => objective.pk !== id
          )
          setObjectives(updatedObjectives)
        })
        .catch((err) => {
          setErrors({ err })
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
        {message && <p id="objective-saved-message">Changes saved.</p>}
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

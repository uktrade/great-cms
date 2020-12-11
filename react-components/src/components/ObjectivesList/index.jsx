import React, { memo, useState } from 'react'
import PropTypes from 'prop-types'

import ErrorList from '@src/components/ErrorList'
import { Objective } from './Objective'
import Services from '../../Services'
import { analytics } from '@src/Helpers'
import { useDebounce } from '@src/components/hooks/useDebounce'

export const ObjectivesList = memo(
  ({ exportPlanID, objectives: initialObjectives }) => {
    const [errors, setErrors] = useState({})
    const [objectives, setObjectives] = useState(initialObjectives || [])
    const [message, setMessage] = useState(false)
    const debounceMessage = useDebounce(setMessage)

    const update = (data) => {
      Services.updateObjective(data)
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

      Services.createObjective({
        description: '',
        owner: '',
        planned_reviews: '',
        start_date: today,
        end_date: today,
        companyexportplan: exportPlanID,
      })
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

    const deleteObjective = (pk) => {
      Services.deleteObjective(pk)
        .then(() => {
          const updatedObjectives = objectives.filter(
            (objective) => objective.pk !== pk
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
        {objectives.length !== 5 && (
          <button
            type="button"
            className="button button--add button--large button--icon"
            onClick={createObjective}
          >
            <i className="fas fa-plus-circle" />
            Add goal {objectives.length + 1} of 5
          </button>
        )}
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
}

ObjectivesList.defaultProps = {
  objectives: [],
}

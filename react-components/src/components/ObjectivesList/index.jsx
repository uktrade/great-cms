import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { Subject } from 'rxjs'
import { debounceTime, delay } from 'rxjs/operators'

import ErrorList from '@src/components/ErrorList'
import { Objective } from './Objective'
import Services from '../../Services'
import { analytics } from '@src/Helpers'

export class ObjectivesList extends Component {

  constructor(props) {
    super(props)

    this.state = {
      errors: {},
      objectives: props.objectives || []
    }

    const { objectives } = this.state

    objectives.forEach(objective => {
      objective.showSavedMessage = false
    })

    this.inputToSave$ = new Subject()

    const saveInput$ = this.inputToSave$.pipe(debounceTime(1000 * 3))

    saveInput$.subscribe(data => {

      this.setState(state => {
        const updatedObjectives = [...state.objectives]
        return { objectives: updatedObjectives }

      }, () => {
        Services.updateObjective(data.data)
          .then(this.handleUpdateSuccess)
          .then(() => {
            analytics({
              'event': 'planSectionSaved',
              'sectionTitle': 'Objectives'
            })
          })
          .catch((err) => this.handleError(err, data.data.pk))
      })
    })

    const afterSave$ = saveInput$.pipe(delay(1000 * 3))

    afterSave$.subscribe(data => {
      this.setState(state => {
        const objectiveToUpdate = state.objectives.indexOf(state.objectives.filter(objective => objective.pk === data.data.pk)[0])
        const updatedObjectives = [...state.objectives]
        updatedObjectives[objectiveToUpdate].showSavedMessage = false
        return { objectives: updatedObjectives }
      })
    })
  }

  handleCreateSuccess = (response) => {
    response.json().then(data => {
      this.setState(state => {
        const newObjective = {...data}
        newObjective.showSavedMessage = false
        newObjective.errors = {}
        const updatedObjectives = state.objectives.concat([newObjective])
        return { objectives: updatedObjectives }
      })
    })
  }

  handleUpdateSuccess = (response) => {
    response.json().then(data => {
      this.setState(state => {
        const objectiveToUpdate = state.objectives.indexOf(state.objectives.filter(objective => objective.pk === data.pk)[0])
        const updatedObjectives = [...state.objectives]
        updatedObjectives[objectiveToUpdate].showSavedMessage = true
        updatedObjectives[objectiveToUpdate].errors = {}
        return { objectives: updatedObjectives }
      })
    })
  }

  handleDeleteSuccess = (response, pk) => {
    response.json().then(() => {
      this.setState(state => {
        const updatedObjectives = state.objectives.filter(objective => objective.pk !== pk)
        return { objectives: updatedObjectives, errors: {} }
      })
    })
  }

  handleError = (errors, pk) => {
    this.setState(state => {
      const objectiveToUpdate = state.objectives.indexOf(state.objectives.filter(objective => objective.pk === pk)[0])
      const updatedObjectives = [...state.objectives]
      updatedObjectives[objectiveToUpdate].errors = errors
      return { objectives: updatedObjectives }
    })
  }

  createObjective = () => {

    const { exportPlanID } = this.props
    const date = new Date()
    const today = `${date.getFullYear().toString()}-${(date.getMonth() + 1).toString().padStart(2, 0)}-${date.getDate().toString().padStart(2, 0)}`

    Services.createObjective({
      description: '',
      owner: '',
      planned_reviews: '',
      start_date: today,
      end_date: today,
      companyexportplan: exportPlanID,
    })
      .then(this.handleCreateSuccess)
      .catch(this.handleCreateError)
  }

  handleCreateError = (errors) => {
    this.setState({ errors })
  }

  deleteObjective = (pk) => {
    this.setState(state => {
      const updatedObjectives = [...state.objectives]
      return { objectives: updatedObjectives }
    }, () => {
      Services.deleteObjective(pk)
        .then((res) => this.handleDeleteSuccess(res, pk))
        .catch((err) => this.handleError(err, pk))
    })
  }

  updateObjective = (data) => {
    this.setState(state => {
      const updatedObjectives = [...state.objectives]
      updatedObjectives[data.id] = data.data
      return { objectives: updatedObjectives }

    }, () => {
      this.inputToSave$.next(data)
    })

  }

  render() {
    const { errors, objectives } = this.state

    return (
      <div className='objectives-list'>
        <div className='objective-box bg-white br-xs m-b-m'>
          {
            objectives.map((objective, i) => (
              <Objective
                key={objective.pk}
                id={i}
                isLoading={objective.isLoading}
                errors={objective.errors}
                showSavedMessage={objective.showSavedMessage}
                data={objective}
                number={i+1}
                handleChange={this.updateObjective}
                deleteObjective={this.deleteObjective}
              />
            ))
          }
          {objectives.length !==5 &&
            <button
              type='button'
              className='button button--large button--icon'
              onClick={this.createObjective}>
                <i className='fas fa-plus-circle' />Add goal {objectives.length+1} of 5
            </button>
          }
          <ErrorList errors={errors.__all__ || []} className='m-0' />
        </div>
      </div>
    )
  }
}

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
        __all__: PropTypes.arrayOf(PropTypes.string)
      }),
    }).isRequired,
  ),
  exportPlanID: PropTypes.number.isRequired,
}

ObjectivesList.defaultProps = {
  objectives: [],
}

import React from 'react'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types'

import { Subject } from 'rxjs'
import { debounceTime, delay } from 'rxjs/operators'

import ErrorList from '@src/components/ErrorList'
import Objective from './Objective'
import Services from '../Services'
import Spinner from './Spinner/Spinner'


class ObjectivesList extends React.Component {

  constructor(props) {
    super(props)

    this.state = {
      errors: {},
      objectives: this.props.objectives || []
    }

    const { objectives } = this.state

    objectives.forEach(objective => {
      objective.isLoading = false
      objective.showSavedMessage = false
    })

    this.inputToSave$ = new Subject()

    const saveInput$ = this.inputToSave$.pipe(debounceTime(1000 * 3))

    saveInput$.subscribe(data => {

      this.setState(state => {
        const updatedObjectives = [...state.objectives]
        updatedObjectives[data.id].isLoading = true
        return { objectives: updatedObjectives }

      }, () => {
        Services.updateObjective(data.data)
          .then(this.handleUpdateSuccess)
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

    this.bindEvents()
  }


  bindEvents() {
    this.createObjective = this.createObjective.bind(this)
    this.updateObjective = this.updateObjective.bind(this)
    this.deleteObjective = this.deleteObjective.bind(this)
    this.handleUpdateSuccess = this.handleUpdateSuccess.bind(this)
    this.handleCreateSuccess = this.handleCreateSuccess.bind(this)
    this.handleDeleteSuccess = this.handleDeleteSuccess.bind(this)
    this.handleError = this.handleError.bind(this)
    this.handleCreateError = this.handleCreateError.bind(this)
  }

  handleCreateSuccess(response) {
    response.json().then(data => {
      this.setState(state => {
        const newObjective = {...data}
        newObjective.isLoading = false
        newObjective.showSavedMessage = false
        newObjective.errors = {}
        const updatedObjectives = state.objectives.concat([newObjective])
        return { objectives: updatedObjectives, isLoading: false }
      })
    })
  }

  handleUpdateSuccess(response) {
    response.json().then(data => {
      this.setState(state => {
        const objectiveToUpdate = state.objectives.indexOf(state.objectives.filter(objective => objective.pk === data.pk)[0])
        const updatedObjectives = [...state.objectives]
        updatedObjectives[objectiveToUpdate].isLoading = false
        updatedObjectives[objectiveToUpdate].showSavedMessage = true
        updatedObjectives[objectiveToUpdate].errors = {}
        return { objectives: updatedObjectives }
      })
    })
  }

  handleDeleteSuccess(response, pk) {
    response.json().then(() => {
      this.setState(state => {
        const updatedObjectives = state.objectives.filter(objective => objective.pk !== pk)
        return { objectives: updatedObjectives, isLoading: false, errors: {} }
      })
    })
  }

  handleError(errors, pk) {
    this.setState(state => {
      const objectiveToUpdate = state.objectives.indexOf(state.objectives.filter(objective => objective.pk === pk)[0])
      const updatedObjectives = [...state.objectives]
      updatedObjectives[objectiveToUpdate].isLoading = false
      updatedObjectives[objectiveToUpdate].errors = errors
      return { objectives: updatedObjectives, isLoading: false }
    })
  }

  createObjective() {
    const data = {
      data: {
        description: '',
        owner: '',
        planned_reviews: '',
        start_date: '',
        end_date: '',
        companyexportplan: this.props.exportPlanID,
      }
    }
    this.setState({ isLoading: true }, () => {
      Services.createObjective(data.data)
        .then(this.handleCreateSuccess)
        .catch(this.handleCreateError)
    })
  }

  handleCreateError(errors) {
    this.setState({ isLoading: false, errors })
  }

  deleteObjective(pk) {
    this.setState(state => {
      const objectiveToUpdate = state.objectives.indexOf(state.objectives.filter(objective => objective.pk === pk)[0])
      const updatedObjectives = [...state.objectives]
      updatedObjectives[objectiveToUpdate].isLoading = true
      return { objectives: updatedObjectives }
    }, () => {
      Services.deleteObjective(pk)
        .then((res) => this.handleDeleteSuccess(res, pk))
        .catch((err) => this.handleError(err, pk))
    })
  }

  updateObjective(data) {
    this.setState(state => {
      const updatedObjectives = [...state.objectives]
      updatedObjectives[data.id] = data.data
      return { objectives: updatedObjectives }

    }, () => {
      this.inputToSave$.next(data)
    })

  }

  render() {
    const { errors, objectives, isLoading } = this.state

    let addNewButton
    if (isLoading) {
      addNewButton = (<Spinner text="Loading..."/>)
    } else {
      addNewButton = (
        <div className="button--plus">
          <span className="icon--plus"/>
          <button type="button" className="button--stone" onClick={this.createObjective}>Add next objective</button>
        </div>
      )
    }

    return (
      <div className="objectives-list">
        <div className="objective-box bg-white br-xs m-b-m border-thin border-light-grey">
          {
            objectives.map((objective, i) => (
              <Objective key={i} id={i} isLoading={objective.isLoading} errors={objective.errors} showSavedMessage={objective.showSavedMessage} data={objective} number={i+1} handleChange={this.updateObjective} deleteObjective={this.deleteObjective}/>
            ))
          }
          <div className="footer">
            {addNewButton}
            <ErrorList errors={errors.__all__ || []} className="m-0" />
          </div>
        </div>
      </div>
    )
  }

}

function createObjectivesList({ element, ...params }) {
  ReactDOM.render(<ObjectivesList {...params} />, element)
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
      isLoading: PropTypes.bool,
      showSavedMessage: PropTypes.bool,
      errors: PropTypes.shape({
        __all__: PropTypes.arrayOf(PropTypes.string)
      }),
    }).isRequired,
  ),
  exportPlanID: PropTypes.number.isRequired,
}

export { ObjectivesList, createObjectivesList }

ObjectivesList.defaultProps = {
  objectives: [],
}

import React from 'react'
import PropTypes from 'prop-types'

import Field from './Fields/Field'
import ErrorList from './ErrorList'
import Spinner from './Spinner/Spinner'


export default class Objective extends React.Component {

  constructor(props) {
    super(props)

    this.bindEvents()
  }

  bindEvents() {
    this.handleChange = this.handleChange.bind(this)
    this.deleteObjective = this.deleteObjective.bind(this)
  }

  handleChange(e) {
    const { name, value } = e.target

    const data = {
      data: {
        ...this.props.data,
        [name]: value,
      },
      id: this.props.id
    }

    this.props.handleChange(data)
  }

  deleteObjective() {
    this.props.deleteObjective(this.props.data.pk)
  }

  render() {
    const { number, data, isLoading, showSavedMessage, errors } = this.props

    let statusIndicator
    if (isLoading) {
      statusIndicator = <Spinner text="Saving..."/>
    } else if (showSavedMessage) {
      statusIndicator = <p id="objective-saved-message">Changes saved.</p>
    } else {
      statusIndicator = ''
    }

    return (
      <>
      <div className="objective p-h-s p-v-xs">
        <div className={`grid objective-fields ${isLoading ? 'loading' : ''}`}>
          <div className="c-1-4">
            <h3 className="h-m">Objective {number}</h3>
          </div>
          <div className="c-1-2">
            <Field
              id={`description_${number}`}
              type="textarea"
              placeholder="Add some text"
              label="Description"
              name="description"
              value={data.description}
              handleChange={this.handleChange}
              errors={[]}
            />
            <Field
              id={`start_date_${number}`}
              type="date"
              label="Start date"
              name="start_date"
              value={data.start_date}
              handleChange={this.handleChange}
              errors={[]}
            />
            <Field
              id={`end_date_${number}`}
              type="date"
              label="End date"
              name="end_date"
              value={data.end_date}
              handleChange={this.handleChange}
              errors={[]}
            />
            <Field
              id={`owner_${number}`}
              type="textarea"
              placeholder="Add an owner"
              label="Owner"
              name="owner"
              value={data.owner}
              handleChange={this.handleChange}
              errors={[]}
            />
            <Field
              id={`planned_reviews_${number}`}
              type="textarea"
              placeholder="Add some text"
              label="Planned reviews"
              name="planned_reviews"
              value={data.planned_reviews}
              handleChange={this.handleChange}
              errors={[]}
            />
          </div>
        </div>
        <button type="button" className="button--delete" onClick={this.deleteObjective}>Delete</button>
        {statusIndicator}
        <ErrorList errors={errors.__all__ || []} />
      </div>
      <hr/>
      </>
    )
  }

}

Objective.propTypes = {
  handleChange: PropTypes.func.isRequired,
  deleteObjective: PropTypes.func.isRequired,
  number: PropTypes.number.isRequired,
  id: PropTypes.number.isRequired,
  isLoading: PropTypes.bool,
  showSavedMessage: PropTypes.bool,
  errors: PropTypes.shape({
    __all__: PropTypes.arrayOf(PropTypes.string.isRequired),
  }),
  data: PropTypes.shape({
    description: PropTypes.string,
    owner: PropTypes.string,
    planned_reviews: PropTypes.string,
    start_date: PropTypes.string,
    end_date: PropTypes.string,
    companyexportplan: PropTypes.number.isRequired,
    pk: PropTypes.number.isRequired,
  }).isRequired
}

Objective.defaultProps = {
  errors: {__all__: []},
  isLoading: false,
  showSavedMessage: false,
}

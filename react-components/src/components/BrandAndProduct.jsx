import React from 'react'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types'

import { Subject } from 'rxjs'
import { debounceTime, delay } from 'rxjs/operators';

import ErrorList from '@src/components/ErrorList'
import FieldWithExample from '@src/components/Fields/FieldWithExample'
import Services from '../Services'
import Spinner from './Spinner/Spinner'


class BrandAndProductForm extends React.Component {
  constructor(props) {
    super(props)

    this.state = {
      errors: {},
      isLoading: false,
      showSavedMessage: false,
      formData: props.formData
    }

    this.inputToSave$ = new Subject()

    const saveInput$ = this.inputToSave$.pipe(debounceTime(1000 * 2))

    saveInput$.subscribe(data => {
      this.setState({ isLoading: true }, () => {
        Services.updateExportPlan(this.formatData(data))
          .then(this.handleUpdateSuccess)
          .catch(this.handleUpdateError)
      })
    })

    const afterSave$ = saveInput$.pipe(delay(1000 * 2))

    afterSave$.subscribe(() => {
      this.setState({ showSavedMessage: false })
    })

    this.bindEvents()
  }

  formatData(data) {
    return { [this.props.field] : data }
  }

  bindEvents() {
    this.handleChange = this.handleChange.bind(this)
    this.handleUpdateSuccess = this.handleUpdateSuccess.bind(this)
    this.handleUpdateError = this.handleUpdateError.bind(this)
  }

  handleUpdateSuccess() {
    this.setState({
      isLoading: false,
      showSavedMessage: true,
      errors: {}
    })
  }

  handleUpdateError(err) {
    this.setState({
      errors: err.message || err,
      isLoading: false,
    })
  }

  handleChange(e) {
    const { formData } = this.state
    const data = {
      ...formData,
      [e.target.name]: e.target.value
    }
    this.setState({ formData: data }, () => {
      this.inputToSave$.next(data)
    })
  }

  render() {
    const { formFields } = this.props
    const { formData, isLoading, showSavedMessage, errors } = this.state

    let saveIndicator;
    if (isLoading) {
      saveIndicator = <Spinner text="Saving..."/>
    } else if (showSavedMessage) {
      saveIndicator = 'Changes saved.'
    } else {
      saveIndicator = ''
    }

    return (
      <>
        {formFields.map(field => (
            <FieldWithExample
              tooltip={field.tooltip}
              placeholder={field.placeholder}
              label={field.label}
              key={field.name}
              name={field.name}
              value={formData[field.name]}
              handleChange={this.handleChange}
            />
          ))}
        {saveIndicator}
        <ErrorList errors={errors.__all__ || []} className="m-0" />
      </>
    )
  }
}

BrandAndProductForm.propTypes = {
  formFields: PropTypes.arrayOf(PropTypes.shape({
    name: PropTypes.string.isRequired,
    label: PropTypes.string.isRequired,
    placeholder: PropTypes.string.isRequired,
  })).isRequired,
  field: PropTypes.string.isRequired,
  formData: PropTypes.objectOf(PropTypes.string).isRequired,
}

function createBrandAndProductForm({ element, ...params }) {
  ReactDOM.render(<BrandAndProductForm {...params} />, element)
}

export { BrandAndProductForm, createBrandAndProductForm }

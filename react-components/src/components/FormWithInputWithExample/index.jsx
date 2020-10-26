import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { Subject } from 'rxjs'
import { debounceTime, delay } from 'rxjs/operators';

import ErrorList from '@src/components/ErrorList'
import { TextArea } from '@src/components/Form/TextArea'
import { Select } from '@src/components/Form/Select'
import Services from '@src/Services'
import Spinner from '@src/components/Spinner/Spinner'
import { analytics } from '@src/Helpers'

export class FormWithInputWithExample extends Component {
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
          .then(() => {
            analytics({
              'event': 'planSectionSaved',
              'sectionTitle': this.props.field
            })
          })
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
      ...e
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
          field.field_type === 'Select' ?
            <Select
              key={field.name}
              label={field.label}
              update={this.handleChange}
              name={field.name}
              options={field.choices}
              selected={field[field.name] ? field.choices.find(x => x.value === formData[field.name]).label: ''}
              example={field.example}
              description={field.description}
              tooltip={field.tooltip}
            />:
            <TextArea
              key={field.name}
              tooltip={field.tooltip}
              label={field.label}
              example={field.example}
              id={field.name}
              value={formData[field.name]}
              description={field.description}
              placeholder={field.placeholder}
              currency={field.currency}
              tag={Number.isInteger(field.placeholder) ? 'number' : 'text'}
              onChange={this.handleChange}
            />
        ))}
        {saveIndicator}
        <ErrorList errors={errors.__all__ || []} className="m-0" />
      </>
    )
  }
}

FormWithInputWithExample.propTypes = {
  formFields: PropTypes.arrayOf(PropTypes.shape({
    name: PropTypes.string.isRequired,
    label: PropTypes.string.isRequired,
    placeholder: PropTypes.string.isRequired,
    field_type: PropTypes.string.isRequired
  })).isRequired,
  field: PropTypes.string.isRequired,
  formData: PropTypes.objectOf(PropTypes.string).isRequired,
}

import React from 'react'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types'

import { Subject } from 'rxjs'
import { debounceTime, tap, mapTo, of } from 'rxjs/operators';

import Field from './Field'
import Services from '../Services'
import Spinner from './Spinner/Spinner'


class BrandAndProductForm extends React.Component {

  constructor(props) {
    super(props)

    this.state = {
      fetchError: '',
      isLoading: false,
      formData: props.formData
    }

    this.inputToSave = new Subject()

    const result = this.inputToSave.pipe(debounceTime(1000 * 2)) // wait 2 secs after user finishes typing to save changes

    result.subscribe(data => {
      this.setState({ isLoading: true }, () => {
        Services.updateExportPlan({ brand_product_details: data })
          .then(this.handleUpdateSuccess)
          .catch(this.handleUpdateError)
      })
    })

    this.bindEvents()
  }

  bindEvents() {
    this.handleChange = this.handleChange.bind(this)
    this.handleUpdateSuccess = this.handleUpdateSuccess.bind(this)
    this.handleUpdateError = this.handleUpdateError.bind(this)
  }

  handleUpdateSuccess() {
    this.setState({
      isLoading: false,
    })
  }

  handleUpdateError(err) {
    this.setState({
      fetchError: err,
      isLoading: false,
    })
  }

  handleChange(e) {
    const prevData = this.state.formData
    const data = {
      ...prevData,
      [e.target.name]: e.target.value
    }
    this.setState({ formData: data }, () => {
      this.inputToSave.next(data)
    })
  }

  render() {
    const { fieldNames } = this.props
    const { formData, isLoading } = this.state

    let saveMessage
    if (isLoading) {
      saveMessage = <Spinner text="Saving..."/>
    } else {
      saveMessage = ''
    }

    return (
    <>
      {
        fieldNames.map(name => (
          <Field
            type="textarea"
            placeholder=""
            key={name}
            label={name}
            name={name}
            disabled={false}
            value={formData[name]}
            handleChange={this.handleChange}
            autofocus
            errors={[]}
          />
        ))
      }
      {saveMessage}
    </>
    )
  }
}

BrandAndProductForm.propTypes = {
  fieldNames: PropTypes.arrayOf(PropTypes.string).isRequired,
  formData: PropTypes.objectOf(PropTypes.string).isRequired,
}

function createBrandAndProductForm({ element, ...params }) {
  ReactDOM.render(<BrandAndProductForm {...params} />, element)
}

export { BrandAndProductForm, createBrandAndProductForm }

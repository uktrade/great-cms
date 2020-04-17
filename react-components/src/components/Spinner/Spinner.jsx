import React from 'react'
import PropTypes from 'prop-types'
import './Spinner.scss'

export default class Spinner extends React.Component {
  constructor(props) {
    super(props)
    const { text } = props

    this.state = {
      text,
    }
  }

  render() {
    const { text } = this.state
    return (
      <div aria-live="polite" role="status">
        {text} <div className="spinner" />
      </div>
    )
  }
}

Spinner.propTypes = {
  text: PropTypes.string,
}

Spinner.defaultProps = {
  text: 'Loading',
}

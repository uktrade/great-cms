import React from 'react'
import PropTypes from 'prop-types'

import { FormGroup } from '../FormGroup'
import EducationalMomentTooltip from '../../EducationalMomentTooltip'

export const TextArea = ({
  error,
  label,
  disabled,
  id,
  placeholder,
  value,
  onChange,
  description,
  tooltip,
  example
}) => (
  <FormGroup
    error={error}
  >
    <>
      <label className='form-label' htmlFor={id}>{label}</label>
      { description && <div className='text-blue-deep-80 p-t-xs p-b-xxs' dangerouslySetInnerHTML={{ __html: description }} /> }
      {
        tooltip &&
        <EducationalMomentTooltip
          heading=''
          description={tooltip}
          id={id}
          type='LEFT'
        />
      }
      {
        example &&
        <dl className='form-group-example bg-blue-deep-10 p-xs m-b-xs'>
          <dt className='body-l-b'>Example</dt>
          <dd className='m-t-xxs body-l' dangerouslySetInnerHTML={{ __html: example }} />
        </dl>
      }
      <textarea
        className='form-control'
        id={id}
        name={id}
        disabled={disabled}
        onChange={(e) => onChange({[id]: e.target.value})}
        placeholder={placeholder}
        value={value}
      />
    </>
  </FormGroup>
)

TextArea.propTypes = {
  error: PropTypes.bool,
  label: PropTypes.string.isRequired,
  disabled: PropTypes.bool,
  id: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  value: PropTypes.string,
  onChange: PropTypes.func.isRequired,
  description: PropTypes.string,
  tooltip: PropTypes.string,
  example: PropTypes.string,
}

TextArea.defaultProps = {
  error: false,
  disabled: false,
  placeholder: '',
  value: '',
  description: '',
  tooltip: '',
  example: ''
}

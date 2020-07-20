import React from 'react'
import PropTypes from 'prop-types'

import { TextArea } from '../Field'
import EducationalMomentTooltip from '../../EducationalMomentTooltip'

const FieldWithExample = ({
  name,
  label,
  placeholder,
  tooltip,
  handleChange,
  value
}) => {

  const labelId = `id_${name}`

  return (
    <div className='field-with-example'>
      <label htmlFor={labelId}>{label}</label>
      { tooltip &&
          <EducationalMomentTooltip
            heading=''
            description={tooltip}
            id={34}
            type='LEFT'
          />
      }
      <dl>
        <dt>Example</dt>
        <dd>{placeholder}</dd>
      </dl>
      <TextArea
        id={labelId}
        disabled={false}
        name={name}
        handleChange={handleChange}
        placeholder='Add some text'
        value={value}
      />
    </div>
  )
}

FieldWithExample.propTypes = {
  name: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  tooltip: PropTypes.string,
  handleChange: PropTypes.func.isRequired,
  value: PropTypes.string.isRequired
}

FieldWithExample.defaultProps = {
  placeholder: '',
  tooltip: ''
}

export default FieldWithExample

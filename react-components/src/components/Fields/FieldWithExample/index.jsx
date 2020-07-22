import React from 'react'
import PropTypes from 'prop-types'

import { TextArea } from '../Field'
import EducationalMomentTooltip from '../../EducationalMomentTooltip'

const FieldWithExample = ({
  name,
  label,
  placeholder,
  example,
  tooltip,
  handleChange,
  value,
  description
}) => {

  const labelId = `id_${name}`

  return (
    <div className='field-with-example'>
      <label htmlFor={labelId}>{label}</label>
      { description && <p>{description}</p> }
      { tooltip &&
          <EducationalMomentTooltip
            heading=''
            description={tooltip}
            id={34}
            type='LEFT'
          />
      }
      {
        example &&
          <dl>
            <dt>Example</dt>
            <dd dangerouslySetInnerHTML={{ __html: example }} />
          </dl>
      }
      <TextArea
        id={labelId}
        disabled={false}
        name={name}
        handleChange={handleChange}
        placeholder={placeholder}
        value={value}
      />
    </div>
  )
}

FieldWithExample.propTypes = {
  name: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  example: PropTypes.string,
  placeholder: PropTypes.string,
  tooltip: PropTypes.string,
  handleChange: PropTypes.func.isRequired,
  value: PropTypes.string.isRequired,
  description: PropTypes.string
}

FieldWithExample.defaultProps = {
  placeholder: 'Add some text',
  tooltip: '',
  example: '',
  description: ''
}

export default FieldWithExample

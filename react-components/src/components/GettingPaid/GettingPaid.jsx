import React, { memo, useState } from 'react'
import PropTypes from 'prop-types'

import { useDebounce } from '@src/components/hooks/useDebounce'
import { TextArea } from '@src/components/Form/TextArea'
import { Select } from '@src/components/Form/Select'
import { getLabel } from '@src/Helpers'
import Services from '@src/Services'

export const GettingPaid = memo(({ formFields, formData, field }) => {
  const [state, setState] = useState(formData)

  const update = (data) => {
    Services.updateExportPlan(data).then(() => {})
  }

  const debounceUpdate = useDebounce(update)

  const onChange = (data) => {
    setState({
      ...state,
      ...data,
    })
    debounceUpdate({ [field]: data })
  }

  return (
    <section className="container p-t-l m-b-l">
      <div className="grid">
        <div className="c-1-4">&nbsp;</div>
        <div className="c-1-1 c-2-3-m c-1-2-xl">
          <h3 className="h-l">Your payment methods</h3>
          <p>
            Foreign buyers may have different expectations about how and when to
            pay for their imports.
          </p>
          <p>
            To avoid uncertainty and disappointment, carefully consider the
            options available.
          </p>
          <div className="form-table bg-blue-deep-10 radius p-h-s p-v-xs">
            <div className="target-market-documents-form">
              {formFields.map(({ field }) => (
                <div className="user-form-group" key={field[0].id}>
                  <Select
                    label={field[0].label}
                    id={field[0].id}
                    name={field[0].name}
                    update={() => {}}
                    options={field[0].options}
                    selected={getLabel(field[0].options, state[field[0].id])}
                    onChange={onChange}
                  />
                  {getLabel(field[0].options, state[field[1].id])}
                  <TextArea
                    onChange={onChange}
                    label={field[1].label}
                    id={field[1].id}
                    value={state[field[1].id]}
                    placeholder={field[1].placeholder}
                  />
                </div>
              ))}
              <p className="body-s text-blue-deep-50 m-b-0">
                Incoterms® and the Incoterms® 2020 logo are trademarks of ICC.
                Use of these trademarks does not imply association with,
                approval of or sponsorship by ICC unless specifically stated
                above. The Incoterms® Rules are protected by copyright owned by
                ICC. Further information on the Incoterm® Rules may be obtained
                from the ICC website iccwbo.org.
              </p>
            </div>
          </div>
        </div>
        <div className="c-1-12-m c-1-4-xl">&nbsp;</div>
      </div>
    </section>
  )
})

GettingPaid.propTypes = {
  formFields: PropTypes.arrayOf(
    PropTypes.objectOf(
      PropTypes.arrayOf(
        PropTypes.objectOf(
          PropTypes.oneOfType([
            PropTypes.string,
            PropTypes.arrayOf(
              PropTypes.shape({
                value: PropTypes.string,
                label: PropTypes.string,
              })
            ),
          ])
        )
      )
    )
  ).isRequired,
  formData: PropTypes.objectOf(
    PropTypes.oneOfType([PropTypes.string, PropTypes.number])
  ).isRequired,
  field: PropTypes.string.isRequired,
}

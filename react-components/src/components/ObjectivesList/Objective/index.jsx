import React, { memo, forwardRef } from 'react'
import PropTypes from 'prop-types'

import { TextArea } from '@src/components/Form/TextArea'
import { Input } from '@src/components/Form/Input'
import { ConfirmModal } from '@src/components/ConfirmModal/ConfirmModal'
import { objectHasValue } from '@src/Helpers'
import ErrorList from '../../ErrorList'
import { Select } from '@src/components/Form/Select'

const MONTHS = [
  'January',
  'February',
  'March',
  'April',
  'May',
  'June',
  'July',
  'August',
  'September',
  'October',
  'November',
  'December',
]

const fwRefObjective = forwardRef((props, ref) => {
  const { handleChange, deleteObjective, number, id, errors, data } = props

  const selectMonths = MONTHS.map((label, i) => ({
    label,
    value: `${i + 1}`,
  }))

  const onChange = (item) => {
    handleChange({
      ...data,
      ...item,
    })
  }

  const onDelete = () => {
    deleteObjective(data.pk)
  }

  const {
    companyexportplan,
    start_month,
    start_year,
    end_month,
    end_year,
    pk,
    ...fields
  } = data

  return (
    <fieldset id={`objective-${number}`} ref={ref} tabIndex="-1">
      <legend className="visually-hidden">{`Objective ${number}`}</legend>
      <div className="costs bg-blue-deep-10 m-b-s">
        <div className="costs__option costs__option--border" tabIndex="-1">
          <TextArea
            id="description"
            placeholder="Add some text"
            label={`Objective ${number}`}
            value={data.description}
            onChange={onChange}
            errors={[]}
            formGroupClassName="m-b-0"
          />
        </div>
        <div className="costs__option costs__option--border">
          <fieldset>
            <legend className="m-b-xs">Start objective in:</legend>
            <div className="inputgroup">
              <div className="inputgroup__input inputgroup__input--month">
                <Select
                  label="Month"
                  id={`start-month-${id}`}
                  name={`start-month-${id}`}
                  update={onChange}
                  options={selectMonths}
                  selected={data.start_month}
                />
              </div>
              <div className="inputgroup__input">
                <Input
                  label="Year"
                  id={`start-year-${id}`}
                  value={data.start_year}
                  onChange={onChange}
                />
              </div>
            </div>
          </fieldset>
          <fieldset>
            <legend className="m-b-xs">Complete by:</legend>
            <div className="inputgroup">
              <div className="inputgroup__input inputgroup__input--month">
                <Select
                  label="Month"
                  id={`end-month-${id}`}
                  name={`end-month-${id}`}
                  update={onChange}
                  options={selectMonths}
                  selected={data.end_month}
                />
              </div>
              <div className="inputgroup__input inputgroup__input--month">
                <Input
                  label="Year"
                  id={`end-year-${id}`}
                  value={data.end_year}
                  onChange={onChange}
                />
              </div>
            </div>
          </fieldset>
        </div>
        <div className="costs__option costs__option--border">
          <Input
            id={`owner-${id}`}
            placeholder="Add an owner"
            label="Owner"
            value={data.owner}
            onChange={(item) => onChange({ owner: item[`owner-${id}`] })}
            errors={[]}
            formGroupClassName="m-b-0"
          />
        </div>
        <div className="costs__option costs__option--border">
          <TextArea
            id="planned_reviews"
            placeholder="Add some text"
            label="Planned reviews"
            value={data.planned_reviews}
            onChange={onChange}
            errors={[]}
            formGroupClassName="m-b-0"
          />
        </div>
        <div className="costs__option costs__option--border text-center">
          <ConfirmModal
            deleteItem={onDelete}
            hasData={objectHasValue(fields)}
          />
        </div>
      </div>
      <ErrorList errors={errors.__all__ || []} />
    </fieldset>
  )
})

export const Objective = memo(fwRefObjective)

Objective.propTypes = {
  handleChange: PropTypes.func.isRequired,
  deleteObjective: PropTypes.func.isRequired,
  number: PropTypes.number.isRequired,
  id: PropTypes.number.isRequired,
  errors: PropTypes.shape({
    __all__: PropTypes.arrayOf(PropTypes.string.isRequired),
  }),
  data: PropTypes.shape({
    description: PropTypes.string,
    owner: PropTypes.string,
    planned_reviews: PropTypes.string,
    start_month: PropTypes.string,
    start_year: PropTypes.string,
    end_month: PropTypes.string,
    end_year: PropTypes.string,
    companyexportplan: PropTypes.number.isRequired,
    pk: PropTypes.number.isRequired,
  }).isRequired,
}

Objective.defaultProps = {
  errors: { __all__: [] },
}

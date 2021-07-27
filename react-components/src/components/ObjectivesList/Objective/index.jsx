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
                  id="start_month"
                  name="start_month"
                  update={onChange}
                  options={selectMonths}
                  selected={`${data.start_month}`}
                />
              </div>
              <div className="inputgroup__input inputgroup__input--year">
                <Input
                  label="Year"
                  id="start_year"
                  type="number"
                  value={`${data.start_year || ''}`}
                  onChange={onChange}
                  size={4}
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
                  id="end_month"
                  name="end_month"
                  update={onChange}
                  options={selectMonths}
                  selected={`${data.end_month}`}
                />
              </div>
              <div className="inputgroup__input inputgroup__input--year">
                <Input
                  label="Year"
                  id="end_year"
                  type="number"
                  value={`${data.end_year || ''}`}
                  onChange={onChange}
                  size={4}
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
    start_month: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    start_year: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    end_month: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    end_year: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    companyexportplan: PropTypes.number.isRequired,
    pk: PropTypes.number.isRequired,
  }).isRequired,
}

Objective.defaultProps = {
  errors: { __all__: [] },
}

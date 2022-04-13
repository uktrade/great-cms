import React, { memo, forwardRef } from 'react'
import PropTypes from 'prop-types'

import { TextArea } from '@src/components/Form/TextArea'
import { Input } from '@src/components/Form/Input'
import { ConfirmModal } from '@src/components/ConfirmModal/ConfirmModal'
import { objectHasValue } from '@src/Helpers'
import ErrorList from '../../ErrorList'
import { MonthYearInput } from '../../Form/MonthYearInput'

const fwRefObjective = forwardRef((props, ref) => {
  const { handleChange, deleteObjective, number, id, errors, data, example } =
    props

  const onChange = (item) => {
    handleChange({
      ...data,
      ...item,
    })
  }

  const onDelete = () => {
    deleteObjective(data.pk)
  }

  const { companyexportplan, end_month, end_year, pk, ...fields } = data

  return (
    <fieldset id={`objective-${number}`} ref={ref} tabIndex="-1">
      <legend className="visually-hidden">{`Objective ${number}`}</legend>
      <div className="costs bg-blue-deep-10 m-b-s">
        <div className="costs__option costs__option--border" tabIndex="-1">
          <TextArea
            id={`${number}`}
            name="description"
            placeholder="Add some text"
            label={`Objective ${number}`}
            value={data.description}
            onChange={onChange}
            errors={[]}
            formGroupClassName="m-b-0"
            example={example}
          />
        </div>
        <div className="costs__option costs__option--border">
          <MonthYearInput
            label="To be completed by:"
            monthName="end_month"
            monthValue={data.end_month}
            yearName="end_year"
            yearValue={data.end_year}
            onChange={onChange}
            className="m-t-s"
          />
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
    end_month: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    end_year: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    companyexportplan: PropTypes.number,
    pk: PropTypes.number,
  }).isRequired,
  example: PropTypes.shape({
    content: PropTypes.string,
  }),
}

Objective.defaultProps = {
  errors: { __all__: [] },
  example: {},
}

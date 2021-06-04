import React, { memo, forwardRef } from 'react'
import PropTypes from 'prop-types'

import { TextArea } from '@src/components/Form/TextArea'
import { Input } from '@src/components/Form/Input'
import { ConfirmModal } from '@src/components/ConfirmModal/ConfirmModal'
import { objectHasValue } from '@src/Helpers'
import ErrorList from '../../ErrorList'



const fwObjective = forwardRef(
  (props, ref) => {
    const { handleChange, deleteObjective, number, id, errors, data } = props
    const onChange = (item) => {
      handleChange({
        ...data,
        ...item,
      })
    }

    const onDelete = () => {
      deleteObjective(data.pk)
    }

    const { companyexportplan, start_date, end_date, pk, ...fields } = data

    return (
      <fieldset id={`objective-${number}`} ref={ref} tabIndex="-1">
      <legend className="visually-hidden">{`Objective ${number}`}</legend>
        <div className="bg-blue-deep-10 radius p-h-s">
          <div className="grid" tabIndex="-1">
            <div className="c-full">
              <TextArea
                id="description"
                placeholder="Add some text"
                label={`Objective ${number}`}
                value={data.description}
                onChange={onChange}
                errors={[]}
              />
              <hr className="hr hr--light" />
            </div>
            <div className="grid">
              <div className="c-1-2">
                <Input
                  id="start_date"
                  type="date"
                  label="Start date"
                  maxDate={data.end_date}
                  value={data.start_date}
                  onChange={onChange}
                  errors={[]}
                />
              </div>
              <div className="c-1-2">
                <Input
                  id="end_date"
                  type="date"
                  label="End date"
                  minDate={data.start_date}
                  value={data.end_date}
                  onChange={onChange}
                  errors={[]}
                />
              </div>
            </div>
            <div className="c-full">
              <hr className="hr hr--light" />
              <Input
                id={`owner-${id}`}
                placeholder="Add an owner"
                label="Owner"
                value={data.owner}
                onChange={(item) => onChange({ owner: item[`owner-${id}`] })}
                errors={[]}
              />
            </div>
            <div className="c-full">
              <TextArea
                id="planned_reviews"
                placeholder="Add some text"
                label="Planned reviews"
                value={data.planned_reviews}
                onChange={onChange}
                errors={[]}
              />
            </div>
          </div>
          <div className="text-center">
            <hr className="hr hr--light" />
            <ConfirmModal
              deleteItem={onDelete}
              hasData={objectHasValue(fields)}
            />
          </div>
        </div>
        <ErrorList errors={errors.__all__ || []} />
        <hr />
      </fieldset>
    )
  }
)

export const Objective = memo(fwObjective)

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
    start_date: PropTypes.string,
    end_date: PropTypes.string,
    companyexportplan: PropTypes.number.isRequired,
    pk: PropTypes.number.isRequired,
  }).isRequired,
}

Objective.defaultProps = {
  errors: { __all__: [] },
}

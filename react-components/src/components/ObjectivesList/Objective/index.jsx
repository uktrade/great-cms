import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { TextArea } from '@src/components/Form/TextArea'
import { Input } from '@src/components/Form/Input'
import ErrorList from '../../ErrorList'

export const Objective = memo(
  ({ handleChange, deleteObjective, number, id, errors, data }) => {
    const onChange = (item) => {
      handleChange({
        ...data,
        ...item,
      })
    }

    const ISONow = new Date().toISOString().slice(0, 10)

    const onDelete = () => {
      deleteObjective(data.pk)
    }

    return (
      <>
        <div className="bg-blue-deep-10 radius p-h-s">
          <div className="grid">
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
                  minDate={ISONow}
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
              <hr className="hr hr--light" />
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
            <button
              type="button"
              className="button--only-icon button button--small button--delete bg-white m-v-xs"
              onClick={onDelete}
            >
              <i className="fas fa-trash-alt" />
            </button>
          </div>
        </div>
        <ErrorList errors={errors.__all__ || []} />
        <hr />
      </>
    )
  }
)

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

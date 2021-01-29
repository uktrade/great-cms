import React, { memo, useState } from 'react'
import PropTypes from 'prop-types'

import { Input } from '@src/components/Form/Input'
import { Select } from '@src/components/Form/Select'
import { getLabel, getValue } from '@src/Helpers'
import { LessonLearn } from '@src/components/LessonLearn'

export const GrossPrice = memo(
  ({
    country,
    currency,
    GrossPriceUnit,
    profitPerUnit,
    potentialPerUnit,
    update,
    input,
    select,
    lesson,
  }) => {
    const [toggleLesson, setToggleLesson] = useState(false)
    const hasLesson = Object.keys(lesson).length > 0

    return (
      <>
        {hasLesson && (
          <>
            <button
              className="button-lesson button button--small button--tertiary m-r-xxs m-b-xs"
              type="button"
              onClick={() => {
                setToggleLesson(!toggleLesson)
              }}
            >
              <i
                className={`fas fa-chevron-${
                  toggleLesson ? 'up' : 'down'
                } m-r-xxs`}
              />
              Lesson
            </button>
            <LessonLearn show={toggleLesson} {...lesson} />
          </>
        )}
        <div className="bg-white radius p-xs c-full m-b-s gross-price">
          <div className="">
            <i className="fas fa-tag text-blue-deep-60 fa-lg" />
            <p className="m-t-xxs m-b-0">
              Gross price per unit for the {country}
            </p>
            <h3 className="h-s p-t-0 p-b-0">
              {currency} {GrossPriceUnit}
            </h3>
          </div>
          <hr className="hr--light m-v-xs" />
          <div className="">
            <p className="m-t-xxs m-b-0">
              Gross price per unit in invoicing currency
            </p>
            <div className="grid m-t-xs">
              <div className="w-full">
                <div className="c-1-6 m-r-xs">
                  <Select
                    label={select.label}
                    id={select.id}
                    update={(item) => {
                      const postData = input.field({
                        unit: item[select.name],
                        value: input.value,
                      })
                      update(
                        {
                          [select.id]: getLabel(
                            select.options,
                            item[select.name]
                          ),
                        },
                        postData
                      )
                    }}
                    name={select.name}
                    options={select.options}
                    hideLabel
                    placeholder={select.placeholder}
                    selected={select.value}
                  />
                </div>
                <div className="c-1-3">
                  <Input
                    onChange={(x) => {
                      const postData = input.field({
                        unit: getValue(select.options, select.value),
                        value: x[input.id],
                      })
                      update(x, postData)
                    }}
                    label={input.label}
                    id={input.id}
                    hideLabel
                    type={input.type}
                    value={input.value}
                    placeholder={input.placeholder}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="grid">
          <div className="c-1-2 m-b-s">
            <div className="bg-white radius p-xs">
              <i className="fas fa-pound-sign text-blue-deep-60 fa-lg" />
              <p className="m-t-xxs m-b-0">Your profit per unit</p>
              <h3 className="h-s p-t-0 p-b-0">
                {currency} {profitPerUnit}
              </h3>
            </div>
          </div>
          <div className="c-1-2 m-b-s">
            <div className="bg-white radius p-xs">
              <i className="fas fa-pound-sign text-blue-deep-60 fa-lg" />
              <p className="m-t-xxs m-b-0">Your potential per unit</p>
              <h3 className="h-s p-t-0 p-b-0">
                {currency} {potentialPerUnit}
              </h3>
            </div>
          </div>
        </div>
      </>
    )
  }
)

GrossPrice.propTypes = {
  country: PropTypes.string.isRequired,
  currency: PropTypes.string.isRequired,
  GrossPriceUnit: PropTypes.string.isRequired,
  profitPerUnit: PropTypes.string.isRequired,
  potentialPerUnit: PropTypes.string.isRequired,
  update: PropTypes.func.isRequired,
  lesson: PropTypes.shape({
    url: PropTypes.string,
    title: PropTypes.string,
    category: PropTypes.string,
    duration: PropTypes.string,
  }).isRequired,
  input: PropTypes.shape({
    label: PropTypes.string,
    id: PropTypes.string,
    value: PropTypes.string,
    placeholder: PropTypes.string,
    type: PropTypes.string,
    field: PropTypes.func,
  }).isRequired,
  select: PropTypes.shape({
    label: PropTypes.string,
    id: PropTypes.string,
    name: PropTypes.string,
    value: PropTypes.string,
    placeholder: PropTypes.string,
    options: PropTypes.arrayOf(
      PropTypes.shape({
        value: PropTypes.string,
        label: PropTypes.string,
      })
    ).isRequired,
  }).isRequired,
}

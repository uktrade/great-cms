import React, { useState, useRef, useEffect, memo } from 'react'
import PropTypes from 'prop-types'
import { useOnOutsideClick } from '@src/components/hooks/useOnOutsideClick'
import { Item } from '@src/components/Form/Select/Item'
import { FormGroup } from '@src/components/Form/FormGroup'

const ENTER_KEY_CODE = 13
const DOWN_ARROW_KEY_CODE = 40
const UP_ARROW_KEY_CODE = 38
const ESCAPE_KEY_CODE = 27

export const Select = memo(
  ({
    label,
    update,
    name,
    selected,
    options,
    description,
    tooltip,
    example,
    hideLabel,
    lesson,
    placeholder,
    id,
    className,
    multiSelect,
    autoComplete,
    inputChange,
    inputValue,
  }) => {
    const [input, setInput] = useState(selected)
    const [isOpen, setIsOpen] = useState(false)
    const liRef = useRef([])
    const [element] = useOnOutsideClick(() => setIsOpen(false), isOpen)

    useEffect(() => {
      setInput(selected)
    }, [selected])

    const optionByValue = (value) => {
      return (
        Object.values(Array.isArray(options) ? { x: options } : options).reduce(
          (running, section) => {
            return running || section.find((option) => option.value === value)
          },
          null
        ) || {}
      )
    }
    const selectedItem = () => {
      if (!input || input.length <= 0) return placeholder
      if (multiSelect) {
        return input.map((item) => (
          <button
            className="tag tag--icon tag--secondary tag--small m-r-xs"
            type="button"
            key={item}
            onClick={() => {
              const items = input.filter((x) => x !== item)
              setInput(items)
              update({ [name]: items })
            }}
          >
            {options.find((option) => item === option.value).label}{' '}
            <i className="fas fa-times-circle" />
          </button>
        ))
      }
      return optionByValue(input).label || placeholder
    }

    const selectOption = (item) => {
      if (multiSelect) {
        const items = [...new Set([...input, item.value])]
        setInput(items)
        update({ [name]: items })
      } else {
        if (!item.isError) {
          setInput(item.value)
          setIsOpen(false)
          update({ [name]: item.value })
        }
      }
    }

    const focusNext = (e, i, item, subSection = null) => {
      const next = i + 1
      const prev = i - 1
      const section = subSection + 1
      const currentElement = element.current.children[section].children[0]

      switch (e.keyCode) {
        case ENTER_KEY_CODE:
          selectOption(item)
          break
        case DOWN_ARROW_KEY_CODE:
          if (subSection !== null) {
            const nextSection = element.current.children[section + 1]
            const nextElement = currentElement.children[next]
              ? currentElement.children[next]
              : nextSection.children[0].children[1]
            nextElement.focus()
          } else if (next < liRef.current.length) liRef.current[next].focus()
          break
        case UP_ARROW_KEY_CODE:
          if (subSection !== null) {
            const nextSection = element.current.children[section - 1]
            const nextElement = currentElement.children[prev - 1]
              ? currentElement.children[prev]
              : nextSection.children[0].children[
                  nextSection.children[0].children.length - 1
                ]
            nextElement.focus()
          } else if (prev >= 0) liRef.current[prev].focus()
          break
        case ESCAPE_KEY_CODE:
          setIsOpen(false)
          break
        default:
          break
      }
    }

    const toggle = (e) => {
      const firstElement = element.current.children[1]
      switch (e.keyCode) {
        case DOWN_ARROW_KEY_CODE:
          setIsOpen(true)
          if (
            firstElement.children[0] &&
            firstElement.children[0].nodeName === 'UL'
          ) {
            firstElement.children[0].children[1].focus()
          } else {
            firstElement.focus()
          }
          break
        case ESCAPE_KEY_CODE:
          setIsOpen(false)
          break
        default:
          break
      }
    }

    return (
      <div className={`select ${className}`}>
        <FormGroup
          label={label}
          id={id || label}
          name={label}
          readOnly
          description={description}
          tooltip={tooltip}
          example={example}
          lesson={lesson}
          tabIndex="-1"
          hideLabel={hideLabel}
        >
          <>
            <div
              className={`select__button text-blue-deep-20 button--toggle ${
                isOpen ? 'select__button--close' : ''
              }`}
              role="region"
              aria-label={label}
            >
              <button
                aria-haspopup="listbox"
                tabIndex="0"
                onKeyDown={toggle}
                type="button"
                onClick={() => setIsOpen(!isOpen)}
                className={`f-r button--toggle ${
                  isOpen ? 'button--toggled' : ''
                }`}
              >
                <i
                  className={`fas ${
                    isOpen ? 'fa-times-circle text-blue-deep-60' : 'fa-sort'
                  }`}
                />
              </button>
            </div>
            <div className="select__placeholder text-blue-deep-60 bg-white radius">
              <div
                className="select__placeholder--input"
                onClick={() => setIsOpen(!isOpen)}
              >
                {autoComplete ? (
                  <input
                    role="combobox"
                    className="form-control"
                    placeholder={placeholder}
                    value={inputValue}
                    onChange={inputChange}
                  />
                ) : (
                  ''
                )}
              </div>
              <div className="select__placeholder--value">{selectedItem()}</div>
              <ul
                role="listbox"
                className={`select__list m-t-0 body-l bg-white radius ${
                  isOpen ? 'select__list--open' : 'hidden'
                }`}
                aria-expanded={isOpen}
                ref={element}
              >
                {!autoComplete ? <li>{placeholder}</li> : ''}

                {Array.isArray(options)
                  ? options.map((item, i) => (
                      <Item
                        isDisabled={
                          Array.isArray(input)
                            ? input.includes(item.value)
                            : input === item.value
                        }
                        key={item.value}
                        onClick={() => selectOption(item)}
                        onKeyDown={(e) => focusNext(e, i, item)}
                        selected={item.value === input}
                        label={item.label}
                        forwardedRef={(el) => (liRef.current[i] = el)}
                        isError={item.isError}
                      />
                    ))
                  : Object.keys(options).map((category, i) => (
                      <li className="sub-section" key={category}>
                        <ul className="m-0">
                          <li className="body-m-b">{category}</li>
                          {options[category].map((li, index) => (
                            <Item
                              key={li.value}
                              onClick={() => selectOption(li)}
                              onKeyDown={(e) => focusNext(e, index + 1, li, i)}
                              selected={li.value === input}
                              label={li.label}
                              forwardedRef={(el) => (liRef.current[index] = el)}
                            >
                              {li.label}
                            </Item>
                          ))}
                        </ul>
                      </li>
                    ))}
              </ul>
            </div>
          </>
        </FormGroup>
      </div>
    )
  }
)

Select.propTypes = {
  label: PropTypes.string.isRequired,
  update: PropTypes.func.isRequired,
  name: PropTypes.string.isRequired,
  selected: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.arrayOf(PropTypes.string),
  ]),
  options: PropTypes.oneOfType([
    PropTypes.objectOf(
      PropTypes.arrayOf(
        PropTypes.shape({
          value: PropTypes.string,
          label: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
        })
      )
    ),
    PropTypes.arrayOf(
      PropTypes.shape({
        value: PropTypes.string,
        label: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
      })
    ),
  ]).isRequired,
  description: PropTypes.string,
  tooltip: PropTypes.objectOf(PropTypes.string),
  example: PropTypes.shape({
    buttonTitle: PropTypes.string,
    header: PropTypes.string,
    content: PropTypes.string,
  }),
  lesson: PropTypes.shape({
    url: PropTypes.string,
    title: PropTypes.string,
    category: PropTypes.string,
    duration: PropTypes.string,
  }),
  hideLabel: PropTypes.bool,
  placeholder: PropTypes.string,
  id: PropTypes.string,
  className: PropTypes.string,
  multiSelect: PropTypes.bool,
  autoComplete: PropTypes.bool,
  inputChange: PropTypes.func,
  inputValue: PropTypes.string,
}

Select.defaultProps = {
  selected: '',
  description: '',
  tooltip: {},
  example: {},
  hideLabel: false,
  lesson: {},
  placeholder: 'Select one',
  id: '',
  className: 'm-b-l',
  multiSelect: false,
  autoComplete: false,
  inputChange: null,
  inputValue: null,
}

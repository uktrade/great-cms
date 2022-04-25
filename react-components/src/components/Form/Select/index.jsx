import React, { useState, useRef, useEffect, memo } from 'react'
import PropTypes from 'prop-types'
import { useOnOutsideClick } from '@src/components/hooks/useOnOutsideClick'
import { Item } from '@src/components/Form/Select/Item'
import { FormGroup } from '@src/components/Form/FormGroup'

const ENTER_KEY_CODE = 13
const DOWN_ARROW_KEY_CODE = 40
const UP_ARROW_KEY_CODE = 38
const ESCAPE_KEY_CODE = 27
const SPACE_KEY_CODE = 32

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
    const [input, setInput] = useState(selected || [])
    const [isOpen, setIsOpen] = useState(false)
    const liRef = useRef([])
    const expander = useRef()
    const outer = useRef()
    const placeHolder = useRef()
    const ulOptions = useRef()

    useEffect(() => {
      setInput(selected)
    }, [selected])

    useEffect(() => {
      // automatically open autocomplete
      if (autoComplete) {
        setIsOpen(!!(options && options.length))
      }
    }, [options])

    useOnOutsideClick(outer, () => {
      setIsOpen(false)
    })

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
      if (multiSelect && Array.isArray(input)) {
        return (
          <ul className="select__selected">
            {input.map((item) => (
              <li key={item}>
                <button
                  className="tag tag--icon tag--secondary tag--small m-r-xs"
                  type="button"
                  onClick={(e) => {
                    e.preventDefault()
                    e.stopPropagation()
                    const items = input.filter((x) => x !== item)
                    setInput(items)
                    update({ [name]: items })
                    placeHolder.current.focus()
                  }}
                >
                  {options.find((option) => item === option.value).label}{' '}
                  <i className="fas fa-times-circle" />
                </button>
              </li>
            ))}
          </ul>
        )
      }
      return optionByValue(input).label || placeholder
    }

    const selectOption = (item) => {
      if (multiSelect) {
        const items = [...new Set([...input, item.value])]
        setInput(items)
        update({ [name]: items })
        placeHolder.current.focus()
      } else if (!item.isError) {
        setInput(item.value)
        setIsOpen(false)
        update({ [name]: item.value })
      }
    }

    const focusNext = (inc, target) => {
      const items = Array.from(
        ulOptions.current.querySelectorAll('li.select__list--item')
      )
      const selectedIndex = items.findIndex((item) => item === target) + inc
      const nextItem = items[selectedIndex]
      setIsOpen(!!nextItem)
      if (nextItem) {
        nextItem.focus()
      } else {
        placeHolder.current.focus()
      }
    }

    const keyHandler = (e, item) => {
      let keyFound = true
      switch (e.keyCode) {
        case ENTER_KEY_CODE:
        case SPACE_KEY_CODE:
          if (e.target.closest('.tag')) {
            keyFound = false
          } else if (item) {
            selectOption(item)
          } else if (autoComplete) {
            keyFound = false
          } else {
            setIsOpen(!isOpen)
          }
          break
        case DOWN_ARROW_KEY_CODE:
          focusNext(1, e.target)
          break
        case UP_ARROW_KEY_CODE:
          focusNext(-1, e.target)
          break
        case ESCAPE_KEY_CODE:
          setIsOpen(false)
          break
        default:
          keyFound = false
          break
      }
      if (keyFound) {
        e.preventDefault()
        e.stopPropagation()
      }
    }

    return (
      <div
        className={`select ${className} ${autoComplete ? 'autocomplete' : ''}`}
        ref={outer}
      >
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
            {' '}
            <div
              className="select__placeholder text-blue-deep-60 bg-white radius"
              ref={placeHolder}
              tabIndex={autoComplete ? -1 : 0}
              onKeyDown={keyHandler}
              onFocus={(e) => {
                if (autoComplete && e.target === placeHolder.current) {
                  placeHolder.current.querySelector('input').focus()
                }
              }}
              onClick={() => setIsOpen(!isOpen)}
              aria-haspopup="listbox"
              role="button"
            >
              {!autoComplete ? (
                <div
                  className={`select__button text-blue-deep-20 ${
                    isOpen ? 'select__button--close' : ''
                  }`}
                >
                  <i className={`fas ${'fa-chevron-down'}`} />
                </div>
              ) : (
                ''
              )}
              <div className="select__placeholder--input">
                {autoComplete ? (
                  <input
                    role="combobox"
                    aria-controls="listbox"
                    aria-expanded={isOpen}
                    className="form-control"
                    placeholder={placeholder}
                    value={inputValue}
                    onChange={inputChange}
                    onKeyDown={keyHandler}
                    aria-label={label}
                  />
                ) : (
                  ''
                )}
              </div>
              {!autoComplete ? (
                <div className="select__placeholder--value" aria-label={label}>
                  {selectedItem()}
                </div>
              ) : (
                ''
              )}
              <div
                role="listbox"
                className={`select__list body-l bg-white radius ${
                  isOpen ? 'select__list--open' : ''
                } `}
                aria-expanded={isOpen}
                ref={expander}
              >
                <ul className="option-list" ref={ulOptions}>
                  {Array.isArray(options)
                    ? options.map((item, i) =>
                        multiSelect && input.includes(item.value) ? (
                          ''
                        ) : (
                          <li
                            key={item.value}
                            tabIndex={isOpen ? 0 : -1}
                            role="option"
                            className={`select__list--item ${
                              !autoComplete && Array.isArray(input)
                                ? input.includes(item.value)
                                : input === item.value
                                ? 'text-black-50'
                                : ''
                            }`}
                            onClick={() => selectOption(item)}
                            onKeyDown={(e) => keyHandler(e, item)}
                            aria-selected={item.value === input}
                            ref={(el) => {
                              liRef.current[i] = el
                            }}
                          >
                            {item.label}
                          </li>
                        )
                      )
                    : Object.keys(options).map((category, i) => (
                        <li className="sub-section" key={category}>
                          <ul className="m-0">
                            <li className="body-m-b">{category}</li>
                            {options[category].map((li) => (
                              <Item
                                key={li.value}
                                onClick={() => selectOption(li)}
                                onKeyDown={(e) => keyHandler(e, li)}
                                selected={li.value === input}
                                label={li.label}
                                forwardedRef={(el) => {
                                  liRef.current[i] = el
                                }}
                              >
                                {li.label}
                              </Item>
                            ))}
                          </ul>
                        </li>
                      ))}
                </ul>
              </div>
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
  tooltip: PropTypes.shape({
    title: PropTypes.string,
    content: PropTypes.string,
  }),
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
  tooltip: null,
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

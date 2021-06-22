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

    const openDuration = 250

    useEffect(() => {
      setInput(selected)
    }, [selected])

    const setOpen = (state, onComplete) => {
      if (state !== isOpen) {
        if (!state) placeHolder.current.focus()
        const elStyle = expander.current.style
        elStyle.transition = `height ${openDuration}ms`
        elStyle.display = 'block'
        elStyle.height = null
        const height = expander.current.offsetHeight
        elStyle.height = state ? '8px' : `${height}px`
        window.setTimeout(() => {
          elStyle.height = state ? `${height}px` : '8px'
          setIsOpen(state)
        }, 0)
        window.setTimeout(() => {
          setIsOpen(state)
          elStyle.height = null
          elStyle.display = state ? 'block' : 'none'
          if (onComplete) onComplete()
        }, openDuration)
      } else if (onComplete) {
        onComplete()
      }
    }

    useEffect(() => {
      // automatically open autocomplete
      if (autoComplete) {
        setOpen(!!(options && options.length))
      }
    }, [options])

    useOnOutsideClick(outer, () => {
      setOpen(false)
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
        return input.map((item) => (
          <button
            className="tag tag--icon tag--secondary tag--small m-r-xs"
            type="button"
            key={item}
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
        ))
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
        setOpen(false)
        update({ [name]: item.value })
      }
    }

    const focusNext = (inc, target) => {
      const items = Array.from(
        ulOptions.current.querySelectorAll('li.select__list--item')
      )
      const selectedIndex = items.findIndex((item) => item === target) + inc
      const nextItem = items[selectedIndex]
      setOpen(selectedIndex >= 0, () => {
        if (nextItem || selectedIndex < 0) {
          ;(nextItem || placeHolder.current).focus()
        }
      })
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
            setOpen(!isOpen)
          }
          break
        case DOWN_ARROW_KEY_CODE:
          focusNext(1, e.target)
          break
        case UP_ARROW_KEY_CODE:
          focusNext(-1, e.target)
          break
        case ESCAPE_KEY_CODE:
          setOpen(false)
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
              onClick={() => setOpen(!isOpen)}
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
                          <Item
                            isDisabled={
                              !autoComplete && Array.isArray(input)
                                ? input.includes(item.value)
                                : input === item.value
                            }
                            key={item.value}
                            onClick={() => selectOption(item)}
                            onKeyDown={(e) => keyHandler(e, item)}
                            selected={item.value === input}
                            label={item.label}
                            forwardedRef={(el) => {
                              liRef.current[i] = el
                            }}
                            isError={item.isError}
                          />
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

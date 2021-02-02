import React, { useState, useRef, useEffect } from 'react'
import PropTypes from 'prop-types'
import { useOnOutsideClick } from '@src/components/hooks/useOnOutsideClick'
import { useNoScroll } from '@src/components/hooks/useNoScroll'
import { Item } from '@src/components/Form/Select/Item'
import { FormGroup } from '@src/components/Form/FormGroup'

const ENTER_KEY_CODE = 13
const DOWN_ARROW_KEY_CODE = 40
const UP_ARROW_KEY_CODE = 38
const ESCAPE_KEY_CODE = 27

export const Select = ({
  label,
  update,
  name,
  selected,
  options,
  description,
  tooltip,
  example,
  hideLabel,
  placeholder,
  id,
  className,
  multiSelect,
}) => {
  const [input, setInput] = useState(selected)
  const [isOpen, setIsOpen] = useState(false)
  const liRef = useRef([])
  const [element] = useOnOutsideClick(() => setIsOpen(false))
  useNoScroll(isOpen)

  useEffect(() => {
    setInput(selected)
  }, [selected])

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
          {item} <i className="fas fa-times-circle" />
        </button>
      ))
    }
    return input
  }

  const selectOption = (item) => {
    if (multiSelect) {
      const items = [...new Set([...input, item.label])]
      setInput(items)
      update({ [name]: items })
    } else {
      setInput(item.label)
      setIsOpen(false)
      update({ [name]: item.value })
    }
  }

  const focusNext = (e, i, item, subSection = null) => {
    const next = i + 1
    const prev = i - 1
    const section = subSection + 1
    const currentElement = element.current.children[section]

    switch (e.keyCode) {
      case ENTER_KEY_CODE:
        selectOption(item)
        break
      case DOWN_ARROW_KEY_CODE:
        if (subSection !== null) {
          const nextSection = element.current.children[section + 1]
          const nextElement = currentElement.children[next]
            ? currentElement.children[next]
            : nextSection.children[1]
          nextElement.focus()
        } else if (next < liRef.current.length) liRef.current[next].focus()
        break
      case UP_ARROW_KEY_CODE:
        if (subSection !== null) {
          const nextSection = element.current.children[section - 1]
          const nextElement = currentElement.children[prev - 1]
            ? currentElement.children[prev]
            : nextSection.children[nextSection.children.length - 1]
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
        if (firstElement.nodeName === 'UL') {
          firstElement.children[1].focus()
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
        tabIndex="-1"
        hideLabel={hideLabel}
      />
      <div
        className={`select__button text-blue-deep-20 button--toggle ${
          isOpen ? 'select__button--close' : ''
        }`}
      >
        <button
          aria-haspopup="listbox"
          tabIndex="0"
          onKeyDown={toggle}
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className="f-r button--toggle"
        >
          <i
            className={`fas button--toggle ${
              isOpen ? 'fa-times-circle text-blue-deep-60' : 'fa-sort'
            }`}
          />
        </button>
      </div>
      <div
        className={`select__placeholder bg-white radius ${
          !isOpen ? '' : 'hidden'
        }`}
      >
        {selectedItem()}
      </div>
      <ul
        role="listbox"
        className={`select__list body-l bg-white radius ${
          isOpen ? '' : 'hidden'
        }`}
        aria-expanded={isOpen}
        ref={element}
      >
        <li>{selectedItem()}</li>

        {Array.isArray(options)
          ? options.map((item, i) => (
              <Item
                isDisabled={input.includes(item.label)}
                key={item.label}
                onClick={() => selectOption(item)}
                onKeyDown={(e) => focusNext(e, i, item)}
                selected={item.label === input}
                label={item.label}
                forwardedRef={(el) => (liRef.current[i] = el)}
              />
            ))
          : Object.keys(options).map((category, i) => (
              <ul className="m-0" key={category}>
                <li className="body-m-b">{category}</li>
                {options[category].map((li, index) => (
                  <Item
                    key={li.label}
                    onClick={() => selectOption(li)}
                    onKeyDown={(e) => focusNext(e, index + 1, li, i)}
                    selected={li.label === input}
                    label={li.label}
                    forwardedRef={(el) => (liRef.current[index] = el)}
                  >
                    {li.label}
                  </Item>
                ))}
              </ul>
            ))}
      </ul>
    </div>
  )
}

Select.propTypes = {
  label: PropTypes.string.isRequired,
  update: PropTypes.func.isRequired,
  name: PropTypes.string.isRequired,
  selected: PropTypes.string,
  options: PropTypes.oneOfType([
    PropTypes.objectOf(
      PropTypes.arrayOf(
        PropTypes.shape({
          value: PropTypes.string,
          label: PropTypes.string,
        })
      )
    ),
    PropTypes.arrayOf(
      PropTypes.shape({
        value: PropTypes.string,
        label: PropTypes.string,
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
  hideLabel: PropTypes.bool,
  placeholder: PropTypes.string,
  id: PropTypes.string,
  className: PropTypes.string,
  multiSelect: false,
}

Select.defaultProps = {
  selected: '',
  description: '',
  tooltip: {},
  example: {},
  hideLabel: false,
  placeholder: 'Select one',
  id: '',
  className: 'm-b-l',
  multiSelect: false,
}

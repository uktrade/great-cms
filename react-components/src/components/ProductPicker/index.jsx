import React, { useState, useEffect, useRef } from 'react'
import ReactDOM from 'react-dom'
import debounce from 'lodash.debounce'

const mapResults = (results) => {
  return results.commodities.map(({ description, hsCode }) => ({
    description,
    hsCode,
  }))
}

function ProductPicker() {
  const [error, setError] = useState(null)
  const [isLoaded, setIsLoaded] = useState(false)
  const [products, setProducts] = useState([])
  const [product, setProduct] = useState({})
  const inputRef = useRef(null)

  const initialDomSetup = () => {
    const hidden_input = document.getElementById('product-input')
    const submit_button = document.getElementById('product-input-submit')
    const input_label = document.querySelector('.great-hero__label')

    if (hidden_input && submit_button && input_label) {
      hidden_input.hidden = true
      hidden_input.style.display = 'none'

      submit_button.disabled = true

      input_label.htmlFor = 'react-product-input'
    }
  }

  const handleClosingResults = (e) => {
    const is_outside_picker = !document
      .querySelector('.great-product-picker')
      .contains(e.target)

    const is_not_clickable_item =
      e.target.nodeName !== 'BUTTON' && e.target.nodeName !== 'A'

    if (is_outside_picker && is_not_clickable_item) {
      setProducts([])
    }
  }

  const addResultsEventHandler = () => {
    document
      .querySelector('.great-hero--product-market')
      .addEventListener('click', handleClosingResults, true)
  }

  const removeResultsEventHandler = () => {
    document
      .querySelector('.great-hero--product-market')
      .removeEventListener('click', handleClosingResults, true)
  }

  const getProducts = (value) => {
    if (value) {
      fetch(
        `https://www.check-duties-customs-exporting-goods.service.gov.uk/rs/classify/keywords/TARIC/${value}/EN/1`
      )
        .then((res) => res.json())
        .then(
          (result) => {
            setIsLoaded(true)
            setProducts([])
            setProducts(mapResults(result))
            addResultsEventHandler()
          },
          (error) => {
            setIsLoaded(true)
            setError(error)
          }
        )
    }
  }

  const updateHiddenInput = (description, hsCode) => {
    const product_input = document.getElementById('product-input')
    const commodity_code_input = document.getElementById('commodity-code')

    if (product_input && commodity_code_input) {
      product_input.value = description
      commodity_code_input.value = hsCode
    }
  }

  const activateSubmitButton = () => {
    const submit_button = document.getElementById('product-input-submit')

    if (submit_button) {
      submit_button.disabled = false
    }
  }

  const deactivateSubmitButton = () => {
    const submit_button = document.getElementById('product-input-submit')

    if (submit_button) {
      submit_button.disabled = true
    }
  }

  const resetState = () => {
    setProduct({ description: null, hsCode: '' })
    setProducts([])
    inputRef.current.value = ''
    inputRef.current.focus()
    deactivateSubmitButton()
    updateHiddenInput(null, null)
  }

  const onProductChange = debounce(() => {
    getProducts(inputRef.current.value)

    if (inputRef.current.value !== '') {
      activateSubmitButton()
      updateHiddenInput(inputRef.current.value, product.hsCode)
    } else {
      deactivateSubmitButton()
    }
  }, 200)

  const isProductEntered =
    inputRef && inputRef.current && inputRef.current.value !== ''

  const isProducts = products.length >= 1

  useEffect(() => {
    initialDomSetup()
  }, [])

  return (
    <div>
      <input
        class="great-hero__input"
        type="text"
        onKeyUp={onProductChange}
        placeholder="For example, Apples"
        value={
          product.description && product.hsCode
            ? `${product.description} (${product.hsCode})`
            : null
        }
        ref={inputRef}
        name="react-product-input"
        id="react-product-input"
      />
      {isProductEntered && (
        <button
          className="great-product-picker__reset-button"
          onClick={(e) => {
            e.preventDefault()
            resetState()
          }}
        >
          <span role="img" class="fa fa-times" aria-hidden="true"></span>
        </button>
      )}
      {isProducts && (
        <ul className="great-bg-white">
          {products.map(({ description, hsCode }) => (
            <li key={hsCode}>
              <button
                className="govuk-body govuk-!-margin-bottom-0"
                onClick={() => {
                  setProduct({ description, hsCode })
                  setProducts([])
                  updateHiddenInput(description, hsCode)
                  activateSubmitButton()
                  removeResultsEventHandler()
                }}
              >
                {description} ({hsCode})
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

function createProductPicker({ element }) {
  ReactDOM.render(<ProductPicker />, element)
}

export { createProductPicker, ProductPicker }

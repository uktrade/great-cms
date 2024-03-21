import React, { useState, useEffect, useRef } from 'react'
import ReactDOM from 'react-dom'
import debounce from 'lodash.debounce'

const mapResults = (results) => {
  return results.data.map(({attributes: {title, goods_nomenclature_item_id}}) => ({title, goods_nomenclature_item_id}))
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
        `/api/product-picker/${value}`
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

  const updateHiddenInput = (title, goods_nomenclature_item_id) => {
    const product_input = document.getElementById('product-input')
    const commodity_code_input = document.getElementById('commodity-code')

    if (product_input && commodity_code_input) {
      product_input.value = title
      commodity_code_input.value = goods_nomenclature_item_id
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
    setProduct({ title: null, goods_nomenclature_item_id: '' })
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
      updateHiddenInput(inputRef.current.value, product.goods_nomenclature_item_id)
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
          product.title && product.goods_nomenclature_item_id
            ? `${product.title} (${product.goods_nomenclature_item_id})`
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
          {products.map(({ title, goods_nomenclature_item_id }) => (
            <li key={goods_nomenclature_item_id}>
              <button
                className="govuk-body govuk-!-margin-bottom-0"
                onClick={() => {
                  setProduct({ title, goods_nomenclature_item_id })
                  setProducts([])
                  updateHiddenInput(title, goods_nomenclature_item_id)
                  activateSubmitButton()
                  removeResultsEventHandler()
                }}
              >
                {title} ({goods_nomenclature_item_id})
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

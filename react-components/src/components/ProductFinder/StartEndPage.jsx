import React, { useState } from 'react'
import PropTypes from 'prop-types'
import ReactHtmlParser from 'react-html-parser'
import ClassificationTree from './ClassificationTree'
import SearchInput from './SearchInput'
import { analytics } from '../../Helpers'

const checkChars = /^[a-zA-Z0-9\s~!@#£$%°^&*()-_+={}[\]|\\/:;"'<>,.?]*$/
const testInput = /[a-zA-Z]+/

export default function StartEndPage(props) {
  const {
    commodityCode,
    defaultCommodityName,
    saveProduct,
    searchCompletedMode,
    allowSaveSameName,
  } = props

  const [commodityName, setCommodityName] = useState(defaultCommodityName)
  const [isEditing, setEditing] = useState(searchCompletedMode)

  const nameOkToSave = (name) => {
    return (
      testInput.test(name) &&
      (allowSaveSameName || name !== defaultCommodityName)
    )
  }

  const saveNamedProduct = () => {
    if (commodityCode && nameOkToSave(commodityName)) {
      saveProduct(commodityCode, commodityName.trim())
      if (!allowSaveSameName) {
        analytics({
          event: 'updateProductName',
        })
      }
    }
  }

  const validateKeys = (inputString) => {
    return checkChars.test(inputString)
  }
  const saveNameButtonClick = (e) => {
    setEditing(false)
    saveNamedProduct(e)
  }

  return (
    <>
      <div className="box box--no-pointer">
        {isEditing ? (
          <>
            <div className="form-group m-0">
              <SearchInput
                id="input-commodity-name"
                onChange={setCommodityName}
                defaultValue={ReactHtmlParser(commodityName).toString()}
                iconClass="fa-pencil-alt"
                onKeyReturn={
                  !searchCompletedMode ? saveNameButtonClick : () => {}
                }
                maxWidth="15em"
                validator={validateKeys}
                onSaveButtonClick={
                  !searchCompletedMode ? saveNameButtonClick : null
                }
                saveButtonDisabled={!nameOkToSave(commodityName)}
                saveButtonLabel="Update"
              />
            </div>
          </>
        ) : (
          <h3 className="h-xs p-v-0">
            <button
              className="p-h-0"
              type="button"
              onClick={() => {
                setEditing(true)
              }}
            >
              {ReactHtmlParser(commodityName).toString()}
              <i className="m-f-xs fas fa-pencil-alt text-blue-deep-60" />
            </button>
          </h3>
        )}
        <h4 className="h-xxs p-v-xxs">HS6 Code: {commodityCode}</h4>
        <ClassificationTree hsCode={commodityCode} />
      </div>
      {searchCompletedMode ? (
        <>
          <p>
            If you&apos;ve created an Export Plan, make sure you update it to
            reflect your new product. You can change product at any time.
          </p>
          <button
            className="button button--primary save-product"
            type="button"
            onClick={saveNamedProduct}
            disabled={!nameOkToSave(commodityName)}
          >
            Save product
          </button>
        </>
      ) : (
        ''
      )}
    </>
  )
}

StartEndPage.propTypes = {
  commodityCode: PropTypes.string.isRequired,
  defaultCommodityName: PropTypes.string.isRequired,
  saveProduct: PropTypes.func.isRequired,
  allowSaveSameName: PropTypes.bool,
  searchCompletedMode: PropTypes.bool,
}

StartEndPage.defaultProps = {
  allowSaveSameName: true,
  searchCompletedMode: false,
}

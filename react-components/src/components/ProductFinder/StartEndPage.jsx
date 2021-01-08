import React, { useState} from 'react'
import PropTypes from 'prop-types'
import ClassificationTree from './ClassificationTree'
import SearchInput from './SearchInput'


export default function StartEndPage(props) {
  const { commodityCode, defaultCommodityName, 
    saveProduct, label, buttonLabel } = props

  const [commodityName, setCommodityName] = useState(defaultCommodityName)

  const saveNamedProduct = () => {
    if(commodityCode && commodityName) {
      saveProduct(commodityCode, commodityName)
    }
  }

  return (
    <div className="box box--no-pointer">
      <h3 className="h-xs p-v-0">HS Code: {commodityCode}</h3>
      <ClassificationTree hsCode={commodityCode} />
      <div className="form-group m-t-s m-b-0">
        <SearchInput
          label={label}
          id="input-commodity-name"
          onChange={setCommodityName}
          defaultValue={commodityName}
          iconClass="fa-pencil-alt"
          onKeyReturn={saveNamedProduct}
          autoFocus
          maxWidth="15em"
        />
      </div>
      <button
        className="button button--primary save-product m-t-s"
        type="button"
        onClick={saveNamedProduct}
        disabled={!commodityName } 
      >
        {buttonLabel}
      </button>
    </div>
  )
}

StartEndPage.propTypes = {
  commodityCode: PropTypes.string.isRequired,
  defaultCommodityName: PropTypes.string.isRequired,
  saveProduct:PropTypes.func.isRequired,
  label: PropTypes.string,
  buttonLabel: PropTypes.string, 
}

StartEndPage.defaultProps = {
  label: 'Does this look like the right product? Name it, then save it.',
  buttonLabel: 'Save product', 
}

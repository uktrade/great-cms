import React, { useState} from 'react'
import PropTypes from 'prop-types'
import ClassificationTree from './ClassificationTree'
import SearchInput from './SearchInput'


export default function StartEndPage(props) {
  const { commodityCode, defaultCommodityName, saveProduct } = props

  const [commodityName, setCommodityName] = useState(defaultCommodityName)

  const saveNamedProduct = () => {
    saveProduct(commodityCode, commodityName)
  }
  return (
    <div>
      <div className="box box--no-pointer m-b-s">
        <h3 className="h-xs p-v-0">HS Code: {commodityCode}</h3>
        <ClassificationTree hsCode={commodityCode} />
        <div className="form-group m-t-s m-b-0">
          <SearchInput
            label="Does this look like the right product? Name it, then save it."
            id="input-commodity-name"
            onChange={setCommodityName}
            defaultValue={commodityName}
            iconClass="fa-pencil-alt"
            onKeyReturn={saveNamedProduct}
            autoFocus
            maxWidth="15em"
          />
        </div>
      </div>
      <button
        className="button button--primary save-product"
        type="button"
        onClick={saveNamedProduct}
        disabled={!commodityName} 
      >
        Save product
      </button>
    </div>
  )
}

StartEndPage.propTypes = {
  commodityCode: PropTypes.string.isRequired,
  defaultCommodityName: PropTypes.string.isRequired,
  saveProduct:PropTypes.func.isRequired 
}

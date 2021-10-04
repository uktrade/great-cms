import React, { useState } from 'react'
import PropTypes from 'prop-types'

import ClassificationTree from '@src/components/ProductFinder/ClassificationTree'

export default function CommodityCodeDetails({ product }) {
  const [isOpen, setopen] = useState(null)

  return (
    <>
      <div className="text-blue-deep-60 bg-white radius p-b-0 p-t-xxs p-f-xxs">
        <div className="flex-center">
          <button type="button" onClick={() => setopen(!isOpen)}>
            <i
              className={`fas ${isOpen ? 'fa-chevron-up' : 'fa-chevron-down'}`}
            />
            <span className="visually-hidden">See details</span>
          </button>
          <span className="m-l-xxs">HS6 code: {product.commodity_code}</span>
        </div>

        {(isOpen !== null && (
          <div className={`p-xs w-full ${!isOpen ? 'hidden' : ''}`}>
            <ClassificationTree hsCode={product.commodity_code} />
          </div>
        )) || <></>}
      </div>
    </>
  )
}

CommodityCodeDetails.propTypes = {
  product: PropTypes.shape({
    commodity_code: PropTypes.string,
    commodity_name: PropTypes.string,
  }),
}

CommodityCodeDetails.defaultProps = {
  product: {},
}

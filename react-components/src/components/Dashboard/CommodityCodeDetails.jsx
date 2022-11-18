import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { links } from '@src/constants'
import { analytics } from '@src/Helpers'

import ClassificationTree from '@src/components/ProductFinder/ClassificationTree'

export default function CommodityCodeDetails({ product }) {
  const [isOpen, setopen] = useState(null)

  const openSection = () => {
    setopen(!isOpen)
    if (!isOpen) {
      analytics({
        event: 'openProductInfo',
        HS6Code: product.commodity_code,
      })
    }
  }

  return (
    <>
      <div className="bg-white p-b-0 p-t-xxs p-f-xxs">
        <div className="flex-center">
          <button type="button icon-only" onClick={() => openSection()}>
            <i
              className={`fas ${isOpen ? 'fa-chevron-up' : 'fa-chevron-down'}`}
            />
            <span className="visually-hidden">See details</span>
          </button>
          <span className="link">{product.commodity_name}</span>
        </div>

        {isOpen !== null && (
          <div className={`p-xs w-full ${!isOpen ? 'hidden' : ''}`}>
            <p className="m-v-0">
              Here is the export classification for {product.commodity_name}.
            </p>
            <ClassificationTree hsCode={product.commodity_code} />
            <p className="m-v-0 body-m">
              We use classification at the chapter level to suggest possible
              export markets and classification at the sub-heading level to show
              you other relevant content about your product.
            </p>
            <a className="body-m" href={links['using-commodity-codes']}>
              For more information see our lesson on product classification
            </a>
          </div>
        )}
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

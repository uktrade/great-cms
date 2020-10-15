import React, { useCallback, useState } from 'react'
import PropTypes from 'prop-types'
import { forceReRender } from '@storybook/react'

export default function RegionToggle(props) {
  const [expand, setExpand] = useState(props.expandAllRegions)

  const countryListToggle = () => {
    setExpand(!expand)
  }

   return (
      <section>
          <div className="grid">
              <h2 className="region-name h-xs" onClick={countryListToggle}>{props.region}
                <button type="button" className="region-expand icon"> 
                  { (expand || props.expandAllRegions) ? '-' : '+'}
                </button>
              </h2>
              <span className={ (expand || props.expandAllRegions) ? 'countryList open': 'countryList'}>
                <hr/>
                <ul>{props.countries}</ul>
              </span>           
          </div>
          <hr className="regionSeperator"/>
      </section>
  )
}

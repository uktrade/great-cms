import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'

export default function RegionToggle(props) {
  const [expand, setExpand] = useState(false)
  const { region, expandAllRegions, countries } = props

  const countryListToggle = () => {
    setExpand(!expand)
  }

  useEffect(() => {
    if(expandAllRegions) {
      setExpand(false)
    }
  }, [expandAllRegions])

  return (
    <section className="accordion c-full">
        <hr className="hr hr--light m-v-xxs"/>
        <div className="expander-section p-r-s">
          <button 
            type="button" 
            className="region-expand icon p-h-0" 
            onClick={countryListToggle}
          >
            <h2 className="region-name h-xs p-v-0 text-align-left">{region}</h2>
              {(expand || expandAllRegions) ? <i className="fa fa-minus text-blue-deep-80"/> : <i className="fa fa-plus text-blue-deep-80"/>}
          </button>
        </div>
        <div className={`p-t-s ${(expand || expandAllRegions) ? 'expand-section open': 'expand-section'}`}>
          <div>{countries}</div>
        </div>
      </section>
  )
}

RegionToggle.propTypes = {
  region: PropTypes.string.isRequired,
  expandAllRegions: PropTypes.bool.isRequired,
  countries: PropTypes.node.isRequired,
}

import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'

export default function RegionToggle(props) {
  const [expand, setExpand] = useState(false)
  const { region, expandAllRegions, countries, index } = props

  const countryListToggle = () => {
    setExpand(!expand)
  }

  useEffect(() => {
    if (expandAllRegions) {
      setExpand(false)
    }
  }, [expandAllRegions])

  const controlAreaId = `region-content-area-${index}`

  return (
    <section className="accordion c-full">
      <hr className="hr hr--light m-v-xxs" role="presentation" />
      <div className="expander-section">
        <button
          type="button"
          className="region-expand h-xs"
          aria-expanded={expand || expandAllRegions}
          aria-controls={controlAreaId}
          onClick={countryListToggle}
        >
          <span>{region}</span>
          <i className={`fa fa-${expand || expandAllRegions ? 'minus' : 'plus'}`} />
        </button>
      </div>
      <div
        id={controlAreaId}
        className={`p-t-s ${
          expand || expandAllRegions ? 'expand-section open' : 'expand-section'
        }`}
      >
        <h2 className="visually-hidden">{region}</h2>
        <ol className="m-t-0">{countries}</ol>
      </div>
    </section>
  )
}

RegionToggle.propTypes = {
  region: PropTypes.string.isRequired,
  expandAllRegions: PropTypes.bool.isRequired,
  countries: PropTypes.node.isRequired,
  index: PropTypes.number.isRequired,
}

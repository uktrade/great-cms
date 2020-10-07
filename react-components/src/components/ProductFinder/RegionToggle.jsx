import React, { useState } from 'react'
import PropTypes from 'prop-types'

export default function RegionToggle(props){

  const [expand, setExpand] = useState(props.expandAllRegions)

  const countryListToggle = () => {
     setExpand(!expand || props.expandAllRegions)
  }

   return (
    <span>
      <section key={props.region.replace(/[\s,]+/g, '-').toLowerCase()}>
          <div className="grid">
            <div className="c-full-width">
              <h2 className="region-name h-xs">{props.region}
                <button className="region-expand" onClick={countryListToggle}><strong>{(expand || props.expandAllRegions) ? '-' : '+'}</strong></button>
              </h2>
              <ul key={props.region.replace(/[\s,]+/g, '-').toLowerCase()} className={(props.expandAllRegions || expand) ? 'countryList open' : 'countryList'}>{props.countries}</ul>
              <hr className="hr m-b-xxs"></hr>
            </div>
          </div>
        </section>
   </span>
  )
}
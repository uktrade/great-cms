import React from 'react'
import PropTypes from 'prop-types'
import Services from '@src/Services'

import './stylesheets/Success.scss'


export default function Success(props){
  const countries = props.countries.map((item, i) => <b key={i}>{item.label}</b>)
  const maybePlural = props.countries.length == 1 ? 'has' : 'have'
  const exportPlanUrl = `${Services.config.exportPlanTargetMarketsUrl}#sector-chooser`

  return (
    <div className='great-mvp-countries-success m-t-xxs'>
      <h2 className='h-m p-t-0'>Which markets do you have in mind?</h2>
      <div className='grid-flex'>
        <div className="c-1-2">
          <div className='great-mvp-flex'>
            <div className='great-mvp-icon-container p-t-s p-r-xs p-f-xs'>
              <img src='/static/images/book.svg' />
            </div>
            <div className='p-xs great-mvp-text-container'>
              <p className="m-b-xs m-t-0">{countries} {maybePlural} been added as target markets to your export plan.</p>
              <a className='great-mvp-wizard-step-link m-r-s' href={exportPlanUrl}>View export plan</a>
              <button
                href='#'
                className='great-mvp-wizard-step-link'
                onClick={props.handleChangeAnswers}
              >Change countries</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

Success.propTypes = {
  countries:  PropTypes.array.isRequired,
  handleChangeAnswers: PropTypes.func.isRequired,
}

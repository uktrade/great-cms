import React from 'react'
import PropTypes from 'prop-types'


export default function Start(props){
  return (
    <div className='great-mvp-countries-Start m-t-xxs'>
      <div className="w-1-2">
        <h2 className='h-m p-t-0'>Would you like to add export markets to your export plan?</h2>
        <p>You can keep learning, and every now and then we will ask you a few questions. Your answers will be added to your export plan, moving you closer to sending your first order overseas.</p>
        <a
          href='#"'
          className='great-mvp-wizard-step-button'
          onClick={event => { event.preventDefault(); props.handleClick() }}
        >Add target markets</a>
      </div>
    </div>
  )
}

Start.propTypes = {
  handleClick: PropTypes.func.isRequired,
}

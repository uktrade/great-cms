import React from 'react'
import PropTypes from 'prop-types'


const styles = {
  p: {
    marginTop: 10,
    marginBottom: 10,
  },
  span: {
    dislay: 'inline-block',
    marginLeft: 20,
    marginRight: 20,
    fontSize: 20,
  },
  hr: {
    verticalAlign: 'middle',
    width: '40%',
    display: 'inline-block',
    background: '#666',
  }
}

export default function VerticalSeparator(props){
  return (
    <p style={styles.p}>
      <hr style={styles.hr} />
      <span style={styles.span}>or</span>
      <hr style={styles.hr} />
    </p>
  )
}



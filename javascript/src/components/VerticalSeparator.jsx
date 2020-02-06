import React from 'react'
import PropTypes from 'prop-types'


const styles = {
  p: {
    marginTop: 30,
    marginBottom: 30,
  },
  span: {
    dislay: 'inline-block',
    marginLeft: 20,
    marginRight: 20,
    fontSize: 19,
  },
  hr: {
    verticalAlign: 'middle',
    width: '40%',
    display: 'inline-block',
    background: '#979797',
    margin: 0,
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



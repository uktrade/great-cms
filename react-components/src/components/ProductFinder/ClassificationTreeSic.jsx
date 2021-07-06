import React, { useState, useEffect, useRef } from 'react'
import PropTypes from 'prop-types'
import Services from '@src/Services'
import Spinner from '../Spinner/Spinner'

const trimAndCapitalize = (str) => {
  const match = /^(?:CHAPTER\s\d+)?\s*-*\s*(.*)$/.exec(str)
  const locStr = match ? match[1] : str
  return (
    locStr && locStr.substr(0, 1).toUpperCase() + locStr.substr(1).toLowerCase()
  )
}

function TreeBranch(props) {
  const { arr } = props
  const str = arr.shift()
  return (
    <div className="classification-tree__item">
      <i className="fa fa-level-up-alt classification-tree__arrow" />
      <span>{str}</span>
      {arr.length ? (
        <ul className="m-v-xs">
          <li key={arr.length}>
            <TreeBranch arr={arr} />
          </li>
        </ul>
      ) : (
        ''
      )}
    </div>
  )
}

export default function ClassificationTreeSic(props) {
  const { sicCode } = props
  const [sicCodes, setSicCodes] = useState({})

  useEffect(() => {
    Services.choicesApi({ choice: 'SIC_SECTOR_MAPPING' }).then((results) => {
      setSicCodes(
        (results || []).reduce((out, row) => {
          out[row['SIC code']] = row
          return out
        }, {})
      )
    })
  }, [])

  return (
    <>
      {sicCodes && sicCodes[sicCode] ? (
        <div className="classification-tree g-panel m-v-xs">
        <TreeBranch
          arr={[
            sicCodes[sicCode]['DIT sector'],
            sicCodes[sicCode]['DIT full sector name'],
            sicCodes[sicCode]['SIC description'],
          ]}
        />
        </div>
      ) : (
        ''
      )}
    </>
  )
}

ClassificationTreeSic.propTypes = {
  sicCode: PropTypes.string.isRequired,
}

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
  const { level, hsCode } = props
  if (!level) {
    return null
  }
  if (!level.type || level.type === 'SECTION')
    return <TreeBranch level={level.children[0]} hsCode={hsCode} />
  const arrow = level.type !== 'CHAPTER' && (
    <i className="fa fa-level-up-alt classification-tree__arrow" />
  )
  return (
    <div className="classification-tree__item">
      {arrow}

      {(level.code || '').substring(0, hsCode.length) !== hsCode ? (
        <>
          <div>{trimAndCapitalize(level.desc)}</div>
          <ul className="m-v-xs">
            {(level.children || []).map((child) => (
              <li key={level.code}>
                <TreeBranch level={child} hsCode={hsCode} />
              </li>
            ))}
          </ul>
        </>
      ) : (
        <>
          <div className="body-l-b">{trimAndCapitalize(level.desc)}</div>
          <div className="body-m">HS6 Code: {hsCode}</div>
        </>
      )}
    </div>
  )
}

export default function ClassificationTree({ hsCode }) {
  const [schedule, setSchedule] = useState()
  const isMounted = useRef(true)

  useEffect(() => {
    if (!schedule) {
      Services.lookupProductSchedule({ hsCode }).then((results) => {
        if (isMounted.current) {
          setSchedule(results)
        }
      })
    }
    return () => {
      isMounted.current = false
    }
  }, [])

  return (
    <>
      {(schedule && schedule.children && schedule.children.length && (
        <div className="classification-tree g-panel m-v-xs">
          <TreeBranch level={schedule} hsCode={hsCode} />
        </div>
      )) ||
        (schedule && (
          <div className="classification-tree m-v-xs form-group-error">
            Unable to show classification tree
          </div>
        )) || <Spinner text="" />}
    </>
  )
}

ClassificationTree.propTypes = {
  hsCode: PropTypes.string.isRequired,
}

const ptLevel = PropTypes.shape({
  type: PropTypes.string,
  desc: PropTypes.string,
  code: PropTypes.string,
})

TreeBranch.propTypes = {
  hsCode: PropTypes.string.isRequired,
  level: PropTypes.shape({
    type: PropTypes.string,
    desc: PropTypes.string,
    code: PropTypes.string,
    children: PropTypes.arrayOf(ptLevel),
  }).isRequired,
}

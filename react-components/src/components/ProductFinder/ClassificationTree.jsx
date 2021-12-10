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

const typeMapping = {
  CHAPTER: 'Chapter',
  HEADING: 'Heading',
  ITEM: 'Sub-heading',
}

function TreeBranch(props) {
  const { level, hsCode } = props
  if (!level) {
    return null
  }
  if (!level.type || level.type === 'SECTION')
    return <TreeBranch level={level.children[0]} hsCode={hsCode} />
  const leaf = (level.code || '').substring(0, hsCode.length) === hsCode
  return (
    <>
      <div
        className={`grid m-b-xxs m-f-xxs br-xs body-l ${
          leaf ? 'bg-white' : ''
        }`}
      >
        <div className="c-1-3 type-heading">{typeMapping[level.type]}</div>
        <div className="c-2-3 level-decription">
          {trimAndCapitalize(level.desc)}
        </div>
      </div>
      {((!leaf && level.children) || []).map((child) => (
        <TreeBranch
          level={child}
          hsCode={hsCode}
          key={level.code}
        />
      ))}
    </>
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
        <div className="g-panel m-v-xs classification-tree">
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

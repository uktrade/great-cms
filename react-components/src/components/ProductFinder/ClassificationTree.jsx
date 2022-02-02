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

function TreeLine({ level, leaf, itemType }) {
  return (
    <div
      className={`grid m-b-xxs m-f-xxs br-xs body-l ${leaf ? 'bg-white' : ''}`}
    >
      <div className="c-1-3 type-heading">
        {typeMapping[itemType || level.type]}
      </div>
      <div className="c-2-3 level-decription">
        {trimAndCapitalize(level.desc)}
      </div>
    </div>
  )
}

function TreeBranch({ schedule, hsCode }) {
  let subHeadingShown = false

  const showLevel = (level, parent) => {
    if (!level) {
      return null
    }
    if (!level.type || level.type === 'SECTION')
      return showLevel(level.children[0])
    const leaf = (level.id || '').substring(0, hsCode.length) === hsCode
    if (leaf && level.id.length > hsCode.length) {
      // We've gone too far - there must be no node at HS6
      if (!subHeadingShown) {
        subHeadingShown = true
        return <TreeLine level={parent} leaf={leaf} itemType={'ITEM'} />
      } else {
        return null
      }
    }
    return (
      <React.Fragment key={`level-${leaf.id}`}>
        {level.type !== 'ORPHAN' && <TreeLine level={level} leaf={leaf} />}
        {((!leaf && level.children) || []).map((child) =>
          showLevel(child, level)
        )}
      </React.Fragment>
    )
  }
  return showLevel(schedule)
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
          <TreeBranch schedule={schedule} hsCode={hsCode} />
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
  schedule: PropTypes.shape({
    type: PropTypes.string,
    desc: PropTypes.string,
    code: PropTypes.string,
    children: PropTypes.arrayOf(ptLevel),
  }).isRequired,
}

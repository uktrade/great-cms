import React, { useState, useEffect } from 'react'
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


/**
 * The Classification Tree builder will parse a full schedule as follows:
 * - Skip the top-level and SECTION
 * - Add the CHAPTER
 * - Add the HEADING
 * - Attempt to find an exact HS6 code match in the rest of the schedule:
 *    - If found, add that as ITEM
 *    - If not found:
 *      - If there was an ORPHAN directly under HEADING with no siblings, add that as ITEM
 *      - If there was not, repeat the HEADING description as ITEM
 * - Flag the last element as 'leaf'
 */
export const buildClassificationTree = (hsCode, schedule) => {
  let orphanAsItem = null

  const walk = (tree, level) => {
    if (!level.type || level.type === 'SECTION') {
      return walk(tree, level.children[0])
    }

    if (level.type === 'CHAPTER' || level.type === 'HEADING' || level.id === hsCode) {
      tree.push({
        type: level.type,
        description: trimAndCapitalize(level.desc),
        id: level.id,
      })
    }

    if (level.id === hsCode) {
      return tree
    }

    if (level.type === 'HEADING' && level.children.length === 1 && level.children[0].type === 'ORPHAN') {
      orphanAsItem = {
        type: 'ITEM',
        description: trimAndCapitalize(level.children[0].desc),
        id: level.children[0].id,
      }
    }

    if (level.children && level.children.length) {
      level.children.map(child => walk(tree, child))
    }

    return tree
  }


  const tree = walk([], schedule)

  if (tree.length < 3) {
    tree.push(orphanAsItem || {
      type: 'ITEM',
      description: tree[tree.length - 1].description,
      id: 'leaf',
    })
  }

  tree[tree.length - 1].leaf = true

  return tree
}

const TreeLine = ({ level }) => (
  <div
    className={`grid m-b-xxs m-f-xxs br-xs body-l ${level.leaf ? 'bg-white' : ''} classification-tree__line`}
  >
    <div className="c-1-3 type-heading">
      {typeMapping[level.type]}
    </div>
    <div className="c-2-3 level-description">
      {level.description}
    </div>
  </div>
)

// React.memo prevents ClassificationTree from being rerendered
// if hsCode hasn't changed.
const ClassificationTree = React.memo(({ hsCode }) => {
  const [tree, setTree] = useState(null)

  useEffect(() => {
    // Set to null to prevent old tree from being displayed while
    // old tree is being built.
    setTree(null)
    Services.lookupProductSchedule({ hsCode })
      .then(results => {
        if (results.errorCode)
          setTree([])
        else
          setTree(buildClassificationTree(hsCode, results))
      })
  }, [hsCode])  // Only rebuild tree when hsCode has changed.

  return (
    <>
      {(tree && tree.length > 0 && (
        <div className="g-panel m-v-xs classification-tree">
          {tree.map(line => (
            <TreeLine level={line} key={line.id} />
          ))}
        </div>
      )) ||
      (tree && (
        <div className="classification-tree m-v-xs form-group-error">
          Unable to show classification tree
        </div>
      )) || <Spinner text="" />}
    </>
  )
})

export default ClassificationTree;

ClassificationTree.propTypes = {
  hsCode: PropTypes.string.isRequired,
}

TreeLine.propTypes = {
  level: PropTypes.shape({
    type: PropTypes.string.isRequired,
    description: PropTypes.string.isRequired,
    id: PropTypes.string.isRequired,
    leaf: PropTypes.bool,
  }).isRequired,
}

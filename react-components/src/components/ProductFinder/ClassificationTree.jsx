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

export const buildProductTree = (hsCode, schedule) => {
  const walk = (tree, level) => {
    // Go straight to the next level if we're high up
    if (!level.type || level.type === 'SECTION') {
      return walk(tree, level.children[0])
    }

    // Add to tree if id is shorter than code or if id matches
    if (level.id.length < hsCode.length || level.id === hsCode) {
      tree.push({
        type: level.type,
        description: trimAndCapitalize(level.desc),
        id: level.id,
      })
    }

    // Found the leaf, return the tree now
    if (level.id === hsCode) {
      return tree
    }

    // Process the children items
    if (level.children && level.children.length) {
      level.children.map(child => walk(tree, child))
    }

    // Return the incomplete tree
    return tree
  }


  const tree = walk([], schedule)

  // Repeat heading if no appropriate sub-heading has been found
  if (tree.length < 3) {
    tree.push({
      type: 'ITEM',
      description: tree[tree.length - 1].description,
      id: 'leaf',
    })
  }

  // Flag the last item as leaf
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
    <div className="c-2-3 level-decription">
      {level.description}
    </div>
  </div>
)

export default function ClassificationTree({ hsCode }) {
  const [tree, setTree] = useState(null)
  const isMounted = useRef(true)

  useEffect(() => {
    if (!tree) {
      Services.lookupProductSchedule({ hsCode }).then((results) => {
        if (isMounted.current) {
          if (results.errorCode) {
            setTree([])
          } else {
            setTree(buildProductTree(hsCode, results))
          }
        }
      })
    }
    return () => {
      isMounted.current = false
    }
  }, [])

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
}

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

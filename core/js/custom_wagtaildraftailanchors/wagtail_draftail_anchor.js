const React = window.React
import { Component } from 'react'
const RichUtils = window.DraftJS.RichUtils
const Icon = window.wagtail.components.Icon
const Portal = window.wagtail.components.Portal
const Tooltip = window.draftail.Tooltip
import slugify from 'slugify'

const CopyAnchorButton = ({ identifier }) => {
  const [didCopy, setDidCopy] = React.useState(false)

  const copyText = (event) => {
    event.preventDefault()
    if (navigator.clipboard) {
      navigator.clipboard.writeText(identifier)
      setDidCopy(true)
    }
  }

  const classes = 'button Tooltip__button'
  return (
    <button
      class={classes}
      style={{ marginLeft: '1rem' }}
      aria-label="Copy anchor identifier"
      aria-live="polite"
      role="button"
      onClick={copyText}
    >
      {didCopy ? 'Copied' : 'Copy'}
    </button>
  )
}

// Modifies draftail Tooltip Entity component
class _TooltipEntity extends Component {
  constructor(props) {
    super(props)

    this.state = {
      showTooltipAt: null,
    }

    this.openTooltip = this.openTooltip.bind(this)
    this.closeTooltip = this.closeTooltip.bind(this)
  }

  openTooltip(e) {
    const trigger = e.target

    if (trigger instanceof Element) {
      this.setState({ showTooltipAt: trigger.getBoundingClientRect() })
    }
  }

  closeTooltip() {
    this.setState({ showTooltipAt: null })
  }

  render() {
    const {
      entityKey,
      contentState,
      children,
      onEdit,
      onRemove,
      icon,
    } = this.props
    const { showTooltipAt } = this.state
    const { url, anchor } = contentState.getEntity(entityKey).getData()

    const slugified = slugify(anchor)
    const anchorText = `#${slugified}`

    return (
      <a role="button" onMouseUp={this.openTooltip} className="TooltipEntity">
         <sub>
            <Icon name="anchor" className="TooltipEntity__icon" />
          </sub>
        <span className="TooltipEntity__text">{children}</span>
        {showTooltipAt && (
          <Portal
            onClose={this.closeTooltip}
            closeOnClick
            closeOnType
            closeOnResize
          >
            <Tooltip target={showTooltipAt} direction="top">
              <a
                href={url}
                title={url}
                target="_blank"
                rel="noopener noreferrer"
                className="Tooltip__link"
              >
                {anchorText}
              </a>
              <button
                style={{ marginLeft: '1rem' }}
                aria-label="Edit anchor identifier"
                aria-live="polite"
                role="button"
                className="button Tooltip__button"
                onClick={onEdit.bind(null, entityKey)}
              >
                Edit
              </button>
              <button
                className="button button-secondary no Tooltip__button"
                style={{ marginLeft: '1rem' }}
                aria-label="Remove anchor identifier"
                aria-live="polite"
                role="button"
                onClick={onRemove.bind(null, entityKey)}
              >
                Remove
              </button>
              <CopyAnchorButton identifier={slugified} />
            </Tooltip>
          </Portal>
        )}
      </a>
    )
  }
}

// Implement the new APIs.

const DECORATORS = []
const CONTROLS = []
const DRAFT_PLUGINS = []

const registerDecorator = (decorator) => {
  DECORATORS.push(decorator)
  return DECORATORS
}

const registerControl = (control) => {
  CONTROLS.push(control)
  return CONTROLS
}

// Override the existing initEditor to hook the new APIs into it.
// This works in Wagtail 2.0 but will definitely break in a future release.
const initEditor = window.draftail.initEditor

const initEditorOverride = (selector, options, currentScript) => {
  const overrides = {
    decorators: DECORATORS.concat(options.decorators || []),
    controls: CONTROLS.concat(options.controls || []),
    plugins: DRAFT_PLUGINS.concat(options.plugins || []),
  }

  const newOptions = Object.assign({}, options, overrides)

  return initEditor(selector, newOptions, currentScript)
}

window.draftail.registerControl = registerControl
window.draftail.registerDecorator = registerDecorator
window.draftail.initEditor = initEditorOverride

class AnchorIdentifierSource extends React.Component {
  componentDidMount() {
    const { editorState, entityType, onComplete } = this.props

    const content = editorState.getCurrentContent()

    const anchor = window.prompt('Create/ Edit an anchor link name')

    // Uses the Draft.js API to create a new entity with the right data.
    if (anchor) {
      const contentWithEntity = content.createEntity(
        entityType.type,
        'MUTABLE',
        {
          anchor: slugify(anchor.toLowerCase()),
        }
      )
      const entityKey = contentWithEntity.getLastCreatedEntityKey()
      const selection = editorState.getSelection()
      const nextState = RichUtils.toggleLink(editorState, selection, entityKey)

      onComplete(nextState)
    } else {
      onComplete(editorState)
    }
  }

  render() {
    return null
  }
}

const getAnchorIdentifierAttributes = (data) => {
  const url = data.anchor || null
  let icon = <Icon name="anchor" />
  let label = `#${url}`

  return {
    url,
    icon,
    label,
  }
}

const AnchorIdentifier = (props) => {
  const { entityKey, contentState } = props
  const data = contentState.getEntity(entityKey).getData()

  return <_TooltipEntity {...props} {...getAnchorIdentifierAttributes(data)} />
}

window.draftail.registerPlugin({
  type: 'ANCHOR-IDENTIFIER',
  source: AnchorIdentifierSource,
  decorator: AnchorIdentifier,
})

const React = window.React
const RichUtils = window.DraftJS.RichUtils
const TooltipEntity = window.draftail.TooltipEntity
const Icon = window.wagtail.components.Icon
const Portal = window.wagtail.components.Portal
const Tooltip = window.draftail.Tooltip
import slugify from 'slugify'

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

    const anchor = window.prompt('Anchor identifier:')

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

class ExtendedTooltipEntity extends TooltipEntity {
  constructor(props) {
    super(props);

    // Initialize the state with the extended property.
    this.state = {
      ...this.state,
      showTooltipAt: null,
    };

    // Bind the methods to the instance.
    this.openTooltip = this.openTooltip.bind(this);
    this.closeTooltip = this.closeTooltip.bind(this);
  }

  // Handle opening the tooltip when a trigger element is clicked.
  openTooltip(e) {
    const trigger = e.target.closest('[data-draftail-trigger]');

    // If the click is not within the tooltip trigger, return early.
    if (!trigger) {
      return;
    }

    const container = trigger.closest('[data-draftail-editor-wrapper]');
    const containerRect = container.getBoundingClientRect();
    const rect = trigger.getBoundingClientRect();

    // Update the state to show the tooltip at the correct position.
    this.setState({
      showTooltipAt: {
        container: container,
        top: rect.top - containerRect.top - window.scrollY,
        left: rect.left - containerRect.left - window.scrollX,
        width: rect.width,
        height: rect.height,
      },
    });
  }

  // Handle closing the tooltip.
  closeTooltip() {
    this.setState({ showTooltipAt: null });
  }

  render() {
    const isAnchorEntity =
      this.props.entityKey &&
      this.props.contentState.getEntity(this.props.entityKey).getData().anchor;

      const baseRender = super.render()

    if (isAnchorEntity) {
      const data = this.props.contentState
        .getEntity(this.props.entityKey)
        .getData();
      const slugified = slugify(data.anchor);
      const anchor = `#${slugified}`;

      return (
        <a
          href=""
          name={anchor}
          role="button"
          // Use onMouseUp to preserve focus in the text even after clicking.
          onMouseUp={(e) => this.openTooltip(e)}
          className="TooltipEntity"
          data-draftail-trigger
        >
          <sub>
            <Icon name="anchor" className="TooltipEntity__icon" />
          </sub>
          <span>{this.props.decoratedText}</span>
          {this.state.showTooltipAt && (
            <Portal
              node={this.state.showTooltipAt.container}
              onClose={this.closeTooltip}
              closeOnClick
              closeOnType
              closeOnResize
            >
              <Tooltip target={this.state.showTooltipAt} direction="top">
                {anchor}
                <CopyAnchorButton identifier={slugified} />
              </Tooltip>
            </Portal>
          )}
        </a>
      );
    }

    // If it's not an anchor entity, render the base content.
    return baseRender;
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

  return (
    <ExtendedTooltipEntity
      {...props}
      {...getAnchorIdentifierAttributes(data)}
    />
  )
}

window.draftail.registerPlugin({
  type: 'ANCHOR-IDENTIFIER',
  source: AnchorIdentifierSource,
  decorator: AnchorIdentifier,
})

const CopyAnchorButton = ({ identifier }) => {
  const [didCopy, setDidCopy] = React.useState(false)

  const copyText = (event) => {
    event.preventDefault()
    if(navigator.clipboard){
    navigator.clipboard.writeText(identifier)
    setDidCopy(true)
    }
  }

  const classes = 'button button-small'
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

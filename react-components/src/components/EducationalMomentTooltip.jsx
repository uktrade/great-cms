import React from 'react'
import PropTypes from 'prop-types'
import EducationalMomentIcon from './EducationalMomentIcon/EducationalMomentIcon'

export default class EducationalMomentTooltip extends React.Component {
    constructor(props) {
        super(props)

        // tooltip type constants
        this.TOOLTIP_TYPE = { Left: 'LEFT', Right: 'RIGHT' }

        this.state = {
          displayed: false,
        }

        this.bindEvents()
    }

    componentDidMount() {
        this.addEvents()
    }

    bindEvents() {
        this.handleHover = this.handleHover.bind(this)
        this.handleFocus = this.handleFocus.bind(this)
        this.handleBlur = this.handleBlur.bind(this)
        this.handleKeyDown = this.handleKeyDown.bind(this)
    }


    addEvents() {
        document.addEventListener('keydown', this.handleKeyDown, false)
    }

    handleKeyDown(e) {
      const { displayed } = this.state
      // if ESC button is pressed down make sure tooltip is closed
      // helpful for Zoomtext and other magnifiers
      if (e.keyCode === 27 && displayed) {
        this.hideTooltip()
      }
    }

    handleHover(e) {
      if (e.type === 'mouseenter') {
        this.showTooltip()
      } else {
        this.hideTooltip()
      }
    }

    handleFocus() {
      this.showTooltip()
    }

    handleBlur() {
      this.hideTooltip()
    }

    showTooltip() {
      this.setState({ displayed: true })
    }

    hideTooltip() {
      this.setState({ displayed: false })
    }

    render() {
      const { heading, description, id, type } = this.props
      const { displayed } = this.state

      return (
        <div
          className="educational-moment--tooltip-container"
          onMouseEnter={this.handleHover}
          onMouseLeave={this.handleHover}
          onFocus={this.handleFocus}
          onBlur={this.handleBlur}>
          <EducationalMomentIcon hiddenText="Additional information" ariaDescribedBy={id} />
            <div
              role="tooltip"
              className={`tooltip ${!displayed ? 'hidden' : ''} ${(type === this.TOOLTIP_TYPE.Right) ? 'tooltip--right-side' : ''}`}
              id={id}>
                <div className="educational-moment educational-moment--tooltip">
                    <div className="educational-moment__tooltip">
                        <h3 className="body-l-b m-b-0">{heading}</h3>
                        <p className="m-t-xs m-b-0">{description}</p>
                    </div>
                </div>
            </div>
        </div>
      )
    }
}

EducationalMomentTooltip.propTypes = {
  id: PropTypes.string.isRequired,
  heading: PropTypes.string.isRequired,
  description: PropTypes.string.isRequired,
  type: PropTypes.string
}

EducationalMomentTooltip.defaultProps = {
  type: 'RIGHT',
}

import React from 'react'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types'
import EducationalMomentIcon from './EducationalMomentIcon/EducationalMomentIcon'
import './stylesheets/EducationalMomentTooltip.scss'


export default class EducationalMomentTooltip extends React.Component {
    constructor(props) {
        super(props)

        //tooltip type constants
        this.TOOLTIP_TYPE = { Left: 'LEFT', Right: 'RIGHT' }

        this.state = {
          displayed: false,
        }

        this.bindEvents()
    }

    bindEvents() {
        this.handleHover = this.handleHover.bind(this)
        this.handleFocus = this.handleFocus.bind(this)
        this.handleBlur = this.handleBlur.bind(this)
        this.handleKeyDown = this.handleKeyDown.bind(this)
    }

    componentDidMount() {
        this.addEvents()
    }

    addEvents() {
        document.addEventListener('keydown', this.handleKeyDown, false)
    }

    handleKeyDown(e) {
      // if ESC button is pressed down make sure tooltip is closed
      // helpful for Zoomtext and other magnifiers
      if (e.keyCode === 27 && this.state.displayed) {
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

    handleFocus(e) {
      this.showTooltip()
    }

    handleBlur(e) {
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
              className={`tooltip ${!this.state.displayed ? 'hidden' : ''} ${(type === this.TOOLTIP_TYPE.Right) ? 'tooltip--right-side' : ''}`}
              id={id}>
                <div className="educational-moment educational-moment--tooltip">
                    <div className="educational-moment__tooltip" id="ease-of-doing-business-tooltip">
                        <h3 className="tooltip__heading h-m">{heading}</h3>
                        <p className="tooltip__paragraph">{description}</p>
                    </div>
                </div>
            </div>
        </div>
      )
    }
}

EducationalMomentTooltip.propTypes = {
  id: PropTypes.string,
  heading: PropTypes.string,
  description: PropTypes.string,
  type: PropTypes.string
}

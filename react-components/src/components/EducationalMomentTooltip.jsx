import React from 'react';
import PropTypes from 'prop-types';
import Tooltip from './Tooltip/Tooltip';
import EducationalMomentIcon from './EducationalMomentIcon/EducationalMomentIcon';

/**
 * Dynamically loaded component from HTML fixture
 * 
 * @class EducationalMomentTooltip
 * @selector ".educational-moment--tooltip"
 * 
 * HTML Fixture:
 * 
    <div class="educational-moment educational-moment--tooltip" data-tooltip-type="LEFT">
        <div class="js-hidden educational-moment__tooltip" id="tooltip-id">
            <h3 class="tooltip__heading h-m">Optional heading</h3>
            <p class="tooltip__paragraph">First paragraph</p>
            <p class="tooltip__paragraph">Second paragraph</p>
        </div>
    </div>
 *
 * Inner HTML content is replaced by React if javascript is on
 * However, we persere the originla fixture via this.props.htmlFixture
 * 
 * To switch the view of tooltip use optional parameter on the container:
 * data-tooltip-type="RIGHT"
 */
export default class EducationalMomentTooltip extends React.Component {
    constructor(props) {
        super(props);

        //tooltip type constants
        this.TOOLTIP_TYPE = { Left: 'LEFT', Right: 'RIGHT' };

        this.state = {
            id: null,
            displayed: false,
            loaded: false,
            tooltipContent: null,
            type: this.TOOLTIP_TYPE.Left
        }

        this.bindEvents();
    }

    bindEvents() {
        this.handleHover = this.handleHover.bind(this);
        this.handleFocus = this.handleFocus.bind(this);
        this.handleBlur = this.handleBlur.bind(this);
        this.handleKeyDown = this.handleKeyDown.bind(this);
    }

    componentDidMount() {
        this.extractFixture();
        this.determineType();
        this.addEvents();
    }

    addEvents() {
        document.addEventListener('keydown', this.handleKeyDown, false);
    }

    determineType() {
        let type = this.props.htmlFixture.dataset.tooltipType;
        if (type && type === this.TOOLTIP_TYPE.Right) {
            this.setState({ type: this.TOOLTIP_TYPE.Right });
        }
    }

    extractFixture() {
        let tooltipContent = this.props.htmlFixture.querySelector('.educational-moment__tooltip');
        tooltipContent.classList.remove('js-hidden');

        this.setState({
            id: tooltipContent.id,
            loaded: true,
            tooltipContent: tooltipContent
        });
    }

    handleKeyDown(e) {
        // if ESC button is pressed down make sure tooltip is closed
        // helpful for Zoomtext and other magnifiers
        if (e.keyCode === 27 && this.state.displayed) {
            this.hideTooltip();
        }
    }

    handleHover(e) {
        if (e.type === 'mouseenter') {
            this.showTooltip();
        } else {
            this.hideTooltip();
        }
    }

    handleFocus(e) {
        this.showTooltip();
    }

    handleBlur(e) {
        this.hideTooltip();
    }

    showTooltip() {
        this.setState({ displayed: true });
    }

    hideTooltip() {
        this.setState({ displayed: false });
    }

    render() {
        return (
            <div onMouseEnter={this.handleHover}
                onMouseLeave={this.handleHover}
                onFocus={this.handleFocus}
                onBlur={this.handleBlur}>
                <EducationalMomentIcon hiddenText="Additional information" ariaDescribedBy={this.state.id} />
                {this.state.loaded ?
                    <Tooltip
                        className={`${!this.state.displayed ? 'hidden' : ''} ${(this.state.type === this.TOOLTIP_TYPE.Right) ? 'tooltip--right-side' : ''}`}
                        id={this.state.id}
                        tooltipContent={this.state.tooltipContent} />
                    : ''
                }
            </div>
        )
    }
}

EducationalMomentTooltip.propTypes = {
    displayed: PropTypes.bool,
    id: PropTypes.string,
    loaded: PropTypes.bool,
    tooltipContent: PropTypes.node,
    type: PropTypes.string
}
import React from 'react';
import ReactDOM from 'react-dom';
import PropTypes from 'prop-types';
import Tooltip from './Tooltip';

export default class EducationalMoment extends React.Component {
    constructor(props, container) {
        super(props);

        this.state = {
            displayed: this.props.displayed,
            id: null,
            heading: null,
            body: [],
            headingPriority: null
        }

        this.handleHover = this.handleHover.bind(this);
        this.handleFocus = this.handleFocus.bind(this);
        this.handleBlur = this.handleBlur.bind(this);
    }

    componentDidMount() {
        this.extractContent(ReactDOM.findDOMNode(this).parentNode);
    }

    extractContent(container) {
        const id = container.dataset.tooltipId;
        const heading = container.dataset.tooltipHeading;
        const headingPriority = container.dataset.headingPriority;
        const body = container.dataset.tooltipBody.split(';;');

        this.setState({
            id: id,
            heading: heading,
            body: body,
            headingPriority: headingPriority
        });
    }

    handleHover(e) {
        let isDisplayed = e.type === 'mouseenter';

        this.setState({ displayed: isDisplayed });
    }

    handleFocus(e) {
        this.setState({ displayed: true });
    }

    handleBlur(e) {
        this.setState({ displayed: false });
    }

    render() {
        return (
            <div className="wqe"
                onMouseEnter={this.handleHover}
                onMouseLeave={this.handleHover}
                onFocus={this.handleFocus}
                onBlur={this.handleBlur}>
                <button aria-describedby={this.state.id}>Show tooltip</button>

                <Tooltip
                    id={this.state.id}
                    className={this.state.displayed ? '' : 'hidden'}
                    heading={this.state.heading}
                    body={this.state.body}
                />
            </div >
        )
    }

}

EducationalMoment.propTypes = {
    displayed: PropTypes.bool,
    id: PropTypes.string,
    heading: PropTypes.string,
    body: PropTypes.array,
    headingPriority: PropTypes.string
}
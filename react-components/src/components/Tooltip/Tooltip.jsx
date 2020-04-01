import React from 'react';
import './Tooltip.scss'

export default class Tooltip extends React.Component {

    constructor(props) {
        super(props);
        this.tooltipRef = React.createRef();
    }

    componentDidMount() {
        //dom operation moved here rather than render function for performance
        this.tooltipRef.current.appendChild(this.props.tooltipContent);
    }

    render() {
        return (
            <div id={this.props.id}
                role="tooltip"
                className={`tooltip ${this.props.className}`}
                ref={this.tooltipRef}>
            </div>
        )
    }
}
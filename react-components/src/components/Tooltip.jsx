import React from 'react';
import './stylesheets/Tooltip.scss'

export default class Tooltip extends React.Component {

    constructor(props) {
        super(props);
    }

    render() {
        const DynamicHeadingTag = `h${this.props.priority}`;
        return (
            <div id={this.props.id} role="tooltip" className={`tooltip ${this.props.className}`}>
                <DynamicHeadingTag className="tooltip__heading h-m">{this.props.heading}</DynamicHeadingTag>
                {this.props.body.map((item, key) =>
                    <p className="tooltip__paragraph" key={key}>{item}</p>
                )}
            </div>
        )
    }

}
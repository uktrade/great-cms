import React from 'react';
import PropTypes from 'prop-types';
import './Spinner.scss';

export default class Spinner extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            text: this.props.text || 'Loading'
        }
    }

    render() {
        return (
            <div aria-live="polite" role="status">
                {this.state.text} <div className="spinner"></div>
            </div>
        )
    }

}

Spinner.propTypes = {
    text: PropTypes.string
}

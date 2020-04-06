import React from 'react';
import PropTypes from 'prop-types';
import './Figure.scss';

export default class Figure extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <figure className="figure">
                <div className="figure__image-wrapper">
                    <img className="figure__image" src={this.props.image} alt=""></img>
                </div>
                <figcaption className="figure__caption">{this.props.caption}</figcaption>
            </figure>
        )
    }

}

Figure.propTypes = {
    image: PropTypes.string.isRequired,
    caption: PropTypes.string.isRequired,
}

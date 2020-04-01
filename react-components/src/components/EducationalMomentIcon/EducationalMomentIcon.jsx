import React from 'react';
import './EducationalMomentIcon.scss';
import OpenBookIcon from './open-book-icon.png';

export default class EducationalMomentIcon extends React.Component {

    constructor(props) {
        super(props);
    }

    render() {
        return (
            <button type="button" className="educational-moment__button" aria-describedby={this.props.ariaDescribedBy}>
                <span className="visually-hidden">{this.props.hiddenText}</span>
                <img className="educational-moment__button-image" src={OpenBookIcon} alt="" />
            </button>
        )
    }

}
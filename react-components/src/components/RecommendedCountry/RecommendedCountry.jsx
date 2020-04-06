import React from 'react';
import PropTypes from 'prop-types';
import './RecommendedCountry.scss';
import Figure from '../Figure/Figure';

export default class RecommendedCountry extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            selected: this.props.country.selected
        };

        this.handleClick = this.handleClick.bind(this);
    }

    componentDidMount() {
    }

    handleClick(e) {
        this.setState({ selected: !this.state.selected });

        /* 
        axios.get(`/load-country?country=${this.props.country.id}`)
            .then(data => { })
            .catch(error => { });
        */

        //dispatch event with country name to be fetch by Country stat section component?
    }

    render() {
        return (
            <button className={`recommended-country ${this.state.selected ? 'recommended-country--selected' : ''}`}
                role="button"
                aria-pressed={this.state.selected}
                id={this.props.country.id}
                onClick={this.handleClick}>

                <Figure image={this.props.country.image} caption={this.props.country.name} />

                <div className="recommended-country__text">{this.state.selected ? 'Selected' : 'Select'}</div>
            </button>
        )
    }

}

RecommendedCountry.propTypes = {
    country: PropTypes.object.isRequired
}

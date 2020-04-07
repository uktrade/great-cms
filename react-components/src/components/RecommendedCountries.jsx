import React from "react";
import PropTypes from "prop-types";
import RecommendedCountry from "./RecommendedCountry/RecommendedCountry";

export default class RecommendedCountries extends React.Component {
  constructor(props) {
    super(props);
    this.countryRef = React.createRef();
  }

  componentDidUpdate(prevProps) {
    if (prevProps.countries !== this.props.countries) {
      this.focusFirstCountry();
    }
  }

  componentDidMount() {
    this.focusFirstCountry();
  }

  focusFirstCountry() {
    this.countryRef.current.querySelectorAll(".recommended-country")[0].focus();
  }

  render() {
    return (
      <ul
        className="grid"
        id="recommended-countries-list"
        ref={this.countryRef}
      >
        {this.props.countries.map((countryData, i) => (
          <li className="c-1-3" key={i}>
            <RecommendedCountry country={countryData} />
          </li>
        ))}
      </ul>
    );
  }
}

RecommendedCountries.propTypes = {
  countries: PropTypes.array.isRequired,
};

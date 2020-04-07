import React from "react";
import PropTypes from "prop-types";
import ReactDOM from "react-dom";
import RecommendedCountries from "./RecommendedCountries";

import Sector from "./Sector";
import { slugify } from "../Helpers";
import Spinner from "./Spinner/Spinner";
import Services from "@src/Services";

class SectorChooser extends React.Component {
  constructor(props) {
    super(props);
    const { selectedSectors: selectedSectors, sectorList: sectorList } = props;

    this.state = {
      sectorList: sectorList,
      selectedSectors: selectedSectors || [],
      savedSelectedSectors: selectedSectors || [],
      showSectorList: false,
      showTooltip: false,
      recommendedCountries: null,
      fetchError: null,
      isLoading: false,
    };

    this.showHideSectorList = this.showHideSectorList.bind(this);
    this.handleMouseOver = this.handleMouseOver.bind(this);
    this.handleMouseOut = this.handleMouseOut.bind(this);
    this.fetchRecommendedCountries = this.fetchRecommendedCountries.bind(this);
  }

  handleSectorButtonClick = (sector) => {
    const { selectedSectors: selectedSectors } = this.state;
    if (selectedSectors.indexOf(sector) > -1) {
      this.removeSector(sector);
    } else {
      this.addSector(sector);
    }
  };

  addSector(sector) {
    const { selectedSectors: selectedSectors } = this.state;
    this.setState({
      selectedSectors: selectedSectors.concat([sector]),
    });
  }

  removeSector(sector) {
    const { selectedSectors: selectedSectors } = this.state;
    const updatedSelectedSectors = selectedSectors.filter(
      (id) => id !== sector
    );
    this.setState({ selectedSectors: updatedSelectedSectors });

    this.fetchRecommendedCountries();
  }

  fetchRecommendedCountries() {
    const { selectedSectors: selectedSectors } = this.state;
    this.setState({
      savedSelectedSectors: selectedSectors,
      isLoading: true,
    });

    Services.get(
      "/export-plan/ajax/recommended-countries",
      { sectors: selectedSectors },
      this.recommendedCountriesFetchSuccess.bind(this),
      this.recommendedCountriesFetchError.bind(this)
    );
  }

  recommendedCountriesFetchSuccess(data) {
    this.setState({
      recommendedCountries: data.data.countries,
      isLoading: false,
    });
  }

  recommendedCountriesFetchError(err) {
    this.setState({
      fetchError: err,
      isLoading: false,
    });
  }

  showHideSectorList() {
    const {
      showSectorList: showSectorList,
      selectedSectors: selectedSectors,
      savedSelectedSectors: savedSelectedSectors,
    } = this.state;
    if (showSectorList) {
      this.setState({ showSectorList: false });
      const isEqual = selectedSectors.every((e) =>
        savedSelectedSectors.includes(e)
      );
      if (!isEqual) {
        this.fetchRecommendedCountries();
      }
    } else {
      this.setState({ showSectorList: true });
      this.setState({ showTooltip: false });
    }
  }

  handleMouseOver(e) {
    this.setState({ showTooltip: true });
  }

  handleMouseOut(e) {
    this.setState({ showTooltip: false });
  }

  render() {
    const {
      showSectorList: showSectorList,
      selectedSectors: selectedSectors,
      sectorList: sectorList,
      showTooltip: showTooltip,
      recommendedCountries: recommendedCountries,
      isLoading: isLoading,
    } = this.state;

    let sectorListDisplay;
    if (showSectorList) {
      sectorListDisplay = (
        <ul className="sector-list" id="sector-list">
          {sectorList.map((sector) => (
            <Sector
              name={sector}
              selected={selectedSectors.indexOf(sector) > -1}
              key={sector}
              id={slugify(sector)}
              handleSectorButtonClick={this.handleSectorButtonClick}
            />
          ))}
        </ul>
      );
    }

    let sectorChooserButton;
    if (!showSectorList) {
      sectorChooserButton = (
        <div className="sector-chooser-button">
          <button
            id="sector-chooser-button"
            type="button"
            className="button--plus"
            onClick={this.showHideSectorList}
            onMouseOver={this.handleMouseOver}
            onMouseOut={this.handleMouseOut}
            aria-describedby="sector-list-tooltip"
          ></button>
          <div
            aria-hidden={!showTooltip}
            id="sector-list-tooltip"
            className={`sector-list-tooltip ${showTooltip ? "" : "hidden"}`}
            role="tooltip"
          >
            Add sectors
          </div>
        </div>
      );
    }

    let saveButton;
    if (selectedSectors.length > 0 && showSectorList) {
      saveButton = (
        <button className="g-button" onClick={this.showHideSectorList}>
          Save
        </button>
      );
    }

    let selectedSectorsDisplay;
    if (selectedSectors.length > 0 && !showSectorList) {
      const currentSelectedSectors = selectedSectors;
      const sectors = currentSelectedSectors.map((sector) => (
        <Sector
          name={sector}
          selected={currentSelectedSectors.indexOf(sector) != -1}
          key={sector}
          id={slugify(sector)}
          handleSectorButtonClick={this.handleSectorButtonClick}
        />
      ));
      selectedSectorsDisplay = (
        <>
          <p className="m-t-0 m-r-xs" id="sector-list-label">
            My sectors
          </p>
          <ul
            className="sector-list"
            id="selected-sectors"
            aria-labelledby="sector-list-label"
          >
            {sectors}
          </ul>
        </>
      );
    }

    return (
      <>
        <h2 className="h-m">Recommended countries</h2>
        <div id="sector-chooser" className="sector-chooser">
          <p className="m-t-0 intro-text">
            Add sectors you're interested in so we can recommend some countries.
          </p>
          {sectorListDisplay}
          {saveButton}
          {selectedSectorsDisplay}
          {sectorChooserButton}
        </div>

        {isLoading ? (
          <Spinner />
        ) : recommendedCountries ? (
          <RecommendedCountries countries={recommendedCountries} />
        ) : (
          ""
        )}
      </>
    );
  }
}

SectorChooser.propTypes = {
  sectorList: PropTypes.array.isRequired,
  selectedSectors: PropTypes.array,
  savedSelectedSectors: PropTypes.array,
};

function createSectorChooser({ element, ...params }) {
  ReactDOM.render(<SectorChooser {...params} />, element);
}

export { SectorChooser, createSectorChooser };

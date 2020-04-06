import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'
import axios from 'axios';
import RecommendedCountries from './RecommendedCountries';

import Sector from './Sector'
import { slugify } from '../Helpers'
import Spinner from './Spinner/Spinner';

const element = document.getElementById('recommended-countries')


class SectorChooser extends React.Component {
  constructor(props) {

    super(props)

    this.state = {
      sectorList: props.sectorList,
      selectedSectors: props.selectedSectors || [],
      savedSelectedSectors: props.selectedSectors || [],
      showSectorList: false,
      showTooltip: false,
      recommendedCountries: null,
      fetchError: null,
      isLoading: false
    }

    this.showHideSectorList = this.showHideSectorList.bind(this)
    this.handleMouseOver = this.handleMouseOver.bind(this)
    this.handleMouseOut = this.handleMouseOut.bind(this)
    this.fetchRecommendedCountries = this.fetchRecommendedCountries.bind(this);
  }

  handleSectorButtonClick = (sector) => {
    if (this.state.selectedSectors.indexOf(sector) > -1) {
      this.removeSector(sector);
    } else {
      this.addSector(sector);
    }
  }

  addSector(sector) {
    this.setState({ selectedSectors: this.state.selectedSectors.concat([sector]) });
  }

  removeSector(sector) {
    const updatedSelectedSectors = this.state.selectedSectors.filter(id => id !== sector);
    this.setState({ selectedSectors: updatedSelectedSectors });

    this.fetchRecommendedCountries();
  }

  fetchRecommendedCountries() {
    this.setState({
      savedSelectedSectors: this.state.selectedSectors,
      isLoading: true
    });

    axios.get('/export-plan/ajax/recommended-countries', {
      params: {
        sectors: this.state.selectedSectors
      },
    }, {
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
      }
    }).then(data => this.setState({
      recommendedCountries: data,
      isLoading: false
    }))
      .catch(error => this.setState({
        fetchError: error,
        isLoading: false
      }));

  }

}

showHideSectorList(e) {
  if (this.state.showSectorList) {
    this.setState({ showSectorList: false });
    const isEqual = this.state.selectedSectors.every(e => this.state.savedSelectedSectors.includes(e))
    if (!isEqual) {
      this.fetchRecommendedCountries();
    }

  } else {
    this.setState({ showSectorList: true })
    this.setState({ showTooltip: false })
  }
}

handleMouseOver(e) {
  this.setState({ showTooltip: true })
}

handleMouseOut(e) {
  this.setState({ showTooltip: false })
}

render() {
  let sectorListDisplay;
  if (this.state.showSectorList) {
    sectorListDisplay = (
      <ul className="sector-list" id="sector-list">
        {
          this.state.sectorList.map((sector) =>
            <Sector
              name={sector}
              selected={this.state.selectedSectors.indexOf(sector) > -1}
              key={sector}
              id={slugify(sector)}
              handleSectorButtonClick={this.handleSectorButtonClick} />
          )
        }
      </ul>
    )
  }

  let sectorChooserButton;
  if (!this.state.showSectorList) {
    sectorChooserButton = (
      <div className="sector-chooser-button">
        <button
          id="sector-chooser-button"
          type="button"
          className="button--plus"
          onClick={this.showHideSectorList}
          onMouseOver={this.handleMouseOver}
          onMouseOut={this.handleMouseOut}
          aria-describedby="sector-list-tooltip"></button>
        <div
          aria-hidden={!this.state.showTooltip}
          id="sector-list-tooltip"
          className={`sector-list-tooltip ${this.state.showTooltip ? '' : 'hidden'}`}
          role="tooltip">Add sectors</div>
      </div>
    )
  }

  let saveButton;
  if (this.state.selectedSectors.length > 0 && this.state.showSectorList) {
    saveButton = (
      <button className="g-button" onClick={this.showHideSectorList}>Save</button>
    )
  }

  let selectedSectorsDisplay;
  if (this.state.selectedSectors.length > 0 && !this.state.showSectorList) {
    const currentSelectedSectors = this.state.selectedSectors;
    const sectors = currentSelectedSectors.map((sector) =>
      <Sector
        name={sector}
        selected={currentSelectedSectors.indexOf(sector) != -1}
        key={sector}
        id={slugify(sector)}
        handleSectorButtonClick={this.handleSectorButtonClick} />
    )
    selectedSectorsDisplay = (
      <>
        <p className="m-t-0 m-r-xs" id="sector-list-label">My sectors</p>
        <ul className="sector-list" id="selected-sectors" aria-labelledby="sector-list-label">
          {sectors}
        </ul>
      </>
    )
  }

  return (
    <>
      <h2 className="h-m">Recommended countries</h2>
      <div id="sector-chooser" className="sector-chooser">
        <p className="m-t-0 intro-text">Add sectors you're interested in so we can recommend some countries.</p>
        {sectorListDisplay}
        {saveButton}
        {selectedSectorsDisplay}
        {sectorChooserButton}
      </div>

      {this.state.isLoading ?
        <Spinner /> :
        this.state.recommendedCountries ?
          <RecommendedCountries countries={this.state.recommendedCountries} /> :
          ''}
    </>
  )
}
}

SectorChooser.propTypes = {
  sectorList: PropTypes.array.isRequired,
  selectedSectors: PropTypes.array,
  savedSelectedSectors: PropTypes.array
}

function createSectorChooser({ element, ...params }) {
  ReactDOM.render(<SectorChooser {...params} />, element)
}

export {
  SectorChooser,
  createSectorChooser,
}

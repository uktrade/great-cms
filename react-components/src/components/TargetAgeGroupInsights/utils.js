export const mapData = ({
  cia_factbook_data,
  country_data,
  population_data,
}) => {
  return {
    population: population_data.total_population
      ? Number((population_data.total_population / 1000).toFixed(1))
      : '',
    cpi: '',
    urban: population_data.urban_percentage
      ? Number((population_data.urban_percentage * 100).toFixed(1))
      : '',
    rural: population_data.rural_percentage
      ? Number((population_data.rural_percentage * 100).toFixed(1))
      : '',
    female: population_data.female_target_age_population
      ? Number((population_data.female_target_age_population / 1000).toFixed(1))
      : '',
    male: population_data.male_target_age_population
      ? Number((population_data.male_target_age_population / 1000).toFixed(1))
      : '',
    internetPercentage: '',
    internetTotal: '',
    targetPopulation: population_data.total_target_age_population
      ? Number((population_data.total_target_age_population / 1000).toFixed(1))
      : '',
    languages: '',
  }
}

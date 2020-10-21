export const mapData = ({ cia_factbook_data, country_data, population_data }) => {
  return {
    population: Number((population_data.total_population/1000).toFixed(1)),
    cpi: Number(country_data.consumer_price_index.value).toFixed(2),
    urban: Number((population_data.urban_percentage * 100).toFixed(1)),
    rural: Number((population_data.rural_percentage * 100).toFixed(1)),
    female: Number((population_data.female_target_age_population/1000).toFixed(1)),
    male: Number((population_data.male_target_age_population/1000).toFixed(1)),
    internet_percentage: Math.floor(country_data.internet_usage.value),
    internet_total: Number(
      ((country_data.internet_usage.value/100) * (population_data.total_population/1000)).toFixed(1)
    ),
    target_population: Number((population_data.total_target_age_population/1000).toFixed(1)),
    target_population_percentage: Math.floor(
      (population_data.total_target_age_population / population_data.total_population) * 100
    ),
    languages: cia_factbook_data.languages ? cia_factbook_data.languages.language.map(({ name }) => name).join(', ') : ''
  }
}

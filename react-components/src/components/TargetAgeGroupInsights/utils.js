export const mapData = ({ cia_factbookdata, country_data, country_population }) => {
  return {
    population: Number(country_population.population_totals.total.toFixed(1)),
    cpi: Number(country_data.consumer_price_index.value.toFixed(2)),
    urban: country_population.population_totals.urban_percentage * 100,
    rural: country_population.population_totals.rural_percentage * 100,
    female: Number(country_population.population_by_age.female_total.toFixed(1)),
    male: Number(country_population.population_by_age.male_total.toFixed(1)),
    internet_percentage: Math.floor(country_data.internet_use_percentage_pop * 100),
    internet_total: Number(
      (country_data.internet_use_percentage_pop * country_population.population_totals.total).toFixed(2)
    ),
    target_population: Number(country_population.population_by_age.total.toFixed(1)),
    target_population_percentage: Math.floor(
      (country_population.population_by_age.total / country_population.population_totals.total) * 100
    ),
    languages: cia_factbookdata.languages.language.map(({ name }) => name).join(', ')
  }
}

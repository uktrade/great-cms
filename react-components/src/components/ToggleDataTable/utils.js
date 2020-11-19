export const mapData = ({
  total_population,
  urban_percentage,
  rural_percentage,
  female_target_age_population,
  male_target_age_population,
  total_target_age_population
}) => {
  return {
    population: total_population ? Number((total_population/1000).toFixed(1)) : '',
    urban: urban_percentage ? Number((urban_percentage * 100).toFixed(1)) : '',
    rural: rural_percentage ? Number((rural_percentage * 100).toFixed(1)) : '',
    female: female_target_age_population ? Number((female_target_age_population/1000).toFixed(1)) : '',
    male: male_target_age_population ? Number((male_target_age_population/1000).toFixed(1)) : '',
    targetPopulation: total_target_age_population ? Number((total_target_age_population/1000).toFixed(1)) : '',
  }
}

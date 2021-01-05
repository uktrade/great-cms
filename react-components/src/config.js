// static values that will not change during execution of the code
// These are set within the base template
export let config = {}
export const setConfig = function ({
  countryDataUrl,
  marketingCountryData,
  removeSectorUrl,
  removeCountryDataUrl,
  countriesBySectorsDataUrl,
  apiLoginUrl,
  apiLogoutUrl,
  apiSignupUrl,
  apiLookupProductUrl,
  apiLookupProductScheduleUrl,
  apiCountriesUrl,
  apiSuggestedCountriesUrl,
  apiUpdateCompanyUrl,
  countryOptions,
  csrfToken,
  dashboardUrl,
  googleUrl,
  industryOptions,
  linkedInUrl,
  loginUrl,
  passwordResetUrl,
  termsUrl,
  verifyCodeUrl,
  userIsAuthenticated,
  apiUpdateExportPlanUrl,
  apiObjectivesCreateUrl,
  apiObjectivesDeleteUrl,
  apiObjectivesUpdateUrl,
  apiRouteToMarketCreateUrl,
  apiRouteToMarketDeleteUrl,
  apiRouteToMarketUpdateUrl,
  exportPlanTargetMarketsUrl,
  signupUrl,
  populationByCountryUrl,
  refreshOnMarketChange,
  apiComTradeDataUrl,
}) {
  config.countryDataUrl = countryDataUrl
  config.marketingCountryData = marketingCountryData
  config.removeSectorUrl = removeSectorUrl
  config.removeCountryDataUrl = removeCountryDataUrl
  config.countriesBySectorsDataUrl = countriesBySectorsDataUrl
  config.apiLoginUrl = apiLoginUrl
  config.apiLogoutUrl = apiLogoutUrl
  config.apiSignupUrl = apiSignupUrl
  config.apiLookupProductUrl = apiLookupProductUrl
  config.apiLookupProductScheduleUrl = apiLookupProductScheduleUrl
  config.apiCountriesUrl = apiCountriesUrl
  config.apiSuggestedCountriesUrl = apiSuggestedCountriesUrl
  config.apiUpdateCompanyUrl = apiUpdateCompanyUrl
  config.apiUpdateExportPlanUrl = apiUpdateExportPlanUrl
  config.apiObjectivesCreateUrl = apiObjectivesCreateUrl
  config.apiObjectivesDeleteUrl = apiObjectivesDeleteUrl
  config.apiObjectivesUpdateUrl = apiObjectivesUpdateUrl
  config.apiRouteToMarketCreateUrl = apiRouteToMarketCreateUrl
  config.apiRouteToMarketDeleteUrl = apiRouteToMarketDeleteUrl
  config.apiRouteToMarketUpdateUrl = apiRouteToMarketUpdateUrl
  config.countryOptions = countryOptions
  config.csrfToken = csrfToken
  config.dashboardUrl = dashboardUrl
  config.googleUrl = googleUrl
  config.industryOptions = industryOptions
  config.linkedInUrl = linkedInUrl
  config.loginUrl = loginUrl
  config.passwordResetUrl = passwordResetUrl
  config.termsUrl = termsUrl
  config.verifyCodeUrl = verifyCodeUrl
  config.userIsAuthenticated = userIsAuthenticated
  config.exportPlanTargetMarketsUrl = exportPlanTargetMarketsUrl
  config.signupUrl = signupUrl
  config.populationByCountryUrl = populationByCountryUrl
  config.refreshOnMarketChange = refreshOnMarketChange
  config.apiComTradeDataUrl = apiComTradeDataUrl
}

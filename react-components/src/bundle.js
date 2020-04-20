import '../../core/sass/main.scss'

import ProductsModal from '@src/views/ProductsModal/Base'
import SignupModal from '@src/views/SignupModal/Base'
import IndustriesModal from '@src/views/IndustriesModal/Base'
import CountriesModal from '@src/views/CountriesModal/Base'
import Countries from '@src/views/Countries/Base'
import LoginModal from '@src/views/LoginModal/Modal'
import MarketSelectNavbar from '@src/views/MarketSelectNavbar/Base'
import Tour from '@src/views/Tour/Base'
import { createTargetMarketCountries } from '@src/components/TargetMarketCountries'
import { STEP_CREDENTIALS, STEP_VERIFICATION_CODE } from '@src/views/SignupModal/Wizard/'
import Services from '@src/Services'
import '@babel/polyfill'

//initialise common components automatically based on selectors
import ComponentInitialiser from './initialisers/common.initialiser'
new ComponentInitialiser();

export default {
  CountriesModal,
  createTargetMarketCountries,
  MarketSelectNavbar,
  Countries,
  IndustriesModal,
  LoginModal,
  setConfig: Services.setConfig,
  SignupModal,
  ProductsModal,
  STEP_CREDENTIALS,
  STEP_VERIFICATION_CODE,
  Tour,
}

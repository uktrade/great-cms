import '../../core/sass/main.scss'


import SignupModal from '@src/views/SignupModal/Container'
import ProductsModal from '@src/views/ProductsModal/Container'
import CountriesModal from '@src/views/CountriesModal/Container'
import IndustriesModal from '@src/views/IndustriesModal/Base'
import Countries from '@src/views/Countries/Container'
import LoginModal from '@src/views/LoginModal/Modal'
import MarketSelectNavbar from '@src/views/MarketSelectNavbar/Container'
import Tour from '@src/views/Tour/Base'
import { createTargetMarketCountries } from '@src/components/TargetMarketCountries'
import { STEP_CREDENTIALS, STEP_VERIFICATION_CODE } from '@src/views/SignupModal/Wizard/'
import Services from '@src/Services'
import '@babel/polyfill'

export default {
  CountriesModal,
  createTargetMarketCountries,
  MarketSelectNavbar,
  ProductsModal,
  Countries,
  IndustriesModal,
  LoginModal,
  setConfig: Services.setConfig,
  setInitialState: Services.setInitialState,
  SignupModal,
  STEP_CREDENTIALS,
  STEP_VERIFICATION_CODE,
  Tour,
}

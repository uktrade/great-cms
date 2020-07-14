import '../../core/sass/main.scss'

import Signup from '@src/views/Signup/Container'
import SignupModal from '@src/views/SignupModal/Container'
import ProductsModal from '@src/views/ProductsModal/Container'
import CountriesModal from '@src/views/CountriesModal/Container'
import IndustriesModal from '@src/views/IndustriesModal/Container'
import Countries from '@src/views/Countries/Container'
import ProductLookup from '@src/views/ProductLookup/Container'
import LoginModal from '@src/views/LoginModal/Modal'
import MarketSelectNavbar from '@src/views/MarketSelectNavbar/Container'
import Tour from '@src/views/Tour/Container'
import { createTargetAgeGroups } from '@src/components/TargetAgeGroups'
import { createTargetMarketCountries } from '@src/components/TargetMarketCountries'
import { createBrandAndProductForm } from '@src/components/BrandAndProduct'
import { createBusinessRationale } from '@src/components/BusinessRationale'
import LearnIntroduction from '@src/views/LearnIntroduction/LearnIntroduction'
import { STEP_CREDENTIALS, STEP_VERIFICATION_CODE } from '@src/views/SignupModal/Component/'
import Services from '@src/Services'
import '@babel/polyfill'

export default {
  Countries,
  CountriesModal,
  createTargetAgeGroups,
  createTargetMarketCountries,
  createBusinessRationale,
  createBrandAndProductForm,
  IndustriesModal,
  LearnIntroduction,
  ProductLookup,
  LoginModal,
  MarketSelectNavbar,
  ProductsModal,
  setConfig: Services.setConfig,
  setInitialState: Services.setInitialState,
  Signup,
  SignupModal,
  STEP_CREDENTIALS,
  STEP_VERIFICATION_CODE,
  Tour
}

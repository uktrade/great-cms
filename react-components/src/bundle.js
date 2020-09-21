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
import ProductFinder from '@src/components/ProductFinder/ProductFinder'
import CountryFinder from '@src/components/ProductFinder/CountryFinder'
import { createRouteToMarket, createSpendingAndResources } from '@src/views/sections/MarketingApproach'
import { aboutYourBusinessForm } from '@src/views/sections/AboutYourBusiness'
import { adaptToTargetMarketForm } from '@src/views/sections/AdaptationForYourTargetMarket'
import { sectionSidebar } from '@src/views/sections'
import { createMarkLessonAsComplete } from '@src/components/MarkLessonAsComplete/MarkLessonAsComplete'
import { createTargetAgeGroupInsights } from '@src/components/TargetAgeGroupInsights/TargetAgeGroupInsights'
import { createTargetMarketCountries } from '@src/components/TargetMarketCountries'
import { createBusinessRationale } from '@src/components/BusinessRationale'
import { createObjectivesList } from '@src/components/ObjectivesList'
import LearnIntroduction from '@src/views/LearnIntroduction/LearnIntroduction'
import { STEP_CREDENTIALS, STEP_VERIFICATION_CODE } from '@src/views/SignupModal/Component/'
import Services from '@src/Services'
import '@babel/polyfill'

export default {
  Countries,
  CountriesModal,
  createMarkLessonAsComplete,
  createRouteToMarket,
  aboutYourBusinessForm,
  adaptToTargetMarketForm,
  createSpendingAndResources,
  createTargetAgeGroupInsights,
  createTargetMarketCountries,
  createBusinessRationale,
  createObjectivesList,
  IndustriesModal,
  LearnIntroduction,
  ProductLookup,
  ProductFinder,
  CountryFinder,
  LoginModal,
  MarketSelectNavbar,
  ProductsModal,
  setConfig: Services.setConfig,
  setInitialState: Services.setInitialState,
  Signup,
  SignupModal,
  STEP_CREDENTIALS,
  STEP_VERIFICATION_CODE,
  Tour,
  sectionSidebar
}

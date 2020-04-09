import '../../core/sass/main.scss'

import ExportModal from '@src/views/ExportModal/Base'
import SignupModal from '@src/views/SignupModal/Base'
import IndustriesModal from '@src/views/IndustriesModal/Base'
import CountriesModal from '@src/views/CountriesModal/Base'
import LoginModal from '@src/views/LoginModal/Modal'
import Tour from '@src/views/Tour/Base'
import { createTargetMarketCountries } from '@src/components/TargetMarketCountries'
import { STEP_CREDENTIALS, STEP_VERIFICATION_CODE } from '@src/views/SignupModal/Wizard/'
import Services from '@src/Services'
import '@babel/polyfill'

export default {
  CountriesModal,
  createTargetMarketCountries,
  IndustriesModal,
  LoginModal,
  setConfig: Services.setConfig,
  SignupModal,
  ExportModal,
  STEP_CREDENTIALS,
  STEP_VERIFICATION_CODE,
  Tour,
}

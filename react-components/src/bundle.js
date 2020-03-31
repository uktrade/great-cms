import '../../core/sass/main.scss'

import SignupModal from '@src/views/SignupModal/Base'
import IndustriesModal from '@src/views/IndustriesModal/Base'
import CountriesModal from '@src/views/CountriesModal/Base'
import LoginModal from '@src/views/LoginModal/Modal'
import Tour from '@src/views/Tour/Base'
import { createSectorChooser } from '@src/components/SectorChooser'
import {STEP_CREDENTIALS, STEP_VERIFICATION_CODE} from '@src/views/SignupModal/Wizard/'
import Services from '@src/Services'
import '@babel/polyfill'

export default {
  setConfig: Services.setConfig,
  SignupModal,
  LoginModal,
  Tour,
  createSectorChooser,
  IndustriesModal,
  CountriesModal,
  STEP_CREDENTIALS,
  STEP_VERIFICATION_CODE,
};

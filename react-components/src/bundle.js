import '../../core/sass/main.scss'

import SignupModal from '@src/views/SignupModal/Modal'
import QuestionModal from '@src/views/QuestionModal/Modal'
import LoginModal from '@src/views/LoginModal/Modal'
import Tour from '@src/views/Tour/Base'
import SectorChooser from '@src/components/SectorChooser'
import {STEP_CREDENTIALS, STEP_VERIFICATION_CODE} from '@src/views/SignupModal/Wizard/'
import Services from '@src/Services'
import '@babel/polyfill'

export default {
  setConfig: Services.setConfig,
  SignupModal,
  LoginModal,
  Tour,
  SectorChooser,
  QuestionModal,
  STEP_CREDENTIALS,
  STEP_VERIFICATION_CODE,
};

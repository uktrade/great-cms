import '../../core/sass/main.scss'

import SignupModal from '@src/views/SignupModal/Modal'
import QuestionModal from '@src/views/QuestionModal/Modal'
import LoginModal from '@src/views/LoginModal/Modal'
import Tour from '@src/views/Tour/Base'
import { createSectorChooser } from '@src/components/SectorChooser'
import {STEP_CREDENTIALS, STEP_VERIFICATION_CODE} from '@src/views/SignupModal/Wizard/'
import Services from '@src/Services'
import '@babel/polyfill'

export default {
  createSectorChooser,
  LoginModal,
  QuestionModal,
  setConfig: Services.setConfig,
  SignupModal,
  STEP_CREDENTIALS,
  STEP_VERIFICATION_CODE,
  Tour,
};

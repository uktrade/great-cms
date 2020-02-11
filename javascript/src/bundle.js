import SignupModal from './SignupModal'
import {STEP_CREDENTIALS, STEP_VERIFICATION_CODE} from './SignupWizard'
import Services from './Services'
import '@babel/polyfill'

export default {
  setConfig: Services.setConfig,
  SignupModal,
  STEP_CREDENTIALS,
  STEP_VERIFICATION_CODE,
};

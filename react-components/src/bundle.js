import LaunchModal from '@src/components/PageModalManager'
import Signup from '@src/views/Signup/Container'
import SignupModal from '@src/views/SignupModal/Container'

import { createLogin } from '@src/views/Login'
import Questionnaire from '@src/components/Segmentation/Questionnaire'
import ProductFinderButton from '@src/components/ProductFinder/ProductFinderButton'
import CountryFinderButton from '@src/components/ProductFinder/CountryFinderButton'
import CompareMarkets from '@src/components/CompareMarkets'
import createSnackbar from '@src/components/Snackbar/Snackbar'
import createExportPlanWizard from '@src/components/ExportPlanWizard/ExportPlanCreate'
import {
  createRouteToMarket,
  createSpendingAndResources,
  createTargetAgeGroupInsights,
} from '@src/views/sections/MarketingApproach'
import { aboutYourBusinessForm } from '@src/views/sections/AboutYourBusiness'
import {
  fundingCreditTotalExportCost,
  fundingCreditHowMuchFunding,
  fundingCreditFundingCreditOptions,
} from '@src/views/sections/FundingCredit/FundingCredit'
import { createGettingPaid } from '@src/views/sections/GettingPaid'
import {
  createTargetMarketResearchForm,
  createDataSnapShot,
} from '@src/views/sections/TargetMarketResearch'
import {
  adaptToTargetMarketForm,
  documentsForTargetMarketForm,
  statsForYourTargetMarket,
} from '@src/views/sections/AdaptationForYourTargetMarket'
import {
  createObjectivesReasons,
  createObjectivesList,
} from '@src/views/sections/Objectives'
import { createCostsAndPricing } from '@src/views/sections/CostsAndPricing'
import {
  travelPlanSnapshot,
  travelPlanCultureRules,
  travelPlanVisaInformation,
  plannedTravel,
} from '@src/views/sections/TravelPlan/TravelPlan'
import { businessRisks } from '@src/views/sections/BusinessRisk/BusinessRisk'

import { createDashboard } from '@src/views/sections/Dashboard'
import { sectionSidebar, sectionComplete } from '@src/views/sections'
import { createMarkLessonAsComplete } from '@src/components/MarkLessonAsComplete/MarkLessonAsComplete'
import { createVideoTranscript } from '@src/components/VideoTranscript/VideoTranscript'
import { createCaseStudy } from '@src/components/CaseStudy/CaseStudy'
import { createComingSoonModal } from '@src/components/Lesson/ComingSoon'
import { createProductPicker } from '@src/components/ProductPicker'
import {
  STEP_CREDENTIALS,
  STEP_VERIFICATION_CODE,
} from '@src/components/Signup/'
import Services from '@src/Services'
import { formatLessonLearned } from '@src/Helpers'
import { setConfig } from '@src/config'
import '@babel/polyfill'

export default {
  createMarkLessonAsComplete,
  createRouteToMarket,
  aboutYourBusinessForm,
  createTargetMarketResearchForm,
  createDataSnapShot,
  adaptToTargetMarketForm,
  documentsForTargetMarketForm,
  statsForYourTargetMarket,
  createComingSoonModal,
  createSpendingAndResources,
  createTargetAgeGroupInsights,
  createGettingPaid,
  createObjectivesList,
  createObjectivesReasons,
  createVideoTranscript,
  createDashboard,
  createCaseStudy,
  createCostsAndPricing,
  fundingCreditTotalExportCost,
  fundingCreditHowMuchFunding,
  fundingCreditFundingCreditOptions,
  travelPlanSnapshot,
  travelPlanCultureRules,
  travelPlanVisaInformation,
  plannedTravel,
  businessRisks,
  ProductFinderButton,
  CountryFinderButton,
  CompareMarkets,
  createLogin,
  setConfig,
  setInitialState: Services.setInitialState,
  LaunchModal,
  Signup,
  SignupModal,
  STEP_CREDENTIALS,
  STEP_VERIFICATION_CODE,
  Questionnaire,

  sectionSidebar,
  sectionComplete,
  formatLessonLearned,
  createExportPlanWizard,
  createSnackbar,
  createProductPicker,
}

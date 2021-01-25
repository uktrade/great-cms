import Signup from '@src/views/Signup/Container'
import SignupModal from '@src/views/SignupModal/Container'

import { createLogin } from '@src/views/Login'
import Tour from '@src/views/Tour/Container'
import ProductFinderButton from '@src/components/ProductFinder/ProductFinderButton'
import CountryFinderButton from '@src/components/ProductFinder/CountryFinderButton'
import ModalMenu from '@src/components/ModalMenu'
import CompareMarkets from '@src/components/CompareMarkets'
import SelectComparisonMarket from '@src/components/CompareMarkets/SelectMarket'
import {
  createRouteToMarket,
  createSpendingAndResources,
  createTargetAgeGroupInsights,
} from '@src/views/sections/MarketingApproach'
import { aboutYourBusinessForm } from '@src/views/sections/AboutYourBusiness'
import {
  financeTotalExportCost,
  financeHowMuchFunding,
  financeFundingCreditOptions,
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
  createDashboard,
  createDisabledButton,
} from '@src/views/sections/Dashboard'
import { sectionSidebar } from '@src/views/sections'
import { createMarkLessonAsComplete } from '@src/components/MarkLessonAsComplete/MarkLessonAsComplete'
import { createVideoTranscript } from '@src/components/VideoTranscript/VideoTranscript'
import { createCaseStudy } from '@src/components/CaseStudy/CaseStudy'
import { createComingSoonModal } from '@src/components/Lesson/ComingSoon'
import {
  STEP_CREDENTIALS,
  STEP_VERIFICATION_CODE,
} from '@src/views/SignupModal/Component/'
import Services from '@src/Services'
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
  createDisabledButton,
  createCaseStudy,
  createCostsAndPricing,
  financeTotalExportCost,
  financeHowMuchFunding,
  financeFundingCreditOptions,
  ProductFinderButton,
  CountryFinderButton,
  CompareMarkets,
  SelectComparisonMarket,
  ModalMenu,
  createLogin,
  setConfig,
  setInitialState: Services.setInitialState,
  Signup,
  SignupModal,
  STEP_CREDENTIALS,
  STEP_VERIFICATION_CODE,
  Tour,
  sectionSidebar,
}

import fetchMock from 'fetch-mock'
import '@testing-library/jest-dom'
import 'regenerator-runtime/runtime'

global.fetch = fetchMock

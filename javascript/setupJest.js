import fetchMock from 'fetch-mock';
import expect from 'expect'
import enzymify from 'expect-enzyme'

expect.extend(enzymify())

global.fetch = fetchMock

import React from 'react'
import ReactDOM from 'react-dom'
import { act, Simulate } from 'react-dom/test-utils'
import ModalMenu from '@src/components/ModalMenu'

let button
let container

beforeEach(() => {
  container = document.createElement('div')
  document.body.appendChild(container)
  container.innerHTML = '<li id="header-link-user-profile"></li>'
  act(() => {
    ModalMenu({ element: container, avatar:'', authenticated:true, user_name:'Noman' })
  })
  button = container.querySelector('button')
})

afterEach(() => {
  document.body.removeChild(container)
})

it('Opens menu and escape to close', () => {
  expect(document.body.querySelector('.menu-items')).toBeFalsy()
  act(() => {
    Simulate.click(button)
  })
  let menu = document.body.querySelector('.menu-items')
  expect(menu).toBeTruthy()
  //  Press escape to close
  Simulate.keyDown(menu, { keyCode: 27 })
  Simulate.keyUp(menu, { keyCode: 27 })
  expect(document.body.querySelector('.menu-items')).toBeFalsy() 
})

it('Open and click to close', () => {
  expect(document.body.querySelector('.menu-items')).toBeFalsy()
  act(() => {
    Simulate.click(button)
  })
  let menu = document.body.querySelector('.menu-items')
  expect(menu).toBeTruthy()
  // Check close on click off
  act(() => {
    Simulate.click(document.body.querySelector('.ReactModal__Overlay'))
  })  
  expect(document.body.querySelector('.menu-items')).toBeFalsy()  
})

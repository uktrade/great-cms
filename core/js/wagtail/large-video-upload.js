import * as utils from './utils'

export const largeVideoUpload = () => {
  const isAddVideoPage = utils.isAddVideoPage(window.location.pathname)
  const isEditVideoPage = utils.isEditVideoPage(window.location.pathname)

  if (isAddVideoPage || isEditVideoPage) {
    const uploadFileInput = document.querySelector('#id_file')

    let file
    let isLargeVideo = false
    let _key
    let form = document.querySelector('form[action="/admin/media/video/add/"]')
    let isInitialised = false

    if (isEditVideoPage) {
      form = document.querySelector('form[action^="/admin/media/edit/"]')
    }

    function enableLargeVideoUpload() {
      isLargeVideo = true
      utils.showHideElements(
        '#large_video_submit',
        '.fields button[type="submit"]'
      )
    }

    function enableLargeVideoSave() {
      isLargeVideo = true
      utils.showHideElements(
        '#large_video_submit',
        '.fields input[type="submit"]',
        'inline-block'
      )
    }

    const getSignedUrl = async () => {
      const body = {
        fileName: file.name,
        fileType: file.type,
      }

      const response = await fetch('/api/signed-url/', {
        method: 'POST',
        body: JSON.stringify(body),
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': document.querySelector(
            "input[name='csrfmiddlewaretoken']"
          ).value,
        },
      })

      const { url, key } = await response.json()

      _key = key

      return url
    }

    const updateStatus = (message) => {
      const progressBar = document.querySelector('#progress_bar')
      const status = document.querySelector('#status')

      status.innerHTML = message
      progressBar.style.display = 'none'
    }

    const uploadFile = async (signedUrl) => {
      const progressBar = document.querySelector('#progress_bar')
      progressBar.style.display = 'block'

      const status = document.querySelector('#status')
      const ajax = new XMLHttpRequest()

      ajax.upload.addEventListener(
        'progress',
        (event) => {
          const percent = Math.round((event.loaded / event.total) * 100)
          status.innerHTML = percent + '% uploaded'
          progressBar.value = percent
        },
        false
      )
      ajax.addEventListener(
        'loadend',
        () => {
          updateStatus('Upload Complete')

          loadendHandler()
        },
        false
      )
      ajax.addEventListener(
        'error',
        () => {
          updateStatus('Upload Failed')
        },
        false
      )
      ajax.addEventListener(
        'abort',
        () => {
          updateStatus('Upload Aborted')
        },
        false
      )
      ajax.open('PUT', signedUrl)
      ajax.setRequestHeader('Content-Type', 'binary/octet-stream')
      ajax.send(file)
    }

    const handleSubmit = async () => {
      const signedUrl = await getSignedUrl()

      if (signedUrl) {
        uploadFile(signedUrl)
      }
    }

    const getFormData = () => {
      const formData = new FormData(document.forms[1])

      formData.delete('file')
      formData.append(
        'file',
        new File([new Blob(['xyz'])], _key, {
          name: _key,
          lastModified: new Date().valueOf(),
          lastModifiedDate: new Date(),
          size: 1,
          type: 'video/mp4',
        })
      )

      return formData
    }

    const loadendHandler = async () => {
      await fetch('/admin/media/video/add/', {
        method: 'POST',
        body: getFormData(),
        headers: {
          'X-CSRFToken': document.querySelector(
            "input[name='csrfmiddlewaretoken']"
          ).value,
        },
        redirect: 'follow',
      }).then((res) => {
        if (res.redirected) {
          window.location = res.url
        }
      })
    }

    const createLargeVideoSubmitButton = () => {
      const submit = utils.createElement('button', [
        { key: 'type', val: 'submit' },
        { key: 'id', val: 'large_video_submit' },
        { key: 'classList', val: 'button' },
        { key: 'innerHTML', val: isAddVideoPage ? 'Upload' : 'Save' },
      ])

      submit.style.display = 'none'

      submit.addEventListener('click', (event) => {
        event.preventDefault()

        if (file && isLargeVideo) {
          handleSubmit()
        }
      })

      if (isAddVideoPage) {
        form.append(submit)
      }

      if (isEditVideoPage) {
        form.querySelector('.fields > li:last-child').prepend(submit)
      }
    }

    const createProgressBar = () => {
      const progressBar = utils.createElement('progress', [
        { key: 'id', val: 'progress_bar' },
        { key: 'max', val: '100' },
        { key: 'value', val: '0' },
      ])

      progressBar.style.display = 'none'

      form.append(progressBar)
    }

    const createStatusMessage = () => {
      const statusMessage = utils.createElement('h3', [
        { key: 'id', val: 'status' },
      ])

      form.append(statusMessage)
    }

    function setup() {
      uploadFileInput.addEventListener('change', (event) => {
        file = event.target.files[0]

        if (!isInitialised) {
          createLargeVideoSubmitButton()
          createStatusMessage()
          createProgressBar()

          if (isAddVideoPage) {
            enableLargeVideoUpload()
          }

          if (isEditVideoPage) {
            enableLargeVideoSave()
          }

          isInitialised = true
        }
      })
    }

    window.addEventListener('DOMContentLoaded', () => setup())
  }
}

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

    function disableLargeVideoUpload() {
      isLargeVideo = false
      utils.showHideElements(
        '.fields button[type="submit"]',
        '#large_video_submit'
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

    const uploadFile = async (signedUrl) => {
      const progressBar = document.querySelector('#progress_bar')
      progressBar.style.display = 'block'

      const formdata = new FormData()
      formdata.append('file', file)
      const ajax = new XMLHttpRequest()
      ajax.upload.addEventListener(
        'progress',
        (event) => {
          progressBar.value = Math.round((event.loaded / event.total) * 100)
        },
        false
      )
      ajax.addEventListener('loadend', loadendHandler, false)
      ajax.open('PUT', signedUrl)
      ajax.setRequestHeader('Content-Type', 'binary/octet-stream')
      ajax.send(formdata)
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
          lastModified: 1680183083519,
          lastModifiedDate: new Date(),
          size: 7942351,
          type: 'video/mp4',
          webkitRelativePath: '',
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

    function setup() {
      uploadFileInput.addEventListener('change', (event) => {
        file = event.target.files[0]

        if (file.size > 100000) {
          createLargeVideoSubmitButton()
          createProgressBar()

          if (isAddVideoPage) {
            enableLargeVideoUpload()
          }

          if (isEditVideoPage) {
            enableLargeVideoSave()
          }
        } else {
          disableLargeVideoUpload()
        }
      })
    }

    setup()
  }
}

import { connect } from 'socket.io-client'
const Chart = require('Chart.js')

document.addEventListener('DOMContentLoaded', () => {
  const socket = connect()

  // our selection elements
  const ghSelect = document.getElementById('gh-select')
  const variableSelect = document.getElementById('variable-select')
  // const modeSelect = document.getElementById('mode-select')

  // their corresponding selected values
  let gh = Number(ghSelect.value)
  let variable = variableSelect.value
  // let mode = modeSelect.value

  // chart details
  const limit = 10
  let lastData = 0
  let data = []
  let labels = []
  let title = `${variableSelect.options[variableSelect.selectedIndex].text} of Greenhouse ${gh}`
  let chart = new Chart(
    document.getElementById('chart'),
    {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: title,
            data
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true
      }
    }
  )

  // creates a new blank chart
  function resetChart () {
    lastData = 0
    data = []
    labels = []
    title = `${variableSelect.options[variableSelect.selectedIndex].text} of Greenhouse ${gh}`
    chart.destroy()
    chart = new Chart(
      document.getElementById('chart'),
      {
        type: 'line',
        data: {
          labels,
          datasets: [
            {
              label: title,
              data
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true
        }
      }
    )
  }

  // selection change handlers
  ghSelect.addEventListener('change', function () {
    gh = Number(ghSelect.value)
    resetChart()
  })

  variableSelect.addEventListener('change', function () {
    variable = variableSelect.value
    resetChart()
  })

  //   modeSelect.addEventListener('change', function () {
  //     mode = modeSelect.value
  //     resetChart()
  //   })

  socket.on('serial', (json) => {
    json = JSON.parse(json)

    // we are only interested in the data pertaining to the selected greenhouse
    if (json.id === gh) {
      switch (variable) {
        case 'temp':
          lastData = json.temp
          break
        case 'humidity':
          lastData = json.humidity
          break
        case 'soilT':
          lastData = json.soilT
          break
        case 'soilM':
          lastData = json.soilM
          break
        case 'lightS':
          lastData = json.lightS
          break
      }
      chart.update()
    }
  })

  // every second create a new chart entry, regardless of if we received data or not
  setInterval(() => {
    const now = new Date()
    const hours = String(now.getHours()).padStart(2, '0')
    const minutes = String(now.getMinutes()).padStart(2, '0')
    const seconds = String(now.getSeconds()).padStart(2, '0')

    // keep chart to past 10 seconds
    if (labels.length > limit) {
      labels.shift()
      data.shift()
    }

    labels.push(`${hours}:${minutes}:${seconds}`)
    data.push(lastData)
    chart.update()
  }, 1000)
})

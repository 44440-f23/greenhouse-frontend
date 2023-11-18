import { connect } from 'socket.io-client'

// only runs our js code after the page has loaded
document.addEventListener('DOMContentLoaded', function () {
  // our greenhouse elements
  const gh1 = document.getElementById('1')
  const gh2 = document.getElementById('2')
  const gh3 = document.getElementById('3')
  const gh4 = document.getElementById('4')
  const gh5 = document.getElementById('5')
  const gh6 = document.getElementById('6')

  // const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
  // const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))

  // create our socket
  // https://socket.io/
  const socket = connect()

  // event listeners that come with socket io
  socket.on('connect', () => {
    console.log('Socket connection to server successful.')
  })

  // Disconecting
  socket.on('disconnect', (msg) => {
    console.log('Socket disconnected, reason: ' + msg)
  })

  // Connection error
  socket.on('connect_error', (msg) => {
    console.log('Error while connecting socket to server, reason: ' + msg)
  })

  // most likely wont be needed in this file, but here for an example/use later
  socket.on('config', (recievedConfigs) => {
    recievedConfigs = JSON.parse(recievedConfigs)
    console.log('These are the current configs: ' + JSON.stringify(recievedConfigs))
  })

  // our custom event that is emitted from out app.py
  socket.on('serial', (data) => {
    try {
      data = JSON.parse(data)
    } catch (e) {
      console.log('failed to parse: ' + data + ' because: ' + e)
    }

    // check the data id, and add information as necessary
    if (data.id === 1) {
      gh1.querySelector('.temp').innerText = parseInt(data.temp) ?? '-'
      gh1.querySelector('.humidity').innerText = parseInt(data.humidity) ?? '-'
      // gh1.querySelector(".soil-temp").innerText = parseInt(data.soilT) ?? "-"
      // gh1.querySelector(".soil-moisture").innerText = parseInt(data.soilM) ?? "-"
      gh1.querySelector('.lux').innerText = parseInt(data.lightS) ?? '-'
    } else if (data.id === 2) {
      gh2.querySelector('.temp').innerText = parseInt(data.temp) ?? '-'
      gh2.querySelector('.humidity').innerText = parseInt(data.humidity) ?? '-'
      // gh2.querySelector(".soil-temp").innerText = parseInt(data.soilT) ?? "-"
      // gh2.querySelector(".soil-moisture").innerText = parseInt(data.soilM) ?? "-"
      gh2.querySelector('.lux').innerText = parseInt(data.lightS) ?? '-'
    } else if (data.id === 3) {
      gh3.querySelector('.temp').innerText = parseInt(data.temp) ?? '-'
      gh3.querySelector('.humidity').innerText = parseInt(data.humidity) ?? '-'
      // gh3.querySelector(".soil-temp").innerText = parseInt(data.soilT) ?? "-"
      // gh3.querySelector(".soil-moisture").innerText = parseInt(data.soilM) ?? "-"
      gh3.querySelector('.lux').innerText = parseInt(data.lightS) ?? '-'
    } else if (data.id === 4) {
      gh4.querySelector('.temp').innerText = parseInt(data.temp) ?? '-'
      gh4.querySelector('.humidity').innerText = parseInt(data.humidity) ?? '-'
      // gh4.querySelector(".soil-temp").innerText = parseInt(data.soilT) ?? "-"
      // gh4.querySelector(".soil-moisture").innerText = parseInt(data.soilM) ?? "-"
      gh4.querySelector('.lux').innerText = parseInt(data.lightS) ?? '-'
    } else if (data.id === 5) {
      gh5.querySelector('.temp').innerText = parseInt(data.temp) ?? '-'
      gh5.querySelector('.humidity').innerText = parseInt(data.humidity) ?? '-'
      // gh5.querySelector(".soil-temp").innerText = parseInt(data.soilT) ?? "-"
      // gh5.querySelector(".soil-moisture").innerText = parseInt(data.soilM) ?? "-"
      gh5.querySelector('.lux').innerText = parseInt(data.lightS) ?? '-'
    } else if (data.id === 6) {
      gh6.querySelector('.temp').innerText = parseInt(data.temp) ?? '-'
      gh6.querySelector('.humidity').innerText = parseInt(data.humidity) ?? '-'
      // gh6.querySelector(".soil-temp").innerText = parseInt(data.soilT) ?? "-"
      // gh6.querySelector(".soil-moisture").innerText = parseInt(data.soilM) ?? "-"
      gh6.querySelector('.lux').innerText = parseInt(data.lightS) ?? '-'
    }
  })
})

document.addEventListener("DOMContentLoaded", () => {
    const socket = io.connect()

    // our selection elements 
    let gh_select = document.getElementById('gh-select')
    let variable_select = document.getElementById('variable-select')    
    let mode_select = document.getElementById('mode-select')

    // their corresponding selected values
    let gh = Number(gh_select.value)
    let variable = variable_select.value
    let mode = mode_select.value

    // chart details
    let limit = 10
    let lastData = 0
    let data = []
    let labels = []
    let title = `${variable_select.options[variable_select.selectedIndex].text} of Greenhouse ${gh}`
    let chart = new Chart(
        document.getElementById('chart'),
        {
          type: 'line',
          data: {
            labels: labels,
            datasets: [
              {
                label: title,
                data: data
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
    function resetChart() {
        lastData = 0
        data = []
        labels = []
        title = `${variable_select.options[variable_select.selectedIndex].text} of Greenhouse ${gh}`
        chart.destroy()
        chart = new Chart(
            document.getElementById('chart'),
            {
              type: 'line',
              data: {
                labels: labels,
                datasets: [
                  {
                    label: title,
                    data: data
                  }
                ]
              },
              options: {
                responsive: true,
                maintainAspectRatio: true
            }
            }
        )

        updateChart()
    }


    // selection change handlers
    gh_select.addEventListener('change', function () {
        gh = Number(gh_select.value)
        resetChart()
    })

    variable_select.addEventListener('change', function () {
        variable = variable_select.value
        resetChart()
    })

    mode_select.addEventListener('change', function () {
        mode = mode_select.value
        resetChart()
    })    

    socket.on("serial", (json) => {
        json = JSON.parse(json)
        
        // we are only interested in the data pertaining to the selected greenhouse
        if (json.id == gh) {
            switch (variable) {
                case "temp":
                    lastData = json.temp
                    break
                case "humidity":
                    lastData = json.humidity
                    break
                case "soilT":
                    lastData = json.soilT
                    break
                case "soilM":
                    lastData = json.soilM
                    break
                case "lightS":
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
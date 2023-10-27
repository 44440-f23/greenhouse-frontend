// only runs our js code after the page has loaded
document.addEventListener('DOMContentLoaded', function() {
    // create our socket 
    // https://socket.io/
    const socket = io.connect()

    // our nice line chart
    // https://www.chartjs.org/
    const chart = new Chart(document.getElementById("chart"), {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Temperature',
                data: [],
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        // options: {
        //     scales: {
        //         y: {
        //             min: 0
        //         }
        //     }
        // }
    });

    // a helper function that gets the current time for us in a nice format for our x values
    function getCurrentTime() {
        const now = new Date()
        const hours = now.getHours().toString().padStart(2, '0')
        const minutes = now.getMinutes().toString().padStart(2, '0')
        const seconds = now.getSeconds().toString().padStart(2, '0')
      
        return `${hours}:${minutes}:${seconds}`
    }

    // event listeners that come with socket io 
    socket.on("connect", () => {
        console.log("Socket connection to server successful.")
    })

    socket.on("disconnect", (msg) => {
        console.log("Socket disconnected, reason: " + msg)
    })

    socket.on("connect_error", (msg) => {
        console.log('Error while connecting socket to server, reason: ' + msg)
    })

    // our custom event that is emitted from out app.py
    socket.on("serial", (data) => {
        // add the current time to the list of X labels
        chart.data.labels.push(getCurrentTime())

        // add the temperature value to the list of Ys
        chart.data.datasets[0].data.push(data.temperature)

        // keeps our chart at 10 x y pairs
        if (chart.data.labels.length > 10) {
            chart.data.labels.shift()
            chart.data.datasets[0].data.shift()
        }

        // show changes
        chart.update()

        // console.log("Data received from server: " + JSON.stringify(data))
        // document.getElementById('temperature').innerText = `Temperature from ESP-32 is ${data.temperature}`
        // document.getElementById('humidity').innerText = `Humidity from ESP-32 is ${data.humidity}`
    })
})
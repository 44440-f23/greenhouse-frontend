document.addEventListener('DOMContentLoaded', function() {
    //Establish a WebSocket Connection to the server
    const socket = io.connect()

    // Create a Chart.js chart for displaying temperature data
    const chart = new Chart(document.getElementById("chart"), {
        type: 'line',
        data: {
            labels: [], // X-axis labels(time)
            datasets: [{
                label: 'Temperature',
                data: [], //Y-axis data (tempature values)
                borderColor: 'rgba(75, 192, 192, 1)', // Line color
                borderWidth: 1 //Line width
            }]
        },
        options: {
            scales: {
                y: {
                    min: 0 // Minium value for the Y-axis
                }
            }
        }
    });
    // Function to get the current time as a formatted string 
    function getCurrentTime() {
        const now = new Date()
        const hours = now.getHours().toString().padStart(2, '0')
        const minutes = now.getMinutes().toString().padStart(2, '0')
        const seconds = now.getSeconds().toString().padStart(2, '0')
      
        return `${hours}:${minutes}:${seconds}`
    }

    //Event handlers for WebSocket events
    //Connecting event
    socket.on("connect", () => {
        console.log("Socket connection to server successful.")
    })

    //Disconecting
    socket.on("disconnect", (msg) => {
        console.log("Socket disconnected, reason: " + msg)
    })

    //Connection error
    socket.on("connect_error", (msg) => {
        console.log('Error while connecting socket to server, reason: ' + msg)
    })

    socket.on("serial", (data) => {
        //Add the current time to the X-axis Labels and Tempature data to the chart
        chart.data.labels.push(getCurrentTime())
        chart.data.datasets[0].data.push(data.temperature)

        //Limit the number of data points displayed to 10
        if (chart.data.labels.length > 10) {
            chart.data.labels.shift()
            chart.data.datasets[0].data.shift()
        }
        //update chart
        chart.update()
        // console.log("Data received from server: " + JSON.stringify(data))
        // document.getElementById('temperature').innerText = `Temperature from ESP-32 is ${data.temperature}`
        // document.getElementById('humidity').innerText = `Humidity from ESP-32 is ${data.humidity}`
    })
})
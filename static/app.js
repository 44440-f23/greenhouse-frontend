document.addEventListener('DOMContentLoaded', function() {
    const socket = io.connect()
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
        options: {
            scales: {
                y: {
                    min: 0
                }
            }
        }
    });

    function getCurrentTime() {
        const now = new Date()
        const hours = now.getHours().toString().padStart(2, '0')
        const minutes = now.getMinutes().toString().padStart(2, '0')
        const seconds = now.getSeconds().toString().padStart(2, '0')
      
        return `${hours}:${minutes}:${seconds}`
    }

    socket.on("connect", () => {
        console.log("Socket connection to server successful.")
    })

    socket.on("disconnect", (msg) => {
        console.log("Socket disconnected, reason: " + msg)
    })

    socket.on("connect_error", (msg) => {
        console.log('Error while connecting socket to server, reason: ' + msg)
    })

    socket.on("serial", (data) => {
        chart.data.labels.push(getCurrentTime())
        chart.data.datasets[0].data.push(data.temperature)

        if (chart.data.labels.length > 10) {
            chart.data.labels.shift()
            chart.data.datasets[0].data.shift()
        }
        chart.update()
        // console.log("Data received from server: " + JSON.stringify(data))
        // document.getElementById('temperature').innerText = `Temperature from ESP-32 is ${data.temperature}`
        // document.getElementById('humidity').innerText = `Humidity from ESP-32 is ${data.humidity}`
    })
})
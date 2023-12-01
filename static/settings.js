const socketio = io()

      // listens for a change in the temp unit toggle and relays info to app.py
document.getElementById('tempUnit').addEventListener('change', function () {
    setTimeout(() => {
        if (this.checked) {
            alert('Temperature unit changed to Fahrenheit.')
            location.reload()
        }
        else {
            alert("Temperature unit changed to Celsius.")
            location.reload()
        }
    }, 500)

    socketio.emit("tempUnitChange", {isCelsius: !this.checked})
})

// reset the alert, the admin can get alerts again
function resetAlert() {
    alert('Alert has been reset. A notification will be sent if a condition is out of bounds.')
    socketio.emit("resetAlert")
}

function submitForm(event) {
    event.preventDefault(); // Prevents the default form submission behavior

    const minInputs = document.querySelectorAll('.min');
    const maxInputs = document.querySelectorAll('.max');

    const numberOfGreenhouses = minInputs.length / 2; // Assuming each greenhouse has 2 sets of inputs (min and max)

    const greenhouseData = {};

    for (let i = 0; i < numberOfGreenhouses; i++) {
    const index = i * 2; // Adjust the index to capture the appropriate input elements

    const tempMinValue = minInputs[index].value.trim();
    const tempMaxValue = maxInputs[index].value.trim();
    const humidityMinValue = minInputs[index + 1].value.trim();
    const humidityMaxValue = maxInputs[index + 1].value.trim();

    const tempMin = tempMinValue !== '' ? parseFloat(tempMinValue) : null;
    const tempMax = tempMaxValue !== '' ? parseFloat(tempMaxValue) : null;
    const humidityMin = humidityMinValue !== '' ? parseFloat(humidityMinValue) : null;
    const humidityMax = humidityMaxValue !== '' ? parseFloat(humidityMaxValue) : null;

    // Validation: min should be less than max
    if ((tempMin !== null && tempMax !== null && tempMin >= tempMax) || (humidityMin !== null && humidityMax !== null && humidityMin >= humidityMax)){
        alert('Minimum values must be lower than Maximum values!');
        return; // Stop processing
    }
    const greenhouseNumber = i + 1;
    is_fahrenheit =  document.getElementById('tempUnit').checked

    // if we are entering temps for F save as C in db
    if (is_fahrenheit){
        greenhouseData[greenhouseNumber] = {
        tempMax: Math.floor((tempMax - 32) * 5/9),
        tempMin: Math.floor((tempMin - 32) * 5/9),
        humidityMax: humidityMax,
        humidityMin: humidityMin
        };
    } else {
        greenhouseData[greenhouseNumber] = {
            tempMax: tempMax,
            tempMin: tempMin,
            humidityMax: humidityMax,
            humidityMin: humidityMin
        };
    }
    }
    const jsonData = JSON.stringify(greenhouseData, null, 2);

    //const jsonDisplay = document.getElementById('jsonDisplay');
    //jsonDisplay.textContent = jsonData;

    //sending the data to the server using fetch API
fetch('/submit_form',{
    method: 'POST',
    headers: {
        'Content-Type' : 'application/json',
    },
    body: jsonData, //send that good json data
})
.then(response => {
        if (response.ok){
            console.log('data send successfully');
        }
        else{
            console.log('Error in sending data');
        }
    })
    .catch(error =>{
        console.error('Error: ', error);
    }) 
}
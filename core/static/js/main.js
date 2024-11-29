async function connectToDevice() {
    try {
        const device = await navigator.bluetooth.requestDevice({
            acceptAllDevices: true,
            optionalServices: ['heart_rate']
        });

        const server = await device.gatt.connect();
        const service = await server.getPrimaryService('heart_rate');
        const characteristic = await service.getCharacteristic('heart_rate_measurement');

        await characteristic.startNotifications();
        characteristic.addEventListener('characteristicvaluechanged', handleHeartRateMeasurement);


    } catch (error) {
        handleError(error);
    }
}

function handleHeartRateMeasurement(event) {
    const value = event.target.value;
    const dataView = new DataView(value.buffer);
    const flags = dataView.getUint8(0);
    let heartRate;

    if (flags & 0x01) {

        heartRate = dataView.getUint16(1, true);
    } else {
        heartRate = dataView.getUint8(1);
    }


    console.log(`Frecuencia cardíaca: ${heartRate} bpm`);
    showStatusMessage(`Frecuencia cardíaca: ${heartRate} bpm`);
}

function showStatusMessage(message) {
    const statusText = document.getElementById('status');
    statusText.textContent = message;
    statusText.classList.remove('error');
}

function handleError(error) {
    console.error('Error al conectar con el dispositivo Bluetooth:', error);
    const statusText = document.getElementById('status');
    statusText.textContent = 'Error al conectar con el dispositivo Bluetooth.';
    statusText.classList.add('error');
}

document.addEventListener('DOMContentLoaded', () => {
    const connectBtn = document.getElementById('connect-btn');
    connectBtn.addEventListener('click', connectToDevice);
});

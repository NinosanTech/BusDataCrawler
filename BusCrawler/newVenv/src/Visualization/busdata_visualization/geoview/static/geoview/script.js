// Karte erstellen und initiale Position auf Berlin setzen
var map = L.map('map').setView([-34.6, -58.38], 12);

// Leaflet-Kachel-Layer hinzufügen (OpenStreetMap)
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

var busLinesLayer;
var currentDay = 'montag';  // Standardmäßig Montag anzeigen

// Funktion zum Abrufen der GeoJSON-Daten von der Django-API
function loadBusData() {

    fetch('/get_bus_data/', {
        headers:{
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest', //Necessary to work with request.is_ajax()
        },
    })
    // .then(response => console.log(response.text()))
    .then(response => {
        // if (!response.ok) {
        try {
            // const data = response.json();
            // console.log(data);
            return response.json();
        } catch (err) {
            console.log(err)
        }
    })
    .then(data => {
        if (typeof data === "string") {
            data = JSON.parse(data);
        }
        const features = data.features
        if (!features || features.length === 0) {
            throw new Error("Kein 'features'-Array in den empfangenen Daten.");
        }
        busLinesLayer = L.geoJSON({type: 'FeatureCollection', features: features}, {
            style: function (feature) {
                var auslastung = feature.properties.auslastung_montag;
                return {
                    color: auslastung > 50 ? 'red' : 'blue',
                    weight: 5
                };
            },
            onEachFeature: function (feature, layer) {
                layer.bindTooltip(
                    `${feature.properties.line}: ${feature.properties.auslastung_montag}% Auslastung`
                );
            }
        }).addTo(map);

        features.forEach(feature => {
            if (feature.geometry && feature.geometry.coordinates.length > 1) {
                const waypoints = feature.geometry.coordinates.map(coord => L.latLng(coord[0], coord[1]));
                addRouting(waypoints);
            }
        });
    })
    .catch(error => {
        console.error('Es gab ein Problem mit der Fetch-Operation:', error);
    });
}

// Lade Buslinien-Daten
loadBusData();

function addRouting(waypoints) {
    L.Routing.control({
        waypoints: waypoints,
        createMarker: function() { return null; },
        router: L.Routing.osrmv1({
            serviceUrl: 'http://localhost:5000/route/v1' // URL deines lokalen OSRM-Servers
        }),
        routeWhileDragging: false,
        show: false,
    }).addTo(map);
}

// Funktion zum Aktualisieren der Karte basierend auf dem ausgewählten Tag
function updateMap() {
    currentDay = document.getElementById('day').value;

    // Entferne die bestehende Layer und füge sie neu hinzu
    if (busLinesLayer) {
        map.removeLayer(busLinesLayer);
    }
    loadBusData();
}
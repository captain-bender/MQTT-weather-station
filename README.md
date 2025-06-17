# MQTT weather station

This is a project that uses an MQTT broker and clients to implement a fictional weather station that pulls data from openweathermap.

### Useful commands (using Windows PowerShell)

Activate your venv environment
```
.\.venv\Scripts\Activate.ps1 
```

Start a broker with a specific custom config
```
& "C:\Program Files\mosquitto\mosquitto.exe" -c "C:\Users\capta\Documents\scps3\mosquitto_config\mosquitto-cloud.conf" -v
```

Listen a topic:
```
mosquitto_sub -h localhost -u viewer -P <password> -t weather/athens/status -q 1 -v
```
### Author
Angelos Plastropoulos
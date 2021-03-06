# NightWatch
> Your personal medical guardian - detects Seizures, Sleep Paralysis, Sleep Apnea, Narcolepsy, Brigada and many more!

NightWatch uses a coordination of IoT devices and sensors - a heart rate sensor (through the Pebble Smart Watch), a muscle tension sensor and a breathing sensor (which is a modified temperature sensor).

## API Routes

All the API endpoints are accessible under `<hostname>/api`. All of the outputs are of the form:

```json
{
  "status": "<int>",
  "message": "<string>",
  "data": "<dict>"
}
```
The outputs of each API Route correspond to the modified attributes of this default output JSON.
  
1. `/api/signup` - Sign a user up
  * **POST/GET**
  * Input: {username, password, full_name}
  * Returns: {status, message}
  
2. `/api/login` - Log a user into the system
  * **POST/GET**
  * Input: {username, password}
  * Returns: {status, message, data:{token}}
  
3. `/api/user/measurement` - Collect instrument values from the various sensors
  * **POST/GET**
  * Input: {token, value, instrument, record_time?}
  * Returns: {status, message}
  
4. `/api/user/relative` - Add a family relative (and that relative's phone number) for the emergency notification system
  * **POST/GET**
  * Input: {token, full_name, phone}
  * Returns: {status, message}

5. `/api/user/get_measurements` - Get all of the measurements for the user
    * **POST/GET**
    * Input: {token, instrument?}
    * Returns: {status, data:{results: [{instrument, value, record_time}], message}}

5. `/api/user/get_relatives` - Get all of the relatives for the user
    * **POST/GET**
    * Input: {token}
    * Returns: [status, data:{results: [{full_name, phone}]}, message]
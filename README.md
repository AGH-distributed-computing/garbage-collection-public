
# agh-distributed-computing


Simulator of garbage production and collection in a city. 

Uses time series and is prepared to execute commands and return its results in JSON format. 

Written as a part of a project for AGH Ubiquitous computing course.

## 1. Location model

The simulator uses two basic ways to describe a location:

1. **Intersection / vertex name**
2. **Street-side position**, defined by:
   - street name,
   - side of the street,
   - distance from the intersection referenced by `firstVertice`.

Bins and events can only use the second form. An event represents a pile of waste and is modeled as a special type of bin.

Truck locations may use either form 1 or form 2.


## 2. Public-facing API

The methods below are intended for interaction with the outside world.

### `getEventsCalendar(self)`

Returns information about all events that are scheduled to occur in the city in the future.

**Return value:** a JSON string in the same structure as `events.json`.

---

### `setAlertLevels(self, binsJson)`

Sets alert thresholds for bins. Thresholds are provided as a fraction of the bin capacity. Once a threshold is exceeded, the bin becomes visible in the output returned by `getAlertBins()`.

**Input:** a JSON structure similar to `bin_alert.json`.

**Notes:**
- Bins are normally identified by street name, side, and distance from `firstVertice`.
- A bin has no alert threshold by default.
- This method is designed to be called multiple times during a simulation run.

---

### `getAlertBins(self)`

Returns the list of bins that have exceeded the thresholds configured with `setAlertLevels()`.

**Return value:** a JSON object containing the locations of bins currently over their alert limits.

---

### `removeAlertLevels(self, binsJson)`

Removes alert thresholds from the selected bins. After removal, the bin returns to its default behavior and no longer reports threshold violations, even if it is completely full.

**Input:** a JSON structure matching `setAlertLevels()`, but without the alert-threshold field.

---

### `parseOrdersForTruck(self, jsonOrders)`

Assigns a route and commands to a truck.

**Input:** a JSON structure in the same format as `example_truck_orders.json`.

The first entry identifies the truck, followed by a sequence of commands. Supported command types are:

- `goToVertice` - move to an intersection by name
- `goToEdgePlace` - move to a street-side location described in the second location format
- `collectGarbage` - collect waste on the side where the truck is currently located

`collectGarbage` means "collect garbage at the place where the truck currently stands."

Warning: bins are not to be placed directly at vertices. To simulate a bin at an intersection, place it on the outgoing edge at distance `0` from that intersection.

---

### `getTruckOrdersAsJson(self, truckName)`

Returns the commands that are still pending for the specified truck.

**Input:** `truckName`, which is also the truck's unique identifier.

**Return value:** a JSON structure analogous to `example_truck_orders.json`.

---

### `getTruckStatus(self, truckName)`

Returns the current state of the specified truck.

**Return value:** information in a format analogous to a single entry from `city1_trucks.json`.

## 3. Internal or initialization-only methods

The following methods are not intended to be part of the public API.

### `__init__(self, topographyFilePath, carFilePath, verbose=False)`

Initializes the `City` class.

The JSON files used by the simulator are not expected to change during runtime.

**Parameters:**
- `topographyFilePath` - path to the JSON file describing the city topology (roads, intersections, bins). The default file is `city1_topography.json`.
- `carFilePath` - path to the JSON file describing garbage trucks (fuel consumption, capacity, and related properties). The default file is `city1_trucks.json`.

---

### `getEventsFromJson(self, eventsJson)`

Loads event data from a JSON structure in the same format as `events.json`.

This method is generally intended to be called once at the start of the simulation.

Event time is defined relative to the start of the simulation using:
- day
- hour
- minute

Event location is described by:
- `streetName`
- `distance`
- `side`

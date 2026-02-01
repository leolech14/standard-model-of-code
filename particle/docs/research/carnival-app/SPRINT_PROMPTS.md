# Carnival SC App - Incremental Sprint Prompts for Google AI Studio

> **Strategy**: Each prompt is atomic, generates 3-5 files max, and produces a working increment.
> **Rule**: Fresh chat for each sprint. Verify before continuing.

---

## SPRINT 0 - Skeleton (Map + Glass Foundation)

```
Build a minimal React + Vite + TypeScript app with a full-screen Google Map.

TECH:
- Vite + React 18 + TypeScript
- @googlemaps/js-api-loader for Google Maps
- Tailwind CSS via CDN in index.html (no build step)

REQUIREMENTS:
1. Map fills entire viewport (100vw x 100vh)
2. Map centers on Santa Catarina coast: lat -27.1, lng -48.5, zoom 10
3. Dark minimal aesthetic
4. If VITE_GOOGLE_MAPS_API_KEY is missing or "PLACEHOLDER", show a centered glass overlay: "Add your Google Maps API key to .env.local"

GLASS STYLING (add to src/styles.css):
.glass {
  background: rgba(10, 12, 18, 0.65);
  border: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 12px;
}

.glass-dark {
  background: rgba(5, 6, 10, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-radius: 12px;
}

FILES TO CREATE:
1. index.html - Include Tailwind CDN, mount point, dark body bg
2. vite.config.ts - Basic React plugin config
3. package.json - Dependencies: react, react-dom, vite, typescript, @vitejs/plugin-react, @googlemaps/js-api-loader
4. tsconfig.json - Standard React TS config
5. src/main.tsx - React entry point
6. src/App.tsx - Main component with map and error overlay
7. src/styles.css - Glass classes and base styles
8. .env.local - VITE_GOOGLE_MAPS_API_KEY=PLACEHOLDER
9. .gitignore - node_modules, dist, .env.local

MAP OPTIONS:
- disableDefaultUI: true
- zoomControl: true
- mapTypeControl: false
- streetViewControl: false
- fullscreenControl: false

Base font: 12px, font-family system-ui. Text color white. Body bg #0a0a0f.

Generate all files with complete working code.
```

**VERIFY**: `npm install && npm run dev` → Shows map OR "missing key" overlay. No crashes.

---

## SPRINT 1 - Data Types + Static Markers

```
I have a working Vite + React + TypeScript app with a full-screen Google Map.

ADD data types and static markers.

CREATE src/types.ts:
```typescript
export type PlaceType = 'house' | 'party' | 'poi';

export interface Place {
  id: string;
  type: PlaceType;
  name: string;
  lat: number;
  lng: number;
}
```

CREATE src/data.ts with hardcoded places:
```typescript
import { Place } from './types';

export const PLACES: Place[] = [
  { id: 'bc-house', type: 'house', name: 'BC House', lat: -26.9906, lng: -48.6353 },
  { id: 'gcr-house', type: 'house', name: 'GCR House', lat: -27.3162, lng: -48.5569 },
  { id: 'warung', type: 'party', name: 'Warung', lat: -27.1467, lng: -48.4839 },
  { id: 'p12', type: 'party', name: 'P12', lat: -27.6044, lng: -48.4527 },
  { id: 'green-valley', type: 'party', name: 'Green Valley', lat: -26.9231, lng: -48.6578 },
  { id: 'surreal', type: 'party', name: 'Surreal', lat: -27.5983, lng: -48.5156 },
];
```

UPDATE src/App.tsx:
1. Import PLACES from data.ts
2. After map loads, create markers using google.maps.marker.AdvancedMarkerElement
3. Marker styling:
   - House: 12px white circle with subtle shadow
   - Party: 12px pink/coral circle (#f472b6)
   - POI: 12px blue circle (#60a5fa)
4. Use a simple div as marker content:
   ```typescript
   const dot = document.createElement('div');
   dot.className = 'w-3 h-3 rounded-full shadow-lg';
   dot.style.backgroundColor = place.type === 'house' ? '#ffffff' :
                                place.type === 'party' ? '#f472b6' : '#60a5fa';
   ```
5. Store markers in a ref so we can update them later
6. console.log place name when marker clicked

Keep all existing code. Just add the new files and update App.tsx.
```

**VERIFY**: Map shows 6 colored dots. Console logs name on click.

---

## SPRINT 2 - Left Rail + Place List

```
I have a Vite + React + Google Maps app with markers for places.

The app has:
- src/types.ts with Place type
- src/data.ts with PLACES array
- src/App.tsx rendering a map with markers

ADD a minimal left navigation rail and place list panel.

CREATE src/components/Rail.tsx:
- Fixed position left: 0, top: 0, bottom: 0
- Width: 52px
- Glass background (use .glass class)
- Flex column, items centered, pt-4, gap-2
- 3 icon buttons stacked:
  1. List icon (📍 or SVG) - toggles place list
  2. Filter icon (⚙️ or SVG) - placeholder for now
  3. Info icon (ℹ️ or SVG) - placeholder for now
- Each button: 36px square, rounded-lg, hover:bg-white/10, flex items-center justify-center
- Active button has bg-white/10

CREATE src/components/PlaceList.tsx:
- Fixed position left: 60px, top: 8px, bottom: 8px
- Width: 220px
- Glass background, p-3
- Header: "Places" in 13px font-medium, mb-3
- List of places as compact rows:
  - 8px colored dot (by type)
  - Place name, 12px
  - Hover: bg-white/5
  - Cursor pointer
- Clicking a row calls onSelect(place.id)

UPDATE src/App.tsx:
1. Add state: showPlaceList (boolean), selectedPlaceId (string | null)
2. Render Rail component
3. Rail's list button toggles showPlaceList
4. Render PlaceList when showPlaceList is true
5. PlaceList onSelect sets selectedPlaceId
6. When selectedPlaceId changes, find the marker and add a ring/glow effect

Selected marker styling:
- Add a CSS class or inline style for selected state
- White ring: box-shadow 0 0 0 3px rgba(255,255,255,0.5)

Files to create/update:
- CREATE src/components/Rail.tsx
- CREATE src/components/PlaceList.tsx
- UPDATE src/App.tsx
```

**VERIFY**: Rail shows on left. Click list icon toggles panel. Click place selects it and marker glows.

---

## SPRINT 3 - Detail Drawer

```
I have a React + Google Maps app with:
- Places data and markers
- Left Rail with place list
- Selection state (selectedPlaceId)

ADD a detail drawer that shows when a place is selected.

CREATE src/components/DetailDrawer.tsx:

Props:
- place: Place
- onClose: () => void

Layout:
- Fixed position: bottom 8px, right 8px
- Width: 300px
- Glass background
- Padding: 16px

Content:
1. Header row:
   - Place name (14px font-medium)
   - Close button (X icon, 24px, hover:bg-white/10, rounded)
2. Type badge below name:
   - Pill shape, px-2 py-0.5, text-xs, rounded-full
   - House: bg-white/20, text "Home"
   - Party: bg-pink-500/30, text "Party"
   - POI: bg-blue-500/30, text "POI"
3. Coordinates row:
   - Text-xs, text-white/50
   - Format: "-27.1467, -48.4839"
4. Divider line (border-t border-white/10, my-3)
5. Actions row (for future use):
   - Empty for now, just a placeholder div

UPDATE src/App.tsx:
1. Import DetailDrawer
2. When selectedPlaceId is set, find the place and render DetailDrawer
3. Pass onClose that sets selectedPlaceId to null
4. When a place is selected:
   - Pan map to that location: map.panTo({ lat: place.lat, lng: place.lng })
   - Optionally zoom in slightly if zoom < 12

Animation (optional but nice):
- Add transition on the drawer: transform and opacity
- Enter from bottom: translate-y-4 opacity-0 → translate-y-0 opacity-100

Files:
- CREATE src/components/DetailDrawer.tsx
- UPDATE src/App.tsx
```

**VERIFY**: Select a place → drawer appears bottom-right with name, type badge, coords. X closes it. Map pans to location.

---

## SPRINT 4 - Enhanced Place Data (Images, Times, Links)

```
I have a React + Google Maps app with places, markers, place list, and detail drawer.

ENHANCE the Place type and data with images, times, and links.

UPDATE src/types.ts:
```typescript
export type PlaceType = 'house' | 'party' | 'poi';
export type PartyCategory = 'day' | 'night' | 'sunset' | 'beach' | 'club' | 'openair';

export interface PlaceLinks {
  instagram?: string;
  tickets?: string;
  website?: string;
}

export interface Place {
  id: string;
  type: PlaceType;
  name: string;
  lat: number;
  lng: number;
  imageUrl?: string;
  startAt?: string; // ISO datetime
  endAt?: string;
  categories?: PartyCategory[];
  links?: PlaceLinks;
  address?: string;
  notes?: string;
}
```

UPDATE src/data.ts with rich party data:
```typescript
export const PLACES: Place[] = [
  // Houses
  {
    id: 'bc-house',
    type: 'house',
    name: 'BC House',
    lat: -26.9906,
    lng: -48.6353,
    address: 'Balneário Camboriú, SC',
    notes: 'Arthur + Leo arrive Feb 14'
  },
  {
    id: 'gcr-house',
    type: 'house',
    name: 'GCR House',
    lat: -27.3162,
    lng: -48.5569,
    address: 'Governador Celso Ramos, SC',
    notes: 'Quieter base, great for recovery'
  },
  // Parties
  {
    id: 'warung',
    type: 'party',
    name: 'Warung',
    lat: -27.1467,
    lng: -48.4839,
    imageUrl: 'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=800&q=80',
    startAt: '2026-02-14T23:00:00-03:00',
    categories: ['night', 'club'],
    links: {
      instagram: 'https://instagram.com/waraborada',
      tickets: 'https://warung.com.br'
    },
    address: 'Praia Brava, Itajaí'
  },
  {
    id: 'p12',
    type: 'party',
    name: 'P12',
    lat: -27.6044,
    lng: -48.4527,
    imageUrl: 'https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=800&q=80',
    startAt: '2026-02-15T14:00:00-03:00',
    categories: ['day', 'beach'],
    links: {
      instagram: 'https://instagram.com/p12floripa'
    },
    address: 'Jurerê, Florianópolis'
  },
  {
    id: 'green-valley',
    type: 'party',
    name: 'Green Valley',
    lat: -26.9231,
    lng: -48.6578,
    imageUrl: 'https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=800&q=80',
    startAt: '2026-02-16T22:00:00-03:00',
    categories: ['night', 'club'],
    links: {
      instagram: 'https://instagram.com/greenvalleybr',
      tickets: 'https://greenvalley.com.br'
    },
    address: 'Camboriú, SC'
  },
  {
    id: 'surreal',
    type: 'party',
    name: 'Surreal',
    lat: -27.5983,
    lng: -48.5156,
    imageUrl: 'https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=800&q=80',
    startAt: '2026-02-17T16:00:00-03:00',
    categories: ['sunset', 'beach', 'openair'],
    links: {
      instagram: 'https://instagram.com/surrealfloripa'
    },
    address: 'Campeche, Florianópolis'
  },
];
```

Files:
- UPDATE src/types.ts
- UPDATE src/data.ts
```

**VERIFY**: TypeScript compiles. Data has images, times, links.

---

## SPRINT 5 - Party Cards with Images

```
I have a React + Google Maps app with enhanced Place data including imageUrl, startAt, and categories.

UPDATE PlaceList to show parties as image cards.

UPDATE src/components/PlaceList.tsx:

Render places in sections:
1. "Bases" section - houses as simple rows
2. "Parties" section - parties as wide image cards
3. "POIs" section - pois as simple rows (if any)

Simple row (houses, pois):
- Flex row, items-center, gap-2, py-2, px-2
- 8px colored dot
- Name text-xs
- Hover: bg-white/5

Party card:
- Width: 100% (fill panel)
- Height: 72px
- Rounded-lg, overflow-hidden
- Background: place.imageUrl as cover image
- Gradient overlay: linear-gradient(to top, rgba(0,0,0,0.8) 0%, transparent 100%)
- Content at bottom:
  - Name (12px font-medium, white)
  - Time badge (text-xs, text-white/70)
    - Format startAt as "Sat 14, 11pm" using:
      new Date(startAt).toLocaleDateString('en-US', { weekday: 'short', day: 'numeric' }) + ', ' +
      new Date(startAt).toLocaleTimeString('en-US', { hour: 'numeric', hour12: true })
- Category pills (tiny, 8px font, bg-white/20, px-1.5 rounded)
- Hover: scale 1.02, transition
- Cursor pointer

Section headers:
- Text-xs, text-white/40, uppercase, tracking-wide, mb-2, mt-4
- First section no mt

Make the panel scrollable: overflow-y-auto

Files:
- UPDATE src/components/PlaceList.tsx
```

**VERIFY**: Place list shows houses as rows, parties as image cards with time and categories.

---

## SPRINT 6 - Enhanced Detail Drawer

```
I have a React + Google Maps app with party cards showing images.

ENHANCE DetailDrawer to show images, times, and action buttons.

UPDATE src/components/DetailDrawer.tsx:

Layout:
- Width: 320px
- No padding at top (image goes edge to edge)

Content structure:

1. Image banner (if place.imageUrl):
   - Height: 140px
   - Object-cover, w-full
   - Gradient overlay at bottom for text
   - If no image: show colored placeholder based on type

2. Content area (p-4):
   a. Name + close button row
      - Name: 15px font-semibold
      - X button: absolute top-right of content area

   b. Type + categories row:
      - Type badge (as before)
      - Category pills next to it (if party)

   c. Time row (if startAt):
      - Calendar icon + formatted date/time
      - Text-sm, text-white/70

   d. Address row (if address):
      - MapPin icon + address
      - Text-xs, text-white/50

   e. Notes (if notes):
      - Text-xs, text-white/40, italic
      - mt-2

   f. Divider

   g. Action buttons row:
      - Flex row, gap-2
      - Each button: flex-1, py-2, rounded-lg, text-xs, font-medium
      - Instagram button (if links.instagram): bg-gradient-to-r from-purple-500 to-pink-500
      - Tickets button (if links.tickets): bg-amber-500
      - Directions button (always): bg-white/10
        - Opens: https://www.google.com/maps/dir/?api=1&destination={lat},{lng}
      - Icons + text in buttons

Use simple emoji or text for icons:
- Instagram: "IG"
- Tickets: "🎫"
- Directions: "→"

Files:
- UPDATE src/components/DetailDrawer.tsx
```

**VERIFY**: Select a party → drawer shows image banner, time, categories, action buttons. Buttons open correct URLs.

---

## SPRINT 7 - Map InfoWindow Popup

```
I have a React + Google Maps app with an enhanced detail drawer.

ADD InfoWindow popups on marker click.

UPDATE src/App.tsx (or create src/components/MapCanvas.tsx if you prefer):

When a marker is clicked:
1. Set selectedPlaceId (as before)
2. Open a google.maps.InfoWindow anchored to the marker

InfoWindow content (HTML string):
```html
<div style="background:#1a1a2e;color:white;padding:12px;border-radius:8px;min-width:200px;font-family:system-ui;font-size:12px;">
  ${place.imageUrl ? `<img src="${place.imageUrl}" style="width:100%;height:80px;object-fit:cover;border-radius:4px;margin-bottom:8px;">` : ''}
  <div style="font-weight:600;font-size:14px;margin-bottom:4px;">${place.name}</div>
  ${place.startAt ? `<div style="color:#aaa;font-size:11px;margin-bottom:8px;">${formatTime(place.startAt)}</div>` : ''}
  <div style="display:flex;gap:6px;margin-top:8px;">
    ${place.links?.instagram ? `<a href="${place.links.instagram}" target="_blank" style="flex:1;background:#833AB4;color:white;padding:6px;border-radius:4px;text-align:center;text-decoration:none;font-size:10px;">Instagram</a>` : ''}
    ${place.links?.tickets ? `<a href="${place.links.tickets}" target="_blank" style="flex:1;background:#f59e0b;color:white;padding:6px;border-radius:4px;text-align:center;text-decoration:none;font-size:10px;">Tickets</a>` : ''}
    <a href="https://www.google.com/maps/dir/?api=1&destination=${place.lat},${place.lng}" target="_blank" style="flex:1;background:#374151;color:white;padding:6px;border-radius:4px;text-align:center;text-decoration:none;font-size:10px;">Directions</a>
  </div>
</div>
```

Rules:
- Only one InfoWindow open at a time (store in ref, close previous before opening new)
- InfoWindow closes when clicking elsewhere on map
- InfoWindow has no default close button (we use our own or let map click close it)

Helper function for time formatting:
```typescript
function formatTime(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }) +
         ', ' + d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
}
```

Files:
- UPDATE src/App.tsx
```

**VERIFY**: Click marker → popup appears with image, name, time, buttons. Links work. Click map → popup closes.

---

## SPRINT 8 - Timeline Bar (Day Pills)

```
I have a React + Google Maps app with markers, place list, detail drawer, and popups.

ADD a timeline bar at the top showing Carnival days.

CREATE src/components/TimelineBar.tsx:

Props:
- selectedDate: string (ISO date, e.g., "2026-02-14")
- onSelectDate: (date: string) => void
- places: Place[] (to show event counts)

Layout:
- Fixed position: top 8px, left 68px (after rail), right 8px
- Height: auto (compact)
- Glass background, px-3, py-2
- Flex row, gap-2, overflow-x-auto, hide scrollbar

Generate day pills for Feb 13-23, 2026:
```typescript
const days = [];
for (let d = 13; d <= 23; d++) {
  days.push(`2026-02-${d.toString().padStart(2, '0')}`);
}
```

Each day pill:
- Min-width: 48px
- Flex column, items-center
- py-1.5, px-2, rounded-lg
- Cursor pointer
- Unselected: bg-transparent, hover:bg-white/5
- Selected: bg-white/15

Pill content:
- Day of week (text-xs, text-white/50): "Fri", "Sat", etc.
- Day number (text-sm, font-medium): "13", "14", etc.
- Event count dot (if events that day):
  - Tiny pink dot below the number
  - Count events where startAt matches this date

UPDATE src/App.tsx:
1. Add state: selectedDate (default to "2026-02-14")
2. Render TimelineBar
3. Pass places so it can count events per day

Files:
- CREATE src/components/TimelineBar.tsx
- UPDATE src/App.tsx
```

**VERIFY**: Timeline bar shows Feb 13-23. Click a day selects it. Days with parties show a dot.

---

## SPRINT 9 - Event Strip (Horizontal Party Cards)

```
I have a React + Google Maps app with a timeline bar for selecting days.

ADD an event strip showing parties for the selected day.

CREATE src/components/EventStrip.tsx:

Props:
- places: Place[]
- selectedDate: string
- selectedPlaceId: string | null
- onSelectPlace: (id: string) => void

Layout:
- Fixed position: top 60px (below timeline), left 68px, right 8px
- Height: 88px
- Glass background, px-3, py-2
- Flex row, gap-3, overflow-x-auto, hide scrollbar
- Scroll snap: snap-x snap-mandatory

Filter places:
- Only show parties (type === 'party')
- Only show where startAt date matches selectedDate
- Sort by startAt time

If no events for selected day:
- Show centered text: "No events on this day" (text-white/40)

Each event card:
- Width: 180px (flex-shrink-0)
- Height: 72px
- Rounded-lg, overflow-hidden
- Snap-start (for scroll snap)
- Background: imageUrl as cover
- Gradient overlay from bottom
- Selected state: ring-2 ring-white/50

Card content:
- Position absolute bottom, p-2
- Name (12px font-medium, white, truncate)
- Time (10px, text-white/70)
- Category pill (one, first category, 8px font)

On click:
- Call onSelectPlace(place.id)

UPDATE src/App.tsx:
1. Render EventStrip below TimelineBar
2. Connect selectedDate, selectedPlaceId, onSelectPlace

Hide EventStrip on mobile (hidden md:flex) - we'll handle mobile later.

Files:
- CREATE src/components/EventStrip.tsx
- UPDATE src/App.tsx
```

**VERIFY**: Select a day → event strip shows parties for that day as horizontal cards. Click card → selects place.

---

## SPRINT 10 - Traffic Layer Toggle

```
I have a React + Google Maps app with timeline and event strip.

ADD a traffic layer toggle.

UPDATE src/types.ts - add settings interface:
```typescript
export interface MapSettings {
  showTraffic: boolean;
  showLabels: boolean;
}
```

UPDATE src/App.tsx:

1. Add state:
   ```typescript
   const [settings, setSettings] = useState<MapSettings>({
     showTraffic: false,
     showLabels: true
   });
   ```

2. Create traffic layer once after map loads:
   ```typescript
   const trafficLayerRef = useRef<google.maps.TrafficLayer | null>(null);

   // After map is ready:
   trafficLayerRef.current = new google.maps.TrafficLayer();
   ```

3. Toggle traffic layer based on settings:
   ```typescript
   useEffect(() => {
     if (trafficLayerRef.current && mapRef.current) {
       if (settings.showTraffic) {
         trafficLayerRef.current.setMap(mapRef.current);
       } else {
         trafficLayerRef.current.setMap(null);
       }
     }
   }, [settings.showTraffic]);
   ```

UPDATE src/components/Rail.tsx:
- The settings/filter icon (⚙️) now toggles a settings panel

CREATE src/components/SettingsPanel.tsx:
- Fixed position: left 60px, bottom 8px
- Width: 200px
- Glass background, p-3
- Toggle rows:
  - "Traffic" toggle
  - "Labels" toggle (placeholder for now)
- Each toggle: flex justify-between, items-center
  - Label (text-xs)
  - Toggle switch (20px x 36px pill, with sliding dot)

Props:
- settings: MapSettings
- onUpdate: (settings: MapSettings) => void

Toggle switch component (inline or separate):
```tsx
<button
  onClick={() => onUpdate({...settings, showTraffic: !settings.showTraffic})}
  className={`w-9 h-5 rounded-full transition-colors ${settings.showTraffic ? 'bg-green-500' : 'bg-white/20'}`}
>
  <div className={`w-4 h-4 rounded-full bg-white transition-transform ${settings.showTraffic ? 'translate-x-4' : 'translate-x-0.5'}`} />
</button>
```

Files:
- UPDATE src/types.ts
- CREATE src/components/SettingsPanel.tsx
- UPDATE src/components/Rail.tsx
- UPDATE src/App.tsx
```

**VERIFY**: Click settings icon → panel appears. Toggle traffic → Google traffic layer shows/hides on map.

---

## SPRINT 11 - Route Between House and Party

```
I have a React + Google Maps app with traffic layer toggle.

ADD routing from nearest house to selected party.

UPDATE src/types.ts - add to MapSettings:
```typescript
export interface MapSettings {
  showTraffic: boolean;
  showLabels: boolean;
  showRoute: boolean;
}
```

CREATE src/services/routing.ts:
```typescript
export interface RouteResult {
  path: google.maps.LatLng[];
  durationSeconds: number;
  distanceMeters: number;
  durationInTraffic?: number;
}

export async function computeRoute(
  directionsService: google.maps.DirectionsService,
  origin: { lat: number; lng: number },
  destination: { lat: number; lng: number }
): Promise<RouteResult | null> {
  try {
    const result = await directionsService.route({
      origin,
      destination,
      travelMode: google.maps.TravelMode.DRIVING,
      drivingOptions: {
        departureTime: new Date(),
        trafficModel: google.maps.TrafficModel.BEST_GUESS
      }
    });

    const route = result.routes[0];
    const leg = route.legs[0];

    return {
      path: route.overview_path,
      durationSeconds: leg.duration?.value || 0,
      distanceMeters: leg.distance?.value || 0,
      durationInTraffic: leg.duration_in_traffic?.value
    };
  } catch (e) {
    console.error('Routing error:', e);
    return null;
  }
}

export function findNearestHouse(houses: Place[], target: { lat: number; lng: number }): Place | null {
  if (houses.length === 0) return null;

  let nearest = houses[0];
  let minDist = haversine(houses[0], target);

  for (const house of houses) {
    const dist = haversine(house, target);
    if (dist < minDist) {
      minDist = dist;
      nearest = house;
    }
  }
  return nearest;
}

function haversine(a: {lat:number;lng:number}, b: {lat:number;lng:number}): number {
  const R = 6371;
  const dLat = (b.lat - a.lat) * Math.PI / 180;
  const dLng = (b.lng - a.lng) * Math.PI / 180;
  const lat1 = a.lat * Math.PI / 180;
  const lat2 = b.lat * Math.PI / 180;
  const x = Math.sin(dLat/2)**2 + Math.cos(lat1)*Math.cos(lat2)*Math.sin(dLng/2)**2;
  return R * 2 * Math.atan2(Math.sqrt(x), Math.sqrt(1-x));
}
```

UPDATE src/App.tsx:

1. Create DirectionsService after map loads:
   ```typescript
   const directionsServiceRef = useRef<google.maps.DirectionsService | null>(null);
   directionsServiceRef.current = new google.maps.DirectionsService();
   ```

2. Create Polyline for route:
   ```typescript
   const routePolylineRef = useRef<google.maps.Polyline | null>(null);
   routePolylineRef.current = new google.maps.Polyline({
     strokeColor: '#60a5fa',
     strokeOpacity: 0.8,
     strokeWeight: 4,
   });
   ```

3. When selectedPlaceId changes AND it's a party AND showRoute is true:
   - Find nearest house
   - Compute route
   - Update polyline path
   - Store route result in state for ETA display

4. Add route toggle to SettingsPanel

5. Clear route when no party selected or route disabled

Files:
- UPDATE src/types.ts
- CREATE src/services/routing.ts
- UPDATE src/components/SettingsPanel.tsx
- UPDATE src/App.tsx
```

**VERIFY**: Select a party → blue route line appears from nearest house. Toggle route off → line disappears.

---

## SPRINT 12 - ETA Badge on Route

```
I have a React + Google Maps app with routing between house and party.

ADD an ETA badge floating on the map near the route midpoint.

CREATE src/components/ETABadge.tsx:

Props:
- durationSeconds: number
- distanceMeters: number
- durationInTraffic?: number
- position: { lat: number; lng: number } // midpoint of route

The badge should be rendered as an AdvancedMarkerElement with custom HTML content.

Badge content:
```html
<div class="glass" style="padding:6px 10px;font-size:11px;white-space:nowrap;">
  <span style="font-weight:600;">${formatDuration(durationInTraffic || durationSeconds)}</span>
  <span style="color:rgba(255,255,255,0.5);margin-left:6px;">${formatDistance(distanceMeters)}</span>
</div>
```

Helper functions:
```typescript
function formatDuration(seconds: number): string {
  const mins = Math.round(seconds / 60);
  if (mins < 60) return `${mins} min`;
  const hrs = Math.floor(mins / 60);
  const m = mins % 60;
  return `${hrs}h ${m}m`;
}

function formatDistance(meters: number): string {
  const km = meters / 1000;
  return `${km.toFixed(1)} km`;
}
```

Calculate midpoint:
```typescript
function getMidpoint(path: google.maps.LatLng[]): { lat: number; lng: number } {
  const mid = path[Math.floor(path.length / 2)];
  return { lat: mid.lat(), lng: mid.lng() };
}
```

UPDATE src/App.tsx:

1. Store route result in state:
   ```typescript
   const [routeResult, setRouteResult] = useState<RouteResult | null>(null);
   ```

2. After computing route, setRouteResult

3. Create/update ETA marker when routeResult exists:
   - Use AdvancedMarkerElement with the badge HTML
   - Position at route midpoint
   - Remove marker when route is cleared

4. The badge should have a slight offset so it doesn't sit exactly on the line

Files:
- UPDATE src/App.tsx (integrate ETA badge as marker)
```

**VERIFY**: Route shows → ETA badge appears at midpoint showing duration and distance. Deselect → badge disappears.

---

## SPRINT 13 - Participants + Arrivals

```
I have a React + Google Maps app with routing and ETA.

ADD participants data and arrival info.

UPDATE src/types.ts:
```typescript
export interface Participant {
  id: string;
  name: string;
  arrivalDate: string; // ISO date
  color: string;
}
```

UPDATE src/data.ts - add participants:
```typescript
export const PARTICIPANTS: Participant[] = [
  { id: 'leo', name: 'Leonardo', arrivalDate: '2026-02-14', color: '#60a5fa' },
  { id: 'arthur', name: 'Arthur', arrivalDate: '2026-02-14', color: '#34d399' },
  { id: 'cristiano', name: 'Cristiano', arrivalDate: '2026-02-15', color: '#f472b6' },
];
```

CREATE src/components/ParticipantsPanel.tsx:

Layout:
- Shown when Info icon in Rail is clicked
- Fixed position: left 60px, top 50%, transform -translateY-50%
- Width: 180px
- Glass background, p-3

Content:
- Header: "Crew" (13px font-medium)
- List of participants:
  - Colored dot (participant.color)
  - Name
  - Arrival badge: "Arrives Feb 14" or "Here!" if already arrived (based on selectedDate)

Arrival logic:
```typescript
const isHere = selectedDate >= participant.arrivalDate;
```

UPDATE src/components/TimelineBar.tsx:
- Below each day number, show tiny colored dots for participants arriving that day
- Or show a row of arrival indicators

UPDATE src/App.tsx:
1. Import PARTICIPANTS
2. Track which panel is open in Rail (places | settings | participants)
3. Render ParticipantsPanel when participants panel is open
4. Pass selectedDate to determine who's arrived

Files:
- UPDATE src/types.ts
- UPDATE src/data.ts
- CREATE src/components/ParticipantsPanel.tsx
- UPDATE src/components/TimelineBar.tsx
- UPDATE src/components/Rail.tsx
- UPDATE src/App.tsx
```

**VERIFY**: Click info icon → participants panel shows crew with arrival dates. Timeline shows arrival indicators.

---

## SPRINT 14 - Import/Export JSON

```
I have a React + Google Maps app with participants.

ADD import/export functionality for places data.

CREATE src/components/ImportModal.tsx:

Props:
- isOpen: boolean
- onClose: () => void
- onImport: (places: Place[]) => void

Layout:
- Fixed overlay: inset-0, bg-black/50, flex items-center justify-center
- Modal: glass background, w-96, p-4

Content:
1. Header: "Import Data" + X close button
2. Textarea:
   - Placeholder: "Paste JSON array of places..."
   - Rows: 10
   - Glass-dark background, rounded, p-2, text-xs, font-mono
3. Error message area (if parse fails)
4. Button row:
   - Cancel (bg-white/10)
   - Import (bg-green-500)

Import logic:
```typescript
function handleImport() {
  try {
    const data = JSON.parse(textValue);
    if (!Array.isArray(data)) throw new Error('Must be an array');
    // Basic validation: each item has id, name, lat, lng, type
    const places = data.map(item => ({
      id: item.id || crypto.randomUUID(),
      type: item.type || 'poi',
      name: item.name || 'Unnamed',
      lat: Number(item.lat),
      lng: Number(item.lng),
      ...item
    }));
    onImport(places);
    onClose();
  } catch (e) {
    setError(e.message);
  }
}
```

CREATE src/utils/storage.ts:
```typescript
const STORAGE_KEY = 'carnival_sc_v1';

export function savePlaces(places: Place[]): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(places));
}

export function loadPlaces(): Place[] | null {
  const data = localStorage.getItem(STORAGE_KEY);
  if (!data) return null;
  try {
    return JSON.parse(data);
  } catch {
    return null;
  }
}

export function exportPlaces(places: Place[]): void {
  const json = JSON.stringify(places, null, 2);
  const blob = new Blob([json], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `carnival-places-${new Date().toISOString().split('T')[0]}.json`;
  a.click();
  URL.revokeObjectURL(url);
}
```

UPDATE src/components/Rail.tsx:
- Add Export icon button (⬇️ or download icon)
- Add Import icon button (⬆️ or upload icon)

UPDATE src/App.tsx:
1. Load places from localStorage on mount (merge with defaults)
2. Save places to localStorage when they change
3. Add showImportModal state
4. Render ImportModal
5. Handle export button click → call exportPlaces
6. Handle import → merge new places with existing (dedupe by id)

Files:
- CREATE src/components/ImportModal.tsx
- CREATE src/utils/storage.ts
- UPDATE src/components/Rail.tsx
- UPDATE src/App.tsx
```

**VERIFY**: Export downloads JSON file. Import accepts JSON and adds places. Data persists on refresh.

---

## SPRINT 15 - Mobile Responsive Layout

```
I have a React + Google Maps app with all core features.

MAKE IT MOBILE RESPONSIVE.

UPDATE index.html:
- Add viewport meta tag if not present:
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">

UPDATE src/components/Rail.tsx for mobile:
- On mobile (< 768px): position at bottom, horizontal layout
- Width: 100%, Height: 56px
- Fixed bottom: 0, left: 0, right: 0
- Flex row, justify-around, items-center
- Safe area padding: pb-safe (for iPhone notch)

UPDATE src/components/TimelineBar.tsx for mobile:
- On mobile: position at top, full width
- Left: 0 (no offset for rail)
- Smaller pills, tighter spacing

UPDATE src/components/EventStrip.tsx for mobile:
- Hidden on mobile (events shown in PlaceList instead)

UPDATE src/components/PlaceList.tsx for mobile:
- On mobile: bottom sheet style
- Position: fixed, bottom: 64px (above rail), left: 0, right: 0
- Max-height: 50vh
- Rounded top corners
- Drag handle at top (small pill indicator)
- Scrollable content

UPDATE src/components/DetailDrawer.tsx for mobile:
- On mobile: bottom sheet, full width
- Position: fixed, bottom: 64px, left: 0, right: 0
- Max-height: 60vh
- Rounded top corners
- Image banner slightly shorter (100px)

ADD CSS for safe areas (src/styles.css):
```css
@supports (padding-bottom: env(safe-area-inset-bottom)) {
  .pb-safe {
    padding-bottom: env(safe-area-inset-bottom);
  }
}
```

Use Tailwind responsive prefixes:
- md:hidden - hide on desktop
- hidden md:flex - hide on mobile, show on desktop
- md:left-[68px] - desktop offset
- md:bottom-auto md:right-2 - desktop positioning

UPDATE src/App.tsx:
- Add window resize listener or use CSS media queries
- Adjust map padding for mobile bottom sheet

Files:
- UPDATE index.html
- UPDATE src/styles.css
- UPDATE src/components/Rail.tsx
- UPDATE src/components/TimelineBar.tsx
- UPDATE src/components/EventStrip.tsx
- UPDATE src/components/PlaceList.tsx
- UPDATE src/components/DetailDrawer.tsx
- UPDATE src/App.tsx
```

**VERIFY**: On mobile viewport (< 768px): Rail at bottom, timeline at top, place list as bottom sheet, drawer as bottom sheet.

---

## BONUS SPRINTS (Optional)

### SPRINT 16 - Time Simulation Mode

```
ADD time simulation to animate through Carnival.

Features:
- Play/pause button in timeline
- Simulated time moves +30 min per second
- Auto-selects party nearest to current sim time
- Route updates to show ETA from house to that party
```

### SPRINT 17 - Weather Widget

```
ADD weather display using OpenWeatherMap API.

Features:
- Fetch 7-day forecast for SC region
- Show weather icon in timeline day pills
- Show temp/conditions in detail drawer
```

### SPRINT 18 - Gemini Text Import

```
ADD Gemini-powered natural language import.

Features:
- Paste raw text describing events
- Send to Gemini to extract structured Place data
- Review and confirm before adding
```

### SPRINT 19 - Municipality Boundaries

```
ADD Google Maps Data-Driven Styling for municipalities.

Features:
- Highlight SC municipalities with subtle fill
- Toggle boundaries on/off
- Requires Map ID with DDS enabled
```

---

## QUICK REFERENCE

| Sprint | Focus | Key Files |
|--------|-------|-----------|
| 0 | Skeleton | App.tsx, styles.css |
| 1 | Data + Markers | types.ts, data.ts |
| 2 | Rail + List | Rail.tsx, PlaceList.tsx |
| 3 | Detail Drawer | DetailDrawer.tsx |
| 4 | Enhanced Data | types.ts, data.ts |
| 5 | Party Cards | PlaceList.tsx |
| 6 | Enhanced Drawer | DetailDrawer.tsx |
| 7 | Map Popup | App.tsx |
| 8 | Timeline Bar | TimelineBar.tsx |
| 9 | Event Strip | EventStrip.tsx |
| 10 | Traffic Layer | SettingsPanel.tsx, routing |
| 11 | Route Line | routing.ts |
| 12 | ETA Badge | App.tsx |
| 13 | Participants | ParticipantsPanel.tsx |
| 14 | Import/Export | ImportModal.tsx, storage.ts |
| 15 | Mobile | All components |

---

## RULES FOR SUCCESS

1. **Fresh chat each sprint** - no context pollution
2. **Verify before continuing** - `npm run dev` must work
3. **One goal per prompt** - resist adding "also do X"
4. **Name files explicitly** - "CREATE src/components/X.tsx"
5. **Include "I have" context** - tell agent what exists
6. **Specify styling details** - pixels, colors, spacing
7. **Keep prompts under 800 words** - shorter = better coherence

# Carnival SC - Copy-Paste Prompts

> Fresh chat for each sprint. Verify before continuing.

---

## SPRINT 0 - Skeleton

```
Build a minimal React + Vite + TypeScript app with a full-screen Google Map.

TECH:
- Vite + React 18 + TypeScript
- @googlemaps/js-api-loader for Google Maps
- Tailwind CSS via CDN in index.html (no build step)

REQUIREMENTS:
1. Map fills entire viewport (100vw x 100vh)
2. Map centers on lat -27.1, lng -48.5, zoom 10
3. Dark minimal aesthetic, body bg #0a0a0f
4. If VITE_GOOGLE_MAPS_API_KEY is missing or "PLACEHOLDER", show centered glass overlay: "Add your Google Maps API key to .env.local"

FILES TO CREATE:
- index.html (Tailwind CDN, dark body)
- vite.config.ts
- package.json (react, react-dom, vite, typescript, @vitejs/plugin-react, @googlemaps/js-api-loader)
- tsconfig.json
- src/main.tsx
- src/App.tsx
- src/styles.css
- .env.local (VITE_GOOGLE_MAPS_API_KEY=PLACEHOLDER)
- .gitignore

GLASS CLASS in styles.css:
.glass {
  background: rgba(10, 12, 18, 0.65);
  border: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 12px;
}

MAP OPTIONS:
disableDefaultUI: true, zoomControl: true, mapTypeControl: false, streetViewControl: false, fullscreenControl: false

Base font 12px system-ui. Text white.
```

---

## SPRINT 1 - Data + Markers

```
I have a working Vite + React + TypeScript app with a full-screen Google Map.

ADD data types and static markers.

CREATE src/types.ts:
export type PlaceType = 'house' | 'party' | 'poi';
export interface Place {
  id: string;
  type: PlaceType;
  name: string;
  lat: number;
  lng: number;
}

CREATE src/data.ts:
import { Place } from './types';
export const PLACES: Place[] = [
  { id: 'bc-house', type: 'house', name: 'BC House', lat: -26.9906, lng: -48.6353 },
  { id: 'gcr-house', type: 'house', name: 'GCR House', lat: -27.3162, lng: -48.5569 },
  { id: 'warung', type: 'party', name: 'Warung', lat: -27.1467, lng: -48.4839 },
  { id: 'p12', type: 'party', name: 'P12', lat: -27.6044, lng: -48.4527 },
  { id: 'green-valley', type: 'party', name: 'Green Valley', lat: -26.9231, lng: -48.6578 },
  { id: 'surreal', type: 'party', name: 'Surreal', lat: -27.5983, lng: -48.5156 },
];

UPDATE src/App.tsx:
1. Import PLACES
2. After map loads, create google.maps.marker.AdvancedMarkerElement for each place
3. Marker: 12px circle div. House=#ffffff, Party=#f472b6, POI=#60a5fa
4. Store markers in ref
5. console.log place name on marker click
```

---

## SPRINT 2 - Rail + List

```
I have a Vite + React + Google Maps app with markers for places.

ADD left navigation rail and place list panel.

CREATE src/components/Rail.tsx:
- Fixed left:0, top:0, bottom:0, width:52px
- Glass background
- Flex column, items-center, pt-4, gap-2
- 3 icon buttons (36px square, rounded-lg, hover:bg-white/10):
  1. 📍 List - toggles place list
  2. ⚙️ Settings - placeholder
  3. ℹ️ Info - placeholder
- Active button: bg-white/10

CREATE src/components/PlaceList.tsx:
- Fixed left:60px, top:8px, bottom:8px, width:220px
- Glass background, p-3, overflow-y-auto
- Header "Places" 13px font-medium, mb-3
- Places as rows: 8px dot + name 12px, hover:bg-white/5, cursor-pointer
- onClick calls onSelect(place.id)

UPDATE src/App.tsx:
1. State: showPlaceList (boolean), selectedPlaceId (string|null)
2. Render Rail, toggle showPlaceList on list button
3. Render PlaceList when open, onSelect sets selectedPlaceId
4. Selected marker gets white ring: box-shadow 0 0 0 3px rgba(255,255,255,0.5)
```

---

## SPRINT 3 - Detail Drawer

```
I have a React + Google Maps app with markers and selection state.

ADD detail drawer when place is selected.

CREATE src/components/DetailDrawer.tsx:
Props: place: Place, onClose: () => void

Layout:
- Fixed bottom:8px, right:8px, width:300px
- Glass background, p-4

Content:
1. Header row: name (14px font-medium) + X button (24px, hover:bg-white/10)
2. Type badge: pill px-2 py-0.5 text-xs rounded-full
   - house: bg-white/20 "Home"
   - party: bg-pink-500/30 "Party"
   - poi: bg-blue-500/30 "POI"
3. Coords: text-xs text-white/50 "-27.14, -48.48"
4. Divider: border-t border-white/10 my-3

UPDATE src/App.tsx:
1. Render DetailDrawer when selectedPlaceId is set
2. Pass onClose that clears selection
3. Pan map to selected place: map.panTo({lat, lng})
```

---

## SPRINT 4 - Enhanced Data

```
I have a React + Google Maps app with places and detail drawer.

ENHANCE Place type with images, times, and links.

UPDATE src/types.ts:
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
  startAt?: string;
  endAt?: string;
  categories?: PartyCategory[];
  links?: PlaceLinks;
  address?: string;
  notes?: string;
}

UPDATE src/data.ts with rich data:
Houses: add address and notes
Parties: add imageUrl (unsplash), startAt (Feb 2026 ISOs), categories, links

Example party:
{
  id: 'warung',
  type: 'party',
  name: 'Warung',
  lat: -27.1467,
  lng: -48.4839,
  imageUrl: 'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=800&q=80',
  startAt: '2026-02-14T23:00:00-03:00',
  categories: ['night', 'club'],
  links: { instagram: 'https://instagram.com/waraborada', tickets: 'https://warung.com.br' },
  address: 'Praia Brava, Itajaí'
}

Add similar data for: p12, green-valley, surreal (vary times Feb 14-17, categories)
```

---

## SPRINT 5 - Party Cards

```
I have a React + Google Maps app with enhanced Place data including imageUrl and startAt.

UPDATE PlaceList to show parties as image cards.

UPDATE src/components/PlaceList.tsx:

Sections:
1. "Bases" - houses as simple rows (dot + name)
2. "Parties" - as wide image cards
3. "POIs" - simple rows (if any)

Section header: text-xs text-white/40 uppercase tracking-wide mb-2 mt-4

Simple row: flex items-center gap-2 py-2 px-2, 8px dot, name text-xs, hover:bg-white/5

Party card:
- Width 100%, height 72px
- rounded-lg overflow-hidden relative
- Background: imageUrl cover
- Gradient overlay: linear-gradient(to top, rgba(0,0,0,0.8), transparent)
- Content absolute bottom-0 p-2:
  - Name 12px font-medium white truncate
  - Time text-[10px] text-white/70: format as "Sat 14, 11pm"
  - One category pill: text-[8px] bg-white/20 px-1.5 rounded
- Hover: scale-[1.02] transition
- Cursor pointer, onClick selects

Time format helper:
new Date(startAt).toLocaleDateString('en-US',{weekday:'short',day:'numeric'}) + ', ' +
new Date(startAt).toLocaleTimeString('en-US',{hour:'numeric',hour12:true}).toLowerCase()
```

---

## SPRINT 6 - Enhanced Drawer

```
I have a React + Google Maps app with party image cards.

ENHANCE DetailDrawer with images, times, and action buttons.

UPDATE src/components/DetailDrawer.tsx:

Layout: width 320px, no top padding (image edge-to-edge)

Structure:
1. Image banner (if imageUrl):
   - Height 140px, object-cover, w-full
   - If no image: colored placeholder by type

2. Content area (p-4):
   a. Name (15px font-semibold) + X close button
   b. Type badge + category pills (if party)
   c. Time row (if startAt): 📅 + formatted date/time, text-sm text-white/70
   d. Address row (if address): 📍 + address, text-xs text-white/50
   e. Notes (if notes): text-xs text-white/40 italic mt-2
   f. Divider border-t border-white/10 my-3
   g. Action buttons row (flex gap-2):
      - Instagram (if links.instagram): flex-1 py-2 rounded-lg text-xs font-medium bg-gradient-to-r from-purple-500 to-pink-500
      - Tickets (if links.tickets): bg-amber-500
      - Directions (always): bg-white/10, opens https://www.google.com/maps/dir/?api=1&destination={lat},{lng}

Button text: "IG", "🎫 Tickets", "→ Go"
All buttons open in new tab (target="_blank")
```

---

## SPRINT 7 - Map Popup

```
I have a React + Google Maps app with enhanced detail drawer.

ADD InfoWindow popup on marker click.

UPDATE src/App.tsx:

When marker clicked:
1. Set selectedPlaceId
2. Open google.maps.InfoWindow anchored to marker

InfoWindow content (template string):
<div style="background:#1a1a2e;color:white;padding:12px;border-radius:8px;min-width:200px;font-family:system-ui;font-size:12px;">
  ${place.imageUrl ? `<img src="${place.imageUrl}" style="width:100%;height:80px;object-fit:cover;border-radius:4px;margin-bottom:8px;">` : ''}
  <div style="font-weight:600;font-size:14px;margin-bottom:4px;">${place.name}</div>
  ${place.startAt ? `<div style="color:#aaa;font-size:11px;margin-bottom:8px;">${formatTime(place.startAt)}</div>` : ''}
  <div style="display:flex;gap:6px;margin-top:8px;">
    ${place.links?.instagram ? `<a href="${place.links.instagram}" target="_blank" style="flex:1;background:#833AB4;color:white;padding:6px;border-radius:4px;text-align:center;text-decoration:none;font-size:10px;">IG</a>` : ''}
    ${place.links?.tickets ? `<a href="${place.links.tickets}" target="_blank" style="flex:1;background:#f59e0b;color:white;padding:6px;border-radius:4px;text-align:center;text-decoration:none;font-size:10px;">Tickets</a>` : ''}
    <a href="https://www.google.com/maps/dir/?api=1&destination=${place.lat},${place.lng}" target="_blank" style="flex:1;background:#374151;color:white;padding:6px;border-radius:4px;text-align:center;text-decoration:none;font-size:10px;">Go</a>
  </div>
</div>

Rules:
- Store InfoWindow in ref, close previous before opening new
- One InfoWindow at a time

Helper:
function formatTime(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString('en-US',{weekday:'short',month:'short',day:'numeric'}) + ', ' + d.toLocaleTimeString('en-US',{hour:'numeric',minute:'2-digit',hour12:true});
}
```

---

## SPRINT 8 - Timeline Bar

```
I have a React + Google Maps app with popups.

ADD timeline bar showing Carnival days Feb 13-23.

CREATE src/components/TimelineBar.tsx:
Props: selectedDate: string, onSelectDate: (date: string) => void, places: Place[]

Layout:
- Fixed top:8px, left:68px, right:8px
- Glass background, px-3 py-2
- Flex row gap-2 overflow-x-auto (hide scrollbar with CSS)

Generate days:
const days = Array.from({length:11}, (_,i) => `2026-02-${(13+i).toString().padStart(2,'0')}`);

Day pill:
- min-w-[48px] flex flex-col items-center py-1.5 px-2 rounded-lg cursor-pointer
- Unselected: hover:bg-white/5
- Selected: bg-white/15

Content:
- Weekday: text-xs text-white/50 ("Fri", "Sat"...)
- Day number: text-sm font-medium ("13", "14"...)
- Event dot: tiny pink dot if any party startAt matches this date

UPDATE src/App.tsx:
1. State: selectedDate = '2026-02-14'
2. Render TimelineBar with props
3. Pass places for event counting

Hide scrollbar CSS:
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
```

---

## SPRINT 9 - Event Strip

```
I have a React + Google Maps app with timeline bar.

ADD event strip showing parties for selected day.

CREATE src/components/EventStrip.tsx:
Props: places: Place[], selectedDate: string, selectedPlaceId: string|null, onSelectPlace: (id: string) => void

Layout:
- Fixed top:60px, left:68px, right:8px
- Height 88px
- Glass background, px-3 py-2
- Flex row gap-3 overflow-x-auto no-scrollbar
- scroll-snap-type: x mandatory

Filter: parties only, startAt date matches selectedDate, sort by time

Empty state: centered "No events" text-white/40

Event card:
- w-[180px] h-[72px] flex-shrink-0 rounded-lg overflow-hidden relative
- scroll-snap-align: start
- Background: imageUrl cover
- Gradient overlay from bottom
- Selected: ring-2 ring-white/50

Card content (absolute bottom-0 p-2):
- Name 12px font-medium truncate
- Time text-[10px] text-white/70
- Category pill

onClick: onSelectPlace(place.id)

UPDATE src/App.tsx:
1. Render EventStrip below TimelineBar
2. Connect all props

Desktop only: hidden md:flex (handle mobile later)
```

---

## SPRINT 10 - Traffic Toggle

```
I have a React + Google Maps app with timeline and event strip.

ADD traffic layer toggle.

UPDATE src/types.ts:
export interface MapSettings {
  showTraffic: boolean;
  showLabels: boolean;
  showRoute: boolean;
}

CREATE src/components/SettingsPanel.tsx:
Props: settings: MapSettings, onUpdate: (s: MapSettings) => void

Layout:
- Fixed left:60px, bottom:8px, width:200px
- Glass background, p-3

Toggle rows (flex justify-between items-center mb-2):
- "Traffic" toggle
- "Route" toggle (for later)

Toggle switch:
<button onClick={() => onUpdate({...settings, showTraffic: !settings.showTraffic})}
  className={`w-9 h-5 rounded-full flex items-center px-0.5 transition ${settings.showTraffic ? 'bg-green-500' : 'bg-white/20'}`}>
  <div className={`w-4 h-4 rounded-full bg-white transition-transform ${settings.showTraffic ? 'translate-x-4' : ''}`}/>
</button>

UPDATE src/App.tsx:
1. State: settings with defaults {showTraffic:false, showLabels:true, showRoute:true}
2. Create TrafficLayer after map loads: new google.maps.TrafficLayer()
3. Effect: toggle traffic layer based on settings.showTraffic
   if (showTraffic) trafficLayer.setMap(map) else trafficLayer.setMap(null)
4. Rail settings button toggles SettingsPanel
```

---

## SPRINT 11 - Route Line

```
I have a React + Google Maps app with traffic toggle.

ADD route from nearest house to selected party.

CREATE src/services/routing.ts:
export interface RouteResult {
  path: google.maps.LatLng[];
  durationSeconds: number;
  distanceMeters: number;
  durationInTraffic?: number;
}

export async function computeRoute(
  service: google.maps.DirectionsService,
  origin: {lat:number;lng:number},
  destination: {lat:number;lng:number}
): Promise<RouteResult|null> {
  const result = await service.route({
    origin, destination,
    travelMode: google.maps.TravelMode.DRIVING,
    drivingOptions: { departureTime: new Date(), trafficModel: google.maps.TrafficModel.BEST_GUESS }
  });
  const leg = result.routes[0].legs[0];
  return {
    path: result.routes[0].overview_path,
    durationSeconds: leg.duration?.value || 0,
    distanceMeters: leg.distance?.value || 0,
    durationInTraffic: leg.duration_in_traffic?.value
  };
}

export function findNearestHouse(houses: Place[], target: {lat:number;lng:number}): Place|null {
  // Haversine distance, return closest
}

UPDATE src/App.tsx:
1. Create DirectionsService after map loads
2. Create Polyline: strokeColor '#60a5fa', strokeOpacity 0.8, strokeWeight 4
3. State: routeResult
4. When party selected + showRoute: compute route from nearest house, set polyline path
5. Clear route when deselected or disabled
```

---

## SPRINT 12 - ETA Badge

```
I have a React + Google Maps app with route line.

ADD ETA badge at route midpoint.

UPDATE src/App.tsx:

When routeResult exists:
1. Calculate midpoint: path[Math.floor(path.length/2)]
2. Create AdvancedMarkerElement with HTML content:

<div class="glass" style="padding:6px 10px;font-size:11px;white-space:nowrap;pointer-events:none;">
  <span style="font-weight:600;">${formatDuration(durationInTraffic || durationSeconds)}</span>
  <span style="color:rgba(255,255,255,0.5);margin-left:6px;">${formatDistance(distanceMeters)}</span>
</div>

Helpers:
function formatDuration(s: number): string {
  const m = Math.round(s/60);
  return m < 60 ? `${m} min` : `${Math.floor(m/60)}h ${m%60}m`;
}
function formatDistance(m: number): string {
  return `${(m/1000).toFixed(1)} km`;
}

Store marker in ref, remove when route cleared.
```

---

## SPRINT 13 - Participants

```
I have a React + Google Maps app with routing and ETA.

ADD participants with arrival dates.

UPDATE src/types.ts:
export interface Participant {
  id: string;
  name: string;
  arrivalDate: string;
  color: string;
}

UPDATE src/data.ts:
export const PARTICIPANTS: Participant[] = [
  { id: 'leo', name: 'Leonardo', arrivalDate: '2026-02-14', color: '#60a5fa' },
  { id: 'arthur', name: 'Arthur', arrivalDate: '2026-02-14', color: '#34d399' },
  { id: 'cristiano', name: 'Cristiano', arrivalDate: '2026-02-15', color: '#f472b6' },
];

CREATE src/components/ParticipantsPanel.tsx:
- Fixed left:60px, top:50%, transform:-translate-y-1/2, width:180px
- Glass background, p-3
- Header "Crew" 13px font-medium mb-3
- Each participant:
  - Colored dot + name
  - Badge: "Arrives Feb 14" or "Here!" (if selectedDate >= arrivalDate)

UPDATE TimelineBar: show colored dots below days for arrivals

UPDATE Rail: info button toggles ParticipantsPanel

UPDATE App.tsx: track which panel is open (places|settings|participants), pass selectedDate
```

---

## SPRINT 14 - Import/Export

```
I have a React + Google Maps app with participants.

ADD import/export JSON functionality.

CREATE src/utils/storage.ts:
const KEY = 'carnival_sc_v1';

export function savePlaces(places: Place[]): void {
  localStorage.setItem(KEY, JSON.stringify(places));
}

export function loadPlaces(): Place[]|null {
  const d = localStorage.getItem(KEY);
  return d ? JSON.parse(d) : null;
}

export function exportPlaces(places: Place[]): void {
  const blob = new Blob([JSON.stringify(places,null,2)], {type:'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `carnival-${new Date().toISOString().split('T')[0]}.json`;
  a.click();
}

CREATE src/components/ImportModal.tsx:
Props: isOpen, onClose, onImport: (places: Place[]) => void

Layout:
- Overlay: fixed inset-0 bg-black/50 flex items-center justify-center
- Modal: glass w-96 p-4
- Header + X button
- Textarea: rows-10 w-full bg-black/30 rounded p-2 text-xs font-mono
- Error message area
- Buttons: Cancel (bg-white/10), Import (bg-green-500)

Import: JSON.parse, validate array, merge by id

UPDATE Rail: add export ⬇️ and import ⬆️ buttons

UPDATE App.tsx:
1. Load places on mount (merge with defaults)
2. Save on change
3. showImportModal state
4. Connect export/import handlers
```

---

## SPRINT 15 - Mobile

```
I have a React + Google Maps app with all features.

MAKE IT MOBILE RESPONSIVE.

UPDATE index.html viewport:
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">

Rail on mobile (< md):
- Position: fixed bottom-0 left-0 right-0, height 56px
- Flex row justify-around items-center
- Add pb-safe for iPhone

TimelineBar on mobile:
- Position top:0 left:0 right:0 (no rail offset)
- Smaller pills

EventStrip: hidden on mobile (hidden md:flex)

PlaceList on mobile:
- Bottom sheet: fixed bottom-[64px] left-0 right-0
- Max-height 50vh
- Rounded-t-xl
- Drag handle pill at top

DetailDrawer on mobile:
- Bottom sheet: fixed bottom-[64px] left-0 right-0
- Max-height 60vh
- Rounded-t-xl
- Image height 100px

CSS safe areas:
@supports (padding-bottom: env(safe-area-inset-bottom)) {
  .pb-safe { padding-bottom: env(safe-area-inset-bottom); }
}

Use Tailwind: md:left-[68px], md:bottom-2, hidden md:flex, md:hidden
```

---

## DONE

After Sprint 15 you have:
- Full-screen Google Map
- Places with images, times, links
- Timeline navigation (Feb 13-23)
- Event strip for selected day
- Detail drawer with actions
- Map popups with buttons
- Traffic layer toggle
- Route with ETA
- Participants tracking
- Import/export JSON
- Mobile responsive

Bonus sprints in full doc: time simulation, weather, Gemini import, boundaries.

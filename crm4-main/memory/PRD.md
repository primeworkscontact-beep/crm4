# Dolgozó CRM - PRD

## Admin Credentials (PERMANENT)
- **Email**: admin@dolgozocrm.hu
- **Password**: admin123

## Tech Stack
- **Backend**: FastAPI, MongoDB, Python
- **Frontend**: React, TailwindCSS, Shadcn/ui, Recharts, @hello-pangea/dnd, FullCalendar
- **Auth**: JWT token alapú

## User Personas
- **Admin**: Teljes jogosultság, minden próbát lát a naptárban, kategória/felhasználó kezelés
- **Toborzó**: Saját dolgozók kezelése, saját próbák láthatósága, NEM tudja módosítani a nevét

## What's Been Implemented

### Session 1-3: Kategória, Dashboard, Naptár, Értesítések ✅

### Session 4: Próba Pozíciók Kezelése ✅
**Próba pozíciók rendszere:**
- `GET /api/projects/{id}/trials/{trial_id}/positions` - Pozíciók lekérése
- `POST /api/projects/{id}/trials/{trial_id}/positions` - Új pozíció
- `PUT /api/projects/{id}/trials/{trial_id}/positions/{id}` - Szerkesztés
- `DELETE /api/projects/{id}/trials/{trial_id}/positions/{id}` - Törlés

**Frontend UI:**
- Próba pozíció dialog (ProjectDetailPage)
- Projekt pozíciók gyors választó dropdown
- Létszámigény mező (headcount)
- Egyéb elvárások textarea
- "Pozíció hozzáadása a projekthez is" switch (új pozíció esetén)
- Pozíciónkénti dolgozó hozzáadás gomb
- Teljesítés státusz badge (X/Y fő)

**Adatmodell:**
```
TrialPositionCreate:
  - position_id: Optional[str]  # Meglévő projekt pozíció ID
  - position_name: str          # Pozíció neve
  - headcount: int              # Létszámigény
  - requirements: str           # Egyéb elvárások
  - add_to_project: bool        # Hozzáadjuk a projekthez?

TrialPositionResponse:
  - id, trial_id, position_id, position_name
  - headcount, requirements, assigned_count
```

## API Endpoints Summary

### Categories
```
GET/POST/PUT/DELETE /api/categories
PUT /api/categories/reorder
GET /api/categories/stats
```

### Calendar & Notifications
```
GET /api/calendar/trials
GET /api/calendar/projects
GET/PUT/DELETE /api/notifications
```

### Trial Positions (NEW)
```
GET    /api/projects/{id}/trials/{trial_id}/positions
POST   /api/projects/{id}/trials/{trial_id}/positions
PUT    /api/projects/{id}/trials/{trial_id}/positions/{position_id}
DELETE /api/projects/{id}/trials/{trial_id}/positions/{position_id}
PUT    /api/projects/{id}/trials/{trial_id}/workers/{worker_id}/position
```

## Testing Status
- Backend API: 100% (26 teszt)
- Frontend UI: 85%
- Integration: 95%

## Navigation Structure
```
/ (Dashboard)
├── /calendar (Naptár)
├── /notifications (Értesítések)
├── /workers (Dolgozók)
├── /projects (Projektek)
│   └── /projects/{id} (Projekt részletek)
│       └── Próbák tab -> Pozíciók kezelése
├── /settings (Beállítások)
└── /admin (Admin)
```

## Prioritized Backlog
### P0 (Critical) - DONE ✅
- ✅ Kategória CRUD + drag&drop
- ✅ Dashboard statisztikákkal
- ✅ Naptár (admin/toborzó jogosultság)
- ✅ Értesítések rendszer
- ✅ Profil korlátozás
- ✅ Próba pozíciók (létszám, elvárások)

### P1 (Important) - Future
- Próba drag&drop a naptárban (dátum változtatás)
- Email értesítés próba előtt 1 nappal
- Naptár export (iCal)
- Dolgozó automatikus pozícióhoz rendelés

### P2 (Nice to have)
- Push notification böngészőben
- Több időszak választó dashboard-on
- Mobil responsive naptár nézet

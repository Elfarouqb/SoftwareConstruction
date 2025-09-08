# 🚗 MobyPark API Reverse-Engineering Analyse Rapport

📅 **Analyse Datum**: 04-09-2025  
📊 **Versie**: 1.0  
🏢 **Systeem**: MobyPark Parking API (Legacy)  

---

## 📋 EXECUTIVE SUMMARY

### Systeem Overzicht

| Metric | Waarde |
|--------|--------|
| **Totaal aantal Python files** | 4 |
| **Lines of Code** | ~1,477 |
| **Gebruikte framework** | Python HTTP Server (geen framework) |
| **Database** | JSON bestanden (file-based) |
| **Programming taal** | Python 3.x |
| **API Type** | RESTful (handmatig geïmplementeerd) |
| **Authenticatie** | Session-based met MD5 hashing |

### 🏗️ Architectuur Patronen
- **Monolithische architectuur** zonder framework
- **File-based data storage** (JSON/CSV)
- **In-memory session management** (verliest data bij herstart)
- **Procedurele code structuur** met minimale OOP

### ⚠️ KRITIEKE BEVINDINGEN

#### 🔴 BLOKKERENDE ISSUES (P0)
1. **MD5 Password Hashing** - Cryptografisch onveilig (server.py:17, 48, 377)
2. **In-Memory Sessions** - Data verlies bij herstart (session_manager.py:1)
3. **SQL Injection achtige bugs** - Line 119: `len(filtered) < 0` is altijd False
4. **Missing Authentication** - Veel endpoints missen auth checks
5. **Race Conditions** - Geen locking bij file writes

#### 🟠 HOGE PRIORITEIT ISSUES (P1)
1. **Geen Database** - JSON files als database
2. **Performance bottlenecks** - O(n) searches door alle data
3. **Geen Error Recovery** - Crashes bij corrupte JSON
4. **Hardcoded configuratie** - Poort 8000, localhost
5. **Memory leaks** - Sessions worden nooit opgeruimd

---

## 📁 FILE-BY-FILE ANALYSE

### 1️⃣ `server.py` - Hoofdbestand API Server

#### FILE METADATA
```
Filepath: /api/server.py
Type: Controller/Main Server
Framework/Library: Python HTTP BaseHTTPRequestHandler
Lines of Code: 925
Complexiteit: KRITIEK (zeer hoog)
```

#### PURPOSE & RESPONSIBILITY
- **Primaire functie**: Complete API server met alle endpoints
- **Business domein**: Alle MobyPark functionaliteit (Gebruikers, Parkeerplaatsen, Reserveringen, Betalingen, Voertuigen, Facturatie)
- **Architecturale rol**: Monolithische server - presentation + business logic + data access in één file

#### DEPENDENCIES MAPPING
```
IMPORTS:
- json (standard library)
- hashlib (standard library) 
- uuid (standard library)
- datetime (standard library)
- http.server (standard library)
- storage_utils (intern) - Data persistence layer
- session_manager (intern) - Session management
- session_calculator (intern) - Prijsberekeningen

GEBRUIKT DOOR:
- Geen andere files (is het hoofdprogramma)
```

#### 🔐 SECURITY VULNERABILITIES

##### KRITIEK - Onveilige Password Hashing
```python
# Line 17, 48, 377
hashed_password = hashlib.md5(password.encode()).hexdigest()
```
**Impact**: MD5 is cryptografisch gebroken. Wachtwoorden kunnen binnen seconden gekraakt worden.
**Aanbeveling**: Gebruik bcrypt, scrypt of Argon2

##### KRITIEK - Logica Bug in Session Stop
```python
# Line 119
if len(filtered) < 0:  # Dit is ALTIJD False!
    self.send_response(401)
```
**Impact**: Gebruikers kunnen geen sessies stoppen
**Fix**: Moet zijn `if len(filtered) == 0:`

##### HOOG - Missing Input Validation
```python
# Line 26 - Direct toevoegen aan set zonder validatie
users.add({
    'username': username,
    'password': hashed_password,
    'name': name
})
```
**Impact**: Geen validatie op username format, password sterkte, of name inhoud

##### HOOG - Session Hijacking Mogelijk
```python
# Line 52
token = str(uuid.uuid4())
```
**Impact**: Tokens worden over HTTP verzonden (geen HTTPS), kunnen onderschept worden

#### 📊 API ENDPOINTS OVERZICHT

| Endpoint | Method | Purpose | Auth Required | Admin Only |
|----------|--------|---------|---------------|------------|
| `/register` | POST | Nieuwe gebruiker registreren | ❌ | ❌ |
| `/login` | POST | Inloggen | ❌ | ❌ |
| `/logout` | GET | Uitloggen | ✅ | ❌ |
| `/profile` | GET/PUT | Profiel bekijken/wijzigen | ✅ | ❌ |
| `/parking-lots` | GET | Alle parkeerplaatsen | ❌ | ❌ |
| `/parking-lots` | POST | Nieuwe parkeerplaats | ✅ | ✅ |
| `/parking-lots/{id}` | GET/PUT/DELETE | Specifieke parkeerplaats | ✅* | ✅* |
| `/parking-lots/{id}/sessions/start` | POST | Start parkeersessie | ✅ | ❌ |
| `/parking-lots/{id}/sessions/stop` | POST | Stop parkeersessie | ✅ | ❌ |
| `/reservations` | POST | Nieuwe reservering | ✅ | ❌ |
| `/reservations/{id}` | GET/PUT/DELETE | Specifieke reservering | ✅ | ❌** |
| `/vehicles` | POST | Voertuig toevoegen | ✅ | ❌ |
| `/vehicles/{id}` | PUT/DELETE | Voertuig wijzigen/verwijderen | ✅ | ❌ |
| `/vehicles/{id}/entry` | POST | Voertuig entry registreren | ✅ | ❌ |
| `/vehicles/{id}/reservations` | GET | Voertuig reserveringen | ✅ | ❌ |
| `/vehicles/{id}/history` | GET | Voertuig geschiedenis | ✅ | ❌ |
| `/payments` | GET/POST | Betalingen | ✅ | ❌ |
| `/payments/refund` | POST | Terugbetaling | ✅ | ✅ |
| `/payments/{id}` | PUT | Betaling voltooien | ✅ | ❌ |
| `/billing` | GET | Facturatie overzicht | ✅ | ❌ |
| `/billing/{username}` | GET | Facturatie voor gebruiker | ✅ | ✅ |

*Sommige operaties vereisen admin rechten  
**Admin of eigenaar van reservering

#### 🐛 BUGS & LOGIC ERRORS

1. **Line 59-68**: Login loop stopt bij eerste gebruiker die niet matcht
2. **Line 119**: `len(filtered) < 0` is altijd False
3. **Line 171**: String vergelijking met nummer: `data.get("parkinglot", -1) not in parking_lots`
4. **Line 228-229**: `datetime.now()` wordt niet geserialiseerd voor JSON
5. **Line 376**: Check op `data["password"]` zonder te controleren of key bestaat
6. **Line 480**: `next()` zonder default waarde kan StopIteration exception gooien
7. **Line 583**: Delete reservering, maar daarna wordt deleted ID gebruikt
8. **Line 680**: `session_user` niet gedefinieerd in scope
9. **Line 759**: `payment["username"]` bestaat niet in payment structuur

---

### 2️⃣ `session_manager.py` - Session Management

#### FILE METADATA
```
Filepath: /api/session_manager.py
Type: Service/Utility
Lines of Code: 10
Complexiteit: LAAG (maar kritiek probleem)
```

#### PURPOSE & RESPONSIBILITY
- **Primaire functie**: Beheer van gebruikerssessies
- **Business domein**: Authenticatie & Autorisatie
- **Architecturale rol**: In-memory session store

#### 🔴 KRITIEKE PROBLEMEN

##### In-Memory Storage
```python
sessions = {}  # Line 1
```
**Impact**: 
- Sessions verdwijnen bij server herstart
- Geen horizontale scaling mogelijk
- Memory groeit onbeperkt

**Aanbeveling**: Redis of database gebruiken

##### Geen Session Expiry
- Sessions verlopen nooit
- Geen cleanup mechanisme
- Memory leak

##### Geen Session Validation
- Geen checks op session data integriteit
- Geen IP binding
- Geen User-Agent checks

---

### 3️⃣ `session_calculator.py` - Prijs & Hash Calculaties

#### FILE METADATA
```
Filepath: /api/session_calculator.py
Type: Business Logic / Utility
Lines of Code: 48
Complexiteit: MEDIUM
```

#### PURPOSE & RESPONSIBILITY
- **Primaire functie**: Parkeerkosten berekening & transactie hashing
- **Business domein**: Facturatie & Betalingen
- **Architecturale rol**: Business logic layer

#### FUNCTIONALITEIT ANALYSE

##### `calculate_price()` - Lines 7-29
```python
def calculate_price(parkinglot, sid, data):
```
**Business Logic**:
1. Gratis eerste 3 minuten (180 seconden)
2. Dagtarief bij meerdere dagen
3. Uurtarief voor enkele dag
4. Maximum dagtarief cap

**🐛 BUG**: Line 26 - `parkinglot.get("daytarief", 999)` 
- Default van 999 is te hoog
- Kan leiden tot onverwacht hoge kosten

##### `generate_payment_hash()` - Line 33-34
```python
def generate_payment_hash(sid, data):
    return md5(str(sid + data["licenseplate"]).encode("utf-8")).hexdigest()
```
**🔐 SECURITY ISSUE**: MD5 voor payment hash
- Voorspelbaar
- Collision attacks mogelijk

---

### 4️⃣ `storage_utils.py` - Data Persistence Layer

#### FILE METADATA
```
Filepath: /api/storage_utils.py  
Type: Data Access Layer / Repository
Lines of Code: 90
Complexiteit: LAAG
```

#### PURPOSE & RESPONSIBILITY
- **Primaire functie**: File-based data persistence
- **Business domein**: Data opslag voor alle modules
- **Architecturale rol**: Data access layer

#### 🔴 KRITIEKE PROBLEMEN

##### Geen Atomic Writes
```python
def write_json(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file, default=str)
```
**Impact**: Data corruptie bij crash tijdens write

##### Geen Locking
- Race conditions bij concurrent writes
- Data verlies mogelijk

##### Geen Backup/Recovery
- Geen versioning
- Geen rollback mogelijkheid

---

## 🗄️ DATA SCHEMA ANALYSE

### Users Collection
```json
{
  "id": "string",
  "username": "string (unique)",
  "password": "string (MD5 hash)",
  "name": "string",
  "email": "string",
  "phone": "string",
  "role": "USER|ADMIN",
  "created_at": "date string",
  "birth_year": "number",
  "active": "boolean"
}
```

### Parking Lots Collection
```json
{
  "id": "string",
  "name": "string",
  "location": "string",
  "address": "string", 
  "capacity": "number",
  "reserved": "number",
  "tariff": "number (hourly rate)",
  "daytariff": "number (day maximum)",
  "created_at": "date string",
  "coordinates": {
    "lat": "number",
    "lng": "number"
  }
}
```

### Sessions Collection (per parking lot)
```json
{
  "licenseplate": "string",
  "started": "datetime string",
  "stopped": "datetime string|null",
  "user": "username string"
}
```

### Vehicles Collection
```json
{
  "[username]": {
    "[license_plate_key]": {
      "licenseplate": "string",
      "name": "string",
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  }
}
```

### Payments Collection
```json
{
  "transaction": "string (hash)",
  "amount": "number",
  "initiator": "string (username)",
  "created_at": "datetime string",
  "completed": "boolean|datetime string",
  "hash": "string (validation UUID)",
  "t_data": "object (transaction data)"
}
```

---

## 🚨 SECURITY VULNERABILITY RAPPORT

### KRITIEK (P0)

1. **MD5 Password Hashing**
   - **Locatie**: server.py:17, 48, 377
   - **OWASP**: A02:2021 – Cryptographic Failures
   - **Fix**: Implementeer bcrypt/scrypt/Argon2

2. **Geen HTTPS**
   - **Locatie**: server.py:922
   - **OWASP**: A02:2021 – Cryptographic Failures
   - **Fix**: SSL/TLS implementeren

3. **Session Hijacking**
   - **Locatie**: session_manager.py
   - **OWASP**: A07:2021 – Identification and Authentication Failures
   - **Fix**: Secure cookies, HTTPS, session binding

### HOOG (P1)

1. **Geen Input Sanitization**
   - **Locatie**: Alle POST/PUT endpoints
   - **OWASP**: A03:2021 – Injection
   - **Fix**: Input validatie framework

2. **Path Traversal Mogelijk**
   - **Locatie**: storage_utils.py file operations
   - **OWASP**: A01:2021 – Broken Access Control
   - **Fix**: Path sanitization

3. **Missing Rate Limiting**
   - **Locatie**: Alle endpoints
   - **OWASP**: A04:2021 – Insecure Design
   - **Fix**: Rate limiting implementeren

---

## ⚡ PERFORMANCE BOTTLENECKS

### KRITIEK

1. **O(n) Searches**
   ```python
   # server.py:50 - Linear search door alle users
   for user in users:
       if user.get("username") == username
   ```
   **Impact**: Traag bij veel gebruikers
   **Fix**: Indexing/database gebruiken

2. **Volledig File Lezen/Schrijven**
   ```python
   # Elke operatie leest/schrijft complete file
   users = load_json('data/users.json')
   save_user_data(users)
   ```
   **Impact**: Memory & I/O bottleneck
   **Fix**: Database met queries

3. **Geen Caching**
   - Parkeerplaats data wordt elke keer opnieuw geladen
   - Geen response caching
   - **Fix**: Redis/Memcached implementeren

### Scalability Issues

- **Single-threaded server**
- **Geen connection pooling**
- **File locks blokkeren concurrent access**
- **In-memory sessions limiteren horizontal scaling**

---

## 📋 FUNCTIONAL REQUIREMENTS EXTRACTED

### FR-001: Gebruiker Registratie
**Beschrijving**: Systeem moet nieuwe gebruikers kunnen registreren
**Geïmplementeerd in**: server.py:12-35
**Status**: Gedeeltelijk geïmplementeerd
**Test coverage**: 0%
**Business Priority**: Must Have
**Issues**: Geen email verificatie, zwakke password requirements

### FR-002: Gebruiker Authenticatie
**Beschrijving**: Gebruikers moeten kunnen inloggen met username/password
**Geïmplementeerd in**: server.py:38-68
**Status**: Geïmplementeerd (met security issues)
**Test coverage**: 0%
**Business Priority**: Must Have

### FR-003: Parkeerplaats Beheer
**Beschrijving**: Admins kunnen parkeerplaatsen toevoegen/wijzigen/verwijderen
**Geïmplementeerd in**: server.py:71-148, 331-362, 512-558
**Status**: Volledig geïmplementeerd
**Test coverage**: 0%
**Business Priority**: Must Have

### FR-004: Parkeersessie Management
**Beschrijving**: Start/stop parkeren met kenteken registratie
**Geïmplementeerd in**: server.py:84-131
**Status**: Gedeeltelijk (stop functie heeft bug)
**Test coverage**: 0%
**Business Priority**: Must Have

### FR-005: Reserveringen
**Beschrijving**: Gebruikers kunnen parkeerplaatsen reserveren
**Geïmplementeerd in**: server.py:151-194, 385-427, 561-597
**Status**: Basis functionaliteit aanwezig
**Test coverage**: 0%
**Business Priority**: Must Have

### FR-006: Voertuig Beheer
**Beschrijving**: Gebruikers kunnen voertuigen registreren
**Geïmplementeerd in**: server.py:197-269, 430-466, 600-625, 864-919
**Status**: Geïmplementeerd
**Test coverage**: 0%
**Business Priority**: Should Have

### FR-007: Betalingen
**Beschrijving**: Betaling processing en refunds
**Geïmplementeerd in**: server.py:272-328, 468-508, 748-792
**Status**: Basis implementatie
**Test coverage**: 0%
**Business Priority**: Must Have

### FR-008: Facturatie
**Beschrijving**: Overzicht kosten en betalingen per gebruiker
**Geïmplementeerd in**: server.py:795-861
**Status**: Geïmplementeerd
**Test coverage**: 0%
**Business Priority**: Must Have

---

## 📊 NON-FUNCTIONAL REQUIREMENTS

### NFR-001: Performance
**Categorie**: Performance
**Huidige implementatie**: Single-threaded, file-based
**Gemeten waarde**: ~10-50 requests/second (geschat)
**Issues**: O(n) operations, geen caching
**Recommended target**: 1000+ requests/second

### NFR-002: Beveiliging
**Categorie**: Security
**Huidige implementatie**: MD5 hashing, geen HTTPS
**Issues**: Multiple kritieke vulnerabilities
**Recommended target**: OWASP Top 10 compliance

### NFR-003: Beschikbaarheid
**Categorie**: Availability
**Huidige implementatie**: Single instance, geen failover
**Issues**: Single point of failure
**Recommended target**: 99.9% uptime

### NFR-004: Schaalbaarheid
**Categorie**: Scalability
**Huidige implementatie**: Niet schaalbaar
**Issues**: In-memory sessions, file-based storage
**Recommended target**: Horizontal scaling capability

---

## 🏨 HOTEL INTEGRATIE ANALYSE

### Huidige Status
- **Geen hotel integratie gevonden** in codebase
- Geen koppeling tussen hotels en parkeerplaatsen
- Geen gratis parkeren logic voor hotelgasten
- Geen API endpoints voor hotel management

### Missing Functionaliteit
1. Hotel entity/model ontbreekt
2. Koppeling hotel <-> parkeerplaats ontbreekt
3. Voucher/discount systeem voor hotelgasten ontbreekt
4. Check-in/check-out integratie ontbreekt

---

## 🏢 ZAKELIJKE KLANTEN ANALYSE

### Huidige Status
- Basis multi-vehicle support aanwezig (vehicles per user)
- Geen specifieke business account functionaliteit
- Geen bulk operations
- Geen aparte facturatie voor zakelijke klanten

### Problemen
1. Vehicles gekoppeld aan individuele users, niet aan organisaties
2. Geen fleet management capabilities
3. Geen consolidated billing
4. Geen reporting voor zakelijke klanten

---

## 🔧 TECHNICAL DEBT REGISTER

### KRITIEK (Onmiddellijke actie vereist)
1. MD5 password hashing → Moderne hashing
2. In-memory sessions → Redis/Database
3. Bug in session stop logic → Fix conditie
4. Geen HTTPS → SSL implementeren

### HOOG (Sprint 1-2)
1. File-based storage → PostgreSQL/MongoDB
2. Monolithische architectuur → Microservices
3. Geen testing → Unit/Integration tests
4. Manual JSON operations → ORM/ODM

### MEDIUM (Sprint 3-4)
1. Geen API versioning
2. Inconsistente error responses
3. Geen logging framework
4. Hardcoded configuratie

### LAAG (Backlog)
1. Code duplicatie reduceren
2. Magic strings vervangen
3. Documentatie toevoegen
4. Response caching

---

## 🚀 MIGRATIE AANBEVELINGEN

### Fase 1: Security & Stabiliteit (Week 1-2)
1. Implementeer bcrypt voor passwords
2. Voeg HTTPS toe
3. Fix kritieke bugs
4. Implementeer basic logging

### Fase 2: Database Migratie (Week 3-4)
1. PostgreSQL setup
2. Data migratie scripts
3. ORM implementatie (SQLAlchemy)
4. Session store naar Redis

### Fase 3: Architectuur Modernisatie (Week 5-8)
1. FastAPI framework implementatie
2. API documentatie (OpenAPI/Swagger)
3. Authentication service extractie
4. Docker containerization

### Fase 4: Features & Integraties (Week 9-12)
1. Hotel integratie ontwikkelen
2. Business accounts implementeren
3. Automated billing/invoicing
4. Payment provider integratie

---

## ✅ QUICK WINS

1. **Fix session stop bug** (Line 119) - 1 uur werk, grote impact
2. **Add basic input validation** - 1 dag werk, security win
3. **Implement connection pooling** - 2 uur werk, performance boost
4. **Add health check endpoint** - 30 min werk, monitoring
5. **Fix datetime serialization** - 1 uur werk, voorkomt crashes

---

## 📝 CONCLUSIE

De MobyPark API is een **legacy monoliet** met **kritieke security en performance issues**. De codebase is **8+ jaar oud** en mist moderne practices. Onmiddellijke actie is vereist voor security fixes, gevolgd door een gefaseerde modernisatie naar een schaalbare, veilige architectuur.

**Geschatte effort complete modernisatie**: 12-16 weken met 2-3 developers

**Risico niveau**: 🔴 **KRITIEK** - Productie gebruik wordt **sterk afgeraden** zonder security fixes

---

*Analyse uitgevoerd door: AI Software Architect*  
*Datum: 04-09-2025*  
*Versie: 1.0*
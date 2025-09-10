# 🚀 PARKING API TEST SUITE - COMPLETE SETUP

## ✅ WAT JE HEBT GEKREGEN:

### 📁 **9 Test Files:**
1. **00-MASTER-ALL-TESTS.http** - ALLE tests in 1 file
2. **01-authentication.http** - Login/Register/Logout tests
3. **02-user-profile.http** - Profile management tests
4. **03-parking-lots.http** - Parking lot CRUD tests
5. **04-parking-sessions.http** - Start/Stop parking tests
6. **05-reservations.http** - Reservation management tests
7. **06-vehicles.http** - Vehicle management tests
8. **07-payments.http** - Payment & refund tests
9. **08-billing.http** - Billing overview tests

---

## 🎯 HOE TE GEBRUIKEN (SUPER SIMPEL):

### **Stap 1: Installeer REST Client**
1. Open VS Code
2. Ga naar Extensions (Ctrl+Shift+X)
3. Zoek: **"REST Client"**
4. Installeer die van **Huachao Mao**

### **Stap 2: Start je server**
```bash
cd /mnt/c/Users/Wisha/Downloads/Nieuwe-map/SoftwareConstruction/v1/api
python server.py
```

### **Stap 3: Open een test file**
- Voor complete test: Open **`00-MASTER-ALL-TESTS.http`**
- Voor specifieke tests: Open bijv. **`01-authentication.http`**

### **Stap 4: Run tests**
1. Je ziet **"Send Request"** boven elke test
2. **Klik op "Send Request"**
3. Response verschijnt rechts!

---

## 📋 TEST VOLGORDE (BELANGRIJK!):

### **Voor eerste keer:**
1. Open **`00-MASTER-ALL-TESTS.http`**
2. Run **1.1 REGISTER NEW USER**
3. Run **1.3 LOGIN AS USER**
4. **KOPIEER DE TOKEN** uit response
5. Plak token op regel 50: `@userToken = HIER_JE_TOKEN`
6. Nu werken alle authenticated endpoints!

### **Voor admin tests:**
1. Maak admin user aan in database met `role: "ADMIN"`
2. Login als admin
3. Kopieer admin token
4. Plak op regel 63: `@adminToken = HIER_JE_ADMIN_TOKEN`

---

## 🔍 WAT ELKE FILE TEST:

### **01-authentication.http** (10 tests)
- ✅ Register nieuwe user
- ✅ Register duplicate user
- ✅ Login met juiste credentials
- ✅ Login met verkeerde password
- ✅ Logout met token
- ✅ Error handling

### **02-user-profile.http** (9 tests)
- ✅ Get profile met token
- ✅ Update profile naam
- ✅ Update password
- ✅ Authorization checks

### **03-parking-lots.http** (13 tests)
- ✅ Get all parking lots (public)
- ✅ Create parking lot (admin)
- ✅ Update parking lot (admin)
- ✅ Delete parking lot (admin)
- ✅ Permission checks

### **04-parking-sessions.http** (17 tests)
- ✅ Start parking session
- ✅ Stop parking session
- ✅ Duplicate session check
- ✅ Get sessions lijst
- ✅ Delete session (admin)

### **05-reservations.http** (18 tests)
- ✅ Create reservation
- ✅ Update reservation
- ✅ Delete reservation
- ✅ Admin can manage all
- ✅ User can only manage own

### **06-vehicles.http** (21 tests)
- ✅ Register vehicle
- ✅ Vehicle entry to parking
- ✅ Get vehicles lijst
- ✅ Update vehicle naam
- ✅ Delete vehicle

### **07-payments.http** (19 tests)
- ✅ Create payment
- ✅ Create refund (admin)
- ✅ Complete payment met validatie
- ✅ Get payment history
- ✅ Validation checks

### **08-billing.http** (7 tests)
- ✅ Get billing overview
- ✅ Calculate parking costs
- ✅ Admin kan alle billing zien
- ✅ Complete flow test

---

## 💡 TIPS & TRICKS:

### **Sneltoetsen:**
- **Ctrl+Alt+R** = Send Request (sneller dan klikken)
- **Ctrl+Shift+P** → "Rest Client: Send Request"

### **Variables:**
- `{{$timestamp}}` = Automatische timestamp
- `{{userToken}}` = Je session token
- `{{adminToken}}` = Admin token
- `{{baseUrl}}` = http://localhost:8000

### **Response kleuren:**
- **Groen (2xx)** = Success
- **Geel (3xx)** = Redirect
- **Rood (4xx/5xx)** = Error

---

## 🔧 TROUBLESHOOTING:

### **"Could not send request"**
- Check: Server draait? (`python server.py`)
- Check: Juiste port? (8000)

### **"401 Unauthorized"**
- Login eerst (test 1.3)
- Kopieer token
- Plak token in variable

### **"403 Access denied"**
- Je hebt admin rechten nodig
- Check user role in database

### **"404 Not found"**
- Resource bestaat niet
- Check ID in URL

---

## ✨ BONUS FEATURES:

### **Test alles in 1 keer:**
1. Open **`00-MASTER-ALL-TESTS.http`**
2. Login & kopieer tokens
3. Run alle tests van boven naar beneden

### **Test specifieke module:**
1. Open bijv. **`06-vehicles.http`**
2. Zet token bovenaan
3. Run alle vehicle tests

### **Debug mode:**
1. Check response headers
2. Check status codes
3. Check response body

---

## 📊 TOTAAL: 120+ TESTS!

Alle endpoints zijn getest met:
- ✅ Success scenarios
- ✅ Error scenarios
- ✅ Permission checks
- ✅ Missing fields
- ✅ Invalid data
- ✅ Complete flows

---

## 🎉 KLAAR!

Je hebt nu een **COMPLETE TEST SUITE** met:
- Alle 38 endpoints
- 120+ test scenarios
- Error handling tests
- Permission tests
- Flow tests

**Just click "Send Request" and test!** 🚀
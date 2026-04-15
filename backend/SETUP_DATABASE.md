# 🗄️ Database Setup Guide

## Issue: 500 Internal Server Error on Signup

The 500 error means the database tables haven't been created yet.

---

## 🔧 Quick Fix

### Step 1: Ensure MySQL is Running

Check if MySQL is running:
```bash
# Windows
net start MySQL80

# Or check services
services.msc
```

### Step 2: Create Database

Open MySQL command line:
```bash
mysql -u root -p
```

Create the database:
```sql
CREATE DATABASE annotation_db;
SHOW DATABASES;
EXIT;
```

### Step 3: Initialize Database Tables

Run the initialization script:
```bash
cd backend
python init_db.py
```

**Expected Output**:
```
Creating database tables...
✅ Database tables created successfully!

Tables created:
  - users
  - files
  - videos
  - frames
  - annotations

Verified tables in database: ['users', 'files', 'videos', 'frames', 'annotations']
```

### Step 4: Restart Flask Server

```bash
python run.py
```

### Step 5: Test Signup Again

Try signing up from your frontend. It should now work!

---

## 🔍 Troubleshooting

### Error: "Can't connect to MySQL server"

**Solution**: 
1. Check if MySQL is running
2. Verify credentials in `backend/app/config.py`:
   ```python
   SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root123@localhost/annotation_db'
   ```
3. Update username/password if different

### Error: "Unknown database 'annotation_db'"

**Solution**: Create the database first:
```sql
mysql -u root -p
CREATE DATABASE annotation_db;
```

### Error: "Access denied for user 'root'@'localhost'"

**Solution**: Update password in `config.py` or reset MySQL root password

### Error: "No module named 'pymysql'"

**Solution**: Install pymysql:
```bash
pip install pymysql
```

---

## 📝 Verify Database Setup

### Check Tables Exist

```bash
mysql -u root -p annotation_db
```

```sql
SHOW TABLES;
```

**Expected Output**:
```
+-------------------------+
| Tables_in_annotation_db |
+-------------------------+
| annotations             |
| files                   |
| frames                  |
| users                   |
| videos                  |
+-------------------------+
```

### Check User Table Structure

```sql
DESCRIBE users;
```

**Expected Output**:
```
+---------------+--------------+------+-----+---------+----------------+
| Field         | Type         | Null | Key | Default | Extra          |
+---------------+--------------+------+-----+---------+----------------+
| id            | int          | NO   | PRI | NULL    | auto_increment |
| email         | varchar(120) | NO   | UNI | NULL    |                |
| password_hash | varchar(255) | NO   |     | NULL    |                |
| created_at    | datetime     | NO   |     | NULL    |                |
+---------------+--------------+------+-----+---------+----------------+
```

---

## 🚀 Alternative: Use SQLite for Testing

If you want to quickly test without MySQL, update `config.py`:

```python
# In backend/app/config.py
class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///annotation.db'  # Use SQLite instead
```

Then run:
```bash
python init_db.py
python run.py
```

---

## ✅ Verification Checklist

- [ ] MySQL server is running
- [ ] Database `annotation_db` exists
- [ ] Database credentials in `config.py` are correct
- [ ] `pymysql` is installed (`pip install pymysql`)
- [ ] `init_db.py` ran successfully
- [ ] All 5 tables created (users, files, videos, frames, annotations)
- [ ] Flask server restarted
- [ ] Signup works without 500 error

---

## 🎯 After Setup

Once database is initialized, you should be able to:

1. ✅ Sign up new users
2. ✅ Login with credentials
3. ✅ Upload files
4. ✅ Process videos
5. ✅ Create annotations
6. ✅ Export data

---

## 📞 Still Having Issues?

1. **Check Flask console** for detailed error messages
2. **Run with error logging**:
   ```bash
   python run.py
   ```
   Look for the traceback in the console

3. **Test database connection**:
   ```python
   from app import create_app
   from app.extensions import db
   
   app = create_app()
   with app.app_context():
       print(db.engine.url)
       db.engine.connect()
       print("✅ Database connection successful!")
   ```

---

**After running `init_db.py`, your signup should work! 🎉**

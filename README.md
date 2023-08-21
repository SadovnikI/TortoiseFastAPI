# Project setup
1. Download and install [Docker](https://www.docker.com/products/docker-desktop/)
2. Open **Terminal** in project directory
3. Run command ```docker-compose up```
4. Done!

---

Alternatively you can start project from ```main.py``` file, but before that you need change database url(```db_url```)  in ```api.main_api.py``` inside ```register_tortoise()``` function to any empy DB

---

By default FastApi app avalible on ```http://localhost:8008/``` and PostgreSQL on ```postgres://root:postgres@localhost:5432/postgres```

---

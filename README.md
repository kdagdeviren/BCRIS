# BCRIS — Breast Cancer Response Intelligence System

**A configuration-based, multi-platform clinical decision support system for predicting neoadjuvant chemotherapy response in breast cancer.**

> Live system: [bcris.site](https://bcris.site) &nbsp;|&nbsp; Licence: MIT &nbsp;|&nbsp; DOI: *(pending)*

---

## Overview

BCRIS is an open-access web and offline desktop application that supports clinicians in predicting Residual Cancer Burden (RCB) category after neoadjuvant chemotherapy in breast cancer. It was developed as part of a doctoral research programme at Ege University and is described in a manuscript submitted to *BMJ Health & Care Informatics*.

The system implements a four-layer architecture in which **clinical logic is entirely separated from source code**: all variables, category options, treatment messages, and the active prediction model are managed through a database-driven admin interface without requiring a server restart or code change.

---

## Key Features

- **RCB category prediction** — four-class output (RCB-0/pCR, RCB-1, RCB-2, RCB-3) with probability distribution
- **Configuration-based architecture** — all clinical content managed via the admin panel, zero hard-coding
- **Swappable model layer** — new prediction model activated via database record, no restart required
- **Embedded explainability** — per-variable contextual guide (definition, measurement method, clinical relevance, source)
- **Priority-coded treatment and recommendation layer** — colour-coded cards (critical/warning/informational) per entered variable profile
- **Bulk Excel import** — upload a multi-patient spreadsheet for batch prediction
- **PDF report export** — downloadable A4 patient report
- **Bilingual interface** — Turkish and English (TR/EN toggle)
- **Physician portal** — registration, verification, data contribution, and contributor recognition page
- **Learning health system loop** — controlled five-stage cycle: access → verification → contribution → re-training → recognition

---

## Quick Start

### Requirements

- Python 3.8+
- Django 5.2+
- PostgreSQL or SQLite

### Installation

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic
python manage.py runserver
```

### First Use

1. Create an admin user:
```bash
   python manage.py createsuperuser
```
2. Home page: http://localhost:8000/
3. Admin panel: http://localhost:8000/admin/

---

## Project Structure

BCRIS/
├── bcris_project/ # Django project settings
├── rcb_predictor/ # Core application
│ ├── models.py # Database models
│ ├── views.py # View functions
│ ├── admin.py # Admin panel configuration
│ └── migrations/ # Database migrations
├── templates/ # HTML templates
├── static/ # Static files (CSS, JS, images)
│ ├── languages.json # Homepage translations
│ └── physician_translations.json # Physician-portal translations
├── models/ # ML model files
├── docs/ # Documentation
├── tests/ # Test files
└── manage.py

---

## Configuration

### Database
Configure database settings in `bcris_project/settings.py`.

### ML Model
Admin Panel → ML Models → Upload Model

### Variables and Content
Admin Panel → Variables → Add / Edit

### Language Files
- Homepage: `static/languages.json`
- Physician portal: `static/physician_translations.json`

---

## Deployment

### Coolify (Recommended)
Deploy with Dockerfile + SQLite in under 3 minutes:
- See [COOLIFY_SIMPLE.md](docs/COOLIFY_SIMPLE.md)
- Only 2 environment variables required
- No separate database setup (SQLite auto-created)

### Docker (Manual)
```bash
docker build -t bcris .
docker run -d \
  -p 8000:8000 \
  -e DJANGO_SECRET_KEY=your-key \
  -e DJANGO_ALLOWED_HOSTS=yourdomain.com \
  -v bcris-data:/app/data \
  -v bcris-media:/app/media \
  -v bcris-models:/app/models \
  -v bcris-static:/app/staticfiles \
  -v bcris-logs:/app/logs \
  --name bcris \
  bcris
```

### Environment Variables
See [.env.example](.env.example)

---

## Documentation

- General overview: [docs/README.md](docs/README.md)
- Django notes: [docs/README_DJANGO.md](docs/README_DJANGO.md)
- Database-driven architecture: [docs/DATABASE_DRIVEN_SYSTEM.md](docs/DATABASE_DRIVEN_SYSTEM.md)
- Deployment guide: [docs/COOLIFY_DEPLOYMENT.md](docs/COOLIFY_DEPLOYMENT.md)

---

## Tests

```bash
cd tests/
python test_hekim_sistemi.py
```

---

## Citing This Work

If you use BCRIS in your research, please cite the associated manuscript:

> Dağdeviren YK, Kantar O, Bekiş R. *BCRIS: Development and evaluation of a configuration-based, multi-platform clinical decision support system for predicting neoadjuvant chemotherapy response in breast cancer.* BMJ Health & Care Informatics *(submitted)*.

---

## Licence

This project is released under the [MIT Licence](LICENSE).

---

## Contact

- **Author**: Yusuf Kağan Dağdeviren
- **Corresponding email**: kagan.dagdeviren@deu.edu.tr
- **Institution**: Dokuz Eylül University Hospital, İzmir, Türkiye
- **ORCID**: [0000-0003-3814-9401](https://orcid.org/0000-0003-3814-9401)

---

> **Note**: BCRIS is an operational prototype. The prediction model was trained on a single-centre retrospective cohort (n = 328). Prospective multi-centre validation is required before clinical deployment.

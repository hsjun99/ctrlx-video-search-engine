# CtrlX

### _Empower creators to craft captivating shorts with ease_

---

## Video Search Engine

_python 3.10 is required_

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host=0.0.0.0 --port=8081
celery -A app.worker.celery_app worker --loglevel=info -c 1
```

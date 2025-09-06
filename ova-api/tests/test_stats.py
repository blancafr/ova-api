from sqlalchemy import text


def _normalize_counts(p):
        if isinstance(p, dict):
            return {str(k).lower(): int(v) for k, v in p.items()}
        if isinstance(p, list):
            if not p:
                return {}
            if isinstance(p[0], (list, tuple)) and len(p[0]) == 2:
                return {str(k).lower(): int(v) for k, v in p}
        raise AssertionError(f"Unexpected disease_counts payload format: {p!r}")

def test_total_patients(client_with_registry_db, registry_session, seed_registries, tokens):
    t = tokens.superuser
    client = client_with_registry_db

    r = client.get(
        "/stats/total-patients",
        params={},
        headers={"Authorization": f"Bearer {t}"},
    )
    assert r.status_code == 200, r.text
    api_total = r.json()["total_patients"]

    expected_total = registry_session.execute(
        text("""
            SELECT COUNT(*) FROM registry
        """),
    ).scalar_one()

    assert api_total == expected_total == 10


def test_total_patients_may(client_with_registry_db, registry_session, seed_registries, tokens):
    t = tokens.superuser
    client = client_with_registry_db

    r = client.get(
        "/stats/total-patients",
        params={"start_date": "2025-05-01", "end_date": "2025-05-31"},
        headers={"Authorization": f"Bearer {t}"},
    )
    assert r.status_code == 200, r.text
    api_total = r.json()["total_patients"]

    expected_total = registry_session.execute(
        text("""
            SELECT COUNT(*) FROM registry
            WHERE date BETWEEN :s AND :e
        """),
        {"s": "2025-05-01", "e": "2025-05-31"},
    ).scalar_one()

    assert api_total == expected_total == 6

def test_total_patients_may_gender(client_with_registry_db, registry_session, seed_registries, tokens):
    t = tokens.superuser
    client = client_with_registry_db

    r = client.get(
        "/stats/total-patients",
        params={"start_date": "2025-05-01", "end_date": "2025-05-31", "sex": "Hombre"},
        headers={"Authorization": f"Bearer {t}"},
    )
    assert r.status_code == 200, r.text
    api_total = r.json()["total_patients"]

    expected_total = registry_session.execute(
        text("""
            SELECT COUNT(*) FROM registry
            WHERE date BETWEEN :s AND :e
            AND sex = 'Hombre'
        """),
        {"s": "2025-05-01", "e": "2025-05-31"},
    ).scalar_one()

    assert api_total == expected_total == 3

def test_disease_counts_may(client_with_registry_db, registry_session, seed_registries, tokens):
    t = tokens.superuser
    client = client_with_registry_db

    r = client.get(
        "/stats/disease-counts",
        params={"start_date": "2025-05-01", "end_date": "2025-05-31"},
        headers={"Authorization": f"Bearer {t}"},
    )
    assert r.status_code == 200, r.text
    payload = r.json()["disease_counts"]


    api_map = _normalize_counts(payload)

    def expected_count(dname: str) -> int:
        return registry_session.execute(
            text("""
                SELECT COUNT(*) FROM registry
                WHERE date BETWEEN :s AND :e
                  AND instr(diseases, :dname) > 0
            """),
            {"s": "2025-05-01", "e": "2025-05-31", "dname": dname},
        ).scalar_one()

    assert api_map.get("malaria", 0)  == expected_count("malaria")  == 4
    assert api_map.get("hipertension", 0)      == expected_count("hipertension")      == 2
    assert api_map.get("diabetes", 0) == expected_count("diabetes") == 1

def test_avg_disease(client_with_registry_db, registry_session, seed_registries, tokens):
    t = tokens.superuser
    client = client_with_registry_db

    r = client.get(
        "/stats/avg-diseases-per-patient",
        params={},
        headers={"Authorization": f"Bearer {t}"},
    )
    assert r.status_code == 200, r.text
    payload = r.json()["avg_diseases_per_patient"]

    assert payload == 1.2

def test_disease_total_malaria_f_50plus_may(client_with_registry_db, registry_session, seed_registries, tokens):
    t = tokens.superuser
    client = client_with_registry_db

    r = client.get(
        "/stats/disease/total",
        params={
            "disease": "malaria",
            "start_date": "2025-05-01",
            "end_date": "2025-05-31",
            "sex": "Mujer",
            "age": ">50años",
        },
        headers={"Authorization": f"Bearer {t}"},
    )
    assert r.status_code == 200, r.text
    api_total = r.json()["total"]

    expected_total = registry_session.execute(
        text("""
            SELECT COUNT(*) FROM registry
            WHERE date BETWEEN :s AND :e
              AND sex = 'Mujer'
              AND age = '>50años'
              AND instr(diseases, 'malaria') > 0
        """),
        {"s": "2025-05-01", "e": "2025-05-31"},
    ).scalar_one()

    assert api_total == expected_total == 1

def test_disease_gender_hipertension(client_with_registry_db, registry_session, seed_registries, tokens):
    t = tokens.superuser
    client = client_with_registry_db

    r = client.get(
        "/stats/disease/gender",
        params={
            "disease": "hipertension",
        },
        headers={"Authorization": f"Bearer {t}"},
    )
    assert r.status_code == 200, r.text
    api_total = r.json()["gender_distribution"]
    api_total = _normalize_counts(api_total)

    rows = registry_session.execute(
        text("""
            SELECT sex as d, COUNT(*) as c
            FROM registry
              WHERE instr(diseases, 'hipertension') > 0
            GROUP BY sex
        """),
    ).all()
    expected = {str(d).lower(): int(c) for d, c in rows}

    assert api_total == expected


def test_disease_proportion_diabetes_sex(client_with_registry_db, registry_session, seed_registries, tokens):
    t = tokens.superuser
    client = client_with_registry_db

    r = client.get(
        "/stats/disease/proportion",
        params={
            "disease": "diabetes",
            "sex": "Mujer"
        },
        headers={"Authorization": f"Bearer {t}"},
    )
    assert r.status_code == 200, r.text
    api_total = r.json()["proportion"]

    total = registry_session.execute(
        text("""
            SELECT COUNT(*) FROM registry
            WHERE sex="Mujer"
        """),
    ).scalar_one()

    malaria_total = registry_session.execute(
        text("""
            SELECT COUNT(*) FROM registry
            WHERE instr(diseases, 'diabetes') > 0
             AND sex="Mujer"
        """)
    ).scalar_one()

    expected_prop = (malaria_total / total) if total else 0.0

    assert api_total == expected_prop


def test_disease_age(client_with_registry_db, registry_session, seed_registries, tokens):
    t = tokens.superuser
    client = client_with_registry_db

    r = client.get(
        "/stats/disease/age",
        params={"disease":"malaria"},
        headers={"Authorization": f"Bearer {t}"},
    )
    assert r.status_code == 200, r.text
    payload = r.json()["age_distribution"]

    api_map = _normalize_counts(payload)

    rows = registry_session.execute(
        text("""
            SELECT age as d, COUNT(*) as c
            FROM registry
              WHERE instr(diseases, 'malaria') > 0
            GROUP BY age
        """),
    ).all()
    expected = {str(d).lower(): int(c) for d, c in rows}

    assert api_map == expected

def test_disease_per_day_may(client_with_registry_db, registry_session, seed_registries, tokens):
    t = tokens.superuser
    client = client_with_registry_db

    r = client.get(
        "/stats/disease/per-day",
        params={"disease":"malaria","start_date": "2025-05-01", "end_date": "2025-05-31"},
        headers={"Authorization": f"Bearer {t}"},
    )
    assert r.status_code == 200, r.text
    payload = r.json()["patients_per_day"]

    api_map = _normalize_counts(payload)

    rows = registry_session.execute(
        text("""
            SELECT date(date) as d, COUNT(*) as c
            FROM registry
            WHERE date BETWEEN :s AND :e
              AND instr(diseases, 'malaria') > 0
            GROUP BY date(date)
        """),
        {"s": "2025-05-01", "e": "2025-05-31"},
    ).all()
    expected = {str(d): int(c) for d, c in rows}

    assert api_map == expected
def test_stats_requires_auth(client):
    r = client.get("/stats/total-patients")
    assert r.status_code in (401, 403)  # without token

def test_stats_rejects_non_superuser(client, tokens):
    t = tokens.regular
    r = client.get("/stats/total-patients", headers={"Authorization": f"Bearer {t}"})
    assert r.status_code == 403  # no superuser

def test_stats_allows_superuser(client, tokens):
    t = tokens.superuser
    r = client.get("/stats/total-patients", headers={"Authorization": f"Bearer {t}"})
    assert r.status_code == 200
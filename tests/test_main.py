from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_root_returns_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_static_css_served():
    response = client.get("/static/css/style.css")
    assert response.status_code == 200

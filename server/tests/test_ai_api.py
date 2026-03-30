"""Unit tests for AI diagnosis API (Task 6.1).

Validates Requirements:
- 4.1: Structured health form (age, gender, symptoms, allergy_history, current_medication)
- 4.2: Combine user input with Prompt_Template and send to AI_Service
- 4.3: Append disclaimer to results
- 4.6: Log every AI diagnosis input/output
- 4.8: History records in time-descending order, paginated
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.schemas.ai import DiagnosisHistoryItem, DiagnosisRequest, DiagnosisResponse


# ---------------------------------------------------------------------------
# Schema tests
# ---------------------------------------------------------------------------


class TestDiagnosisRequest:
    """Validates: Requirement 4.1"""

    def test_valid_full_request(self):
        req = DiagnosisRequest(
            age=30, gender="男", symptoms="头痛", allergy_history="青霉素", current_medication="无"
        )
        assert req.age == 30
        assert req.gender == "男"
        assert req.symptoms == "头痛"
        assert req.allergy_history == "青霉素"
        assert req.current_medication == "无"

    def test_optional_fields_default_empty(self):
        req = DiagnosisRequest(age=25, gender="女", symptoms="失眠")
        assert req.allergy_history == ""
        assert req.current_medication == ""

    def test_invalid_age_negative(self):
        with pytest.raises(Exception):
            DiagnosisRequest(age=-1, gender="男", symptoms="头痛")

    def test_missing_symptoms_raises(self):
        with pytest.raises(Exception):
            DiagnosisRequest(age=30, gender="男", symptoms="")


class TestDiagnosisResponse:
    """Validates: Requirement 4.3"""

    def test_valid_response(self):
        now = datetime.now(timezone.utc)
        resp = DiagnosisResponse(id=uuid.uuid4(), result="建议调理", created_at=now)
        assert resp.result == "建议调理"

    def test_from_attributes(self):
        obj = MagicMock()
        obj.id = uuid.uuid4()
        obj.result = "AI 建议"
        obj.created_at = datetime.now(timezone.utc)
        resp = DiagnosisResponse.model_validate(obj)
        assert resp.result == "AI 建议"


class TestDiagnosisHistoryItem:
    """Validates: Requirement 4.8"""

    def test_valid_history_item(self):
        item = DiagnosisHistoryItem(
            id=uuid.uuid4(),
            input_data={"age": 30, "gender": "男"},
            ai_output="建议内容",
            created_at=datetime.now(timezone.utc),
        )
        assert item.ai_output == "建议内容"

    def test_from_attributes(self):
        obj = MagicMock()
        obj.id = uuid.uuid4()
        obj.input_data = {"age": 25}
        obj.ai_output = "结果"
        obj.created_at = datetime.now(timezone.utc)
        item = DiagnosisHistoryItem.model_validate(obj)
        assert item.input_data == {"age": 25}


# ---------------------------------------------------------------------------
# Endpoint tests
# ---------------------------------------------------------------------------


def _mock_user():
    user = MagicMock()
    user.id = uuid.uuid4()
    user.status = "active"
    return user


def _mock_log_entry(user_id, ai_output="AI 建议结果"):
    log = MagicMock()
    log.id = uuid.uuid4()
    log.user_id = user_id
    log.input_data = {"age": 30, "gender": "男", "symptoms": "头痛"}
    log.ai_output = ai_output
    log.created_at = datetime.now(timezone.utc)
    return log


class TestCreateDiagnosisEndpoint:

    def test_diagnosis_success_with_overrides(self):
        from fastapi.testclient import TestClient
        from app.main import app
        from app.database import get_db
        from app.middleware.auth import get_current_user

        user = _mock_user()
        log_entry = _mock_log_entry(user.id, "调理方向建议\n\n免责声明")

        mock_db = AsyncMock()
        mock_db_result = MagicMock()
        mock_db_result.scalar_one.return_value = log_entry
        mock_db.execute.return_value = mock_db_result

        with patch("app.routers.ai.diagnose", new_callable=AsyncMock) as mock_diagnose:
            mock_diagnose.return_value = "调理方向建议\n\n免责声明"

            app.dependency_overrides[get_db] = lambda: mock_db
            app.dependency_overrides[get_current_user] = lambda: user
            try:
                client = TestClient(app)
                response = client.post(
                    "/api/v1/ai/diagnosis",
                    json={
                        "age": 30,
                        "gender": "男",
                        "symptoms": "头痛",
                        "allergy_history": "无",
                        "current_medication": "无",
                    },
                )
            finally:
                app.dependency_overrides.clear()

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["result"] == "调理方向建议\n\n免责声明"
        assert "id" in body["data"]
        assert "created_at" in body["data"]

    def test_diagnosis_ai_failure_returns_500(self):
        from fastapi.testclient import TestClient
        from app.main import app
        from app.database import get_db
        from app.middleware.auth import get_current_user

        user = _mock_user()
        mock_db = AsyncMock()

        with patch("app.routers.ai.diagnose", new_callable=AsyncMock) as mock_diagnose:
            mock_diagnose.side_effect = ValueError("AI 服务暂时不可用，请稍后再试")

            app.dependency_overrides[get_db] = lambda: mock_db
            app.dependency_overrides[get_current_user] = lambda: user
            try:
                client = TestClient(app)
                response = client.post(
                    "/api/v1/ai/diagnosis",
                    json={"age": 30, "gender": "男", "symptoms": "头痛"},
                )
            finally:
                app.dependency_overrides.clear()

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 500
        assert "AI 服务暂时不可用" in body["message"]

    def test_diagnosis_missing_required_field_returns_422(self):
        from fastapi.testclient import TestClient
        from app.main import app
        from app.middleware.auth import get_current_user

        user = _mock_user()
        app.dependency_overrides[get_current_user] = lambda: user
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/ai/diagnosis",
                json={"age": 30, "gender": "男"},  # missing symptoms
            )
        finally:
            app.dependency_overrides.clear()
        assert response.status_code == 422


class TestDiagnosisHistoryEndpoint:
    """Validates: Requirement 4.8"""

    def test_history_returns_paginated_results(self):
        from fastapi.testclient import TestClient
        from app.main import app
        from app.database import get_db
        from app.middleware.auth import get_current_user

        user = _mock_user()
        log1 = _mock_log_entry(user.id, "结果1")
        log2 = _mock_log_entry(user.id, "结果2")

        mock_db = AsyncMock()
        # First call: count query
        count_result = MagicMock()
        count_result.scalar_one.return_value = 2
        # Second call: items query
        items_result = MagicMock()
        items_result.scalars.return_value.all.return_value = [log1, log2]

        mock_db.execute.side_effect = [count_result, items_result]

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_current_user] = lambda: user
        try:
            client = TestClient(app)
            response = client.get("/api/v1/ai/diagnosis/history?page=1&page_size=10")
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["total"] == 2
        assert len(body["data"]["items"]) == 2
        assert body["data"]["page"] == 1

    def test_history_empty(self):
        from fastapi.testclient import TestClient
        from app.main import app
        from app.database import get_db
        from app.middleware.auth import get_current_user

        user = _mock_user()
        mock_db = AsyncMock()

        count_result = MagicMock()
        count_result.scalar_one.return_value = 0
        items_result = MagicMock()
        items_result.scalars.return_value.all.return_value = []

        mock_db.execute.side_effect = [count_result, items_result]

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_current_user] = lambda: user
        try:
            client = TestClient(app)
            response = client.get("/api/v1/ai/diagnosis/history")
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["total"] == 0
        assert body["data"]["items"] == []

    def test_history_page_size_exceeds_max_returns_422(self):
        from fastapi.testclient import TestClient
        from app.main import app
        from app.middleware.auth import get_current_user

        user = _mock_user()
        app.dependency_overrides[get_current_user] = lambda: user
        try:
            client = TestClient(app)
            response = client.get("/api/v1/ai/diagnosis/history?page_size=21")
        finally:
            app.dependency_overrides.clear()
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# Pairing suggestion schema tests (Task 6.2)
# ---------------------------------------------------------------------------

from app.schemas.ai import PairingRequest, PairingResponse


class TestPairingRequest:
    """Validates: Requirement 5.1"""

    def test_valid_request(self):
        req = PairingRequest(herb_ids=[uuid.uuid4(), uuid.uuid4()])
        assert len(req.herb_ids) == 2

    def test_single_herb(self):
        req = PairingRequest(herb_ids=[uuid.uuid4()])
        assert len(req.herb_ids) == 1

    def test_empty_herb_ids_raises(self):
        with pytest.raises(Exception):
            PairingRequest(herb_ids=[])


class TestPairingResponse:
    """Validates: Requirements 5.2, 5.3, 5.4"""

    def test_valid_response(self):
        resp = PairingResponse(result="搭配建议内容")
        assert resp.result == "搭配建议内容"


# ---------------------------------------------------------------------------
# Pairing endpoint tests (Task 6.2)
# ---------------------------------------------------------------------------


def _mock_herb(herb_id=None, name="当归"):
    herb = MagicMock()
    herb.id = herb_id or uuid.uuid4()
    herb.name = name
    return herb


class TestCreatePairingSuggestionEndpoint:
    """Validates: Requirements 5.1, 5.2, 5.3, 5.4"""

    def test_pairing_success(self):
        from fastapi.testclient import TestClient
        from app.main import app
        from app.database import get_db
        from app.middleware.auth import get_current_user

        user = _mock_user()
        herb1_id = uuid.uuid4()
        herb2_id = uuid.uuid4()
        herb1 = _mock_herb(herb1_id, "当归")
        herb2 = _mock_herb(herb2_id, "黄芪")

        mock_db = AsyncMock()
        # herbs query
        herbs_result = MagicMock()
        herbs_result.scalars.return_value.all.return_value = [herb1, herb2]
        mock_db.execute.return_value = herbs_result

        suggestion_text = "当归与黄芪搭配建议\n\n不适合人群：孕妇\n注意事项：请遵医嘱\n\n免责声明"

        with patch(
            "app.routers.ai.get_pairing_suggestion", new_callable=AsyncMock
        ) as mock_pairing:
            mock_pairing.return_value = suggestion_text

            app.dependency_overrides[get_db] = lambda: mock_db
            app.dependency_overrides[get_current_user] = lambda: user
            try:
                client = TestClient(app)
                response = client.post(
                    "/api/v1/ai/pairing",
                    json={"herb_ids": [str(herb1_id), str(herb2_id)]},
                )
            finally:
                app.dependency_overrides.clear()

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["result"] == suggestion_text

    def test_pairing_herb_not_found(self):
        from fastapi.testclient import TestClient
        from app.main import app
        from app.database import get_db
        from app.middleware.auth import get_current_user

        user = _mock_user()
        herb1_id = uuid.uuid4()
        missing_id = uuid.uuid4()
        herb1 = _mock_herb(herb1_id, "当归")

        mock_db = AsyncMock()
        herbs_result = MagicMock()
        herbs_result.scalars.return_value.all.return_value = [herb1]
        mock_db.execute.return_value = herbs_result

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_current_user] = lambda: user
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/ai/pairing",
                json={"herb_ids": [str(herb1_id), str(missing_id)]},
            )
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 400
        assert str(missing_id) in body["message"]

    def test_pairing_ai_failure_returns_500(self):
        from fastapi.testclient import TestClient
        from app.main import app
        from app.database import get_db
        from app.middleware.auth import get_current_user

        user = _mock_user()
        herb1_id = uuid.uuid4()
        herb1 = _mock_herb(herb1_id, "当归")

        mock_db = AsyncMock()
        herbs_result = MagicMock()
        herbs_result.scalars.return_value.all.return_value = [herb1]
        mock_db.execute.return_value = herbs_result

        with patch(
            "app.routers.ai.get_pairing_suggestion", new_callable=AsyncMock
        ) as mock_pairing:
            mock_pairing.side_effect = ValueError("AI 服务暂时不可用，请稍后再试")

            app.dependency_overrides[get_db] = lambda: mock_db
            app.dependency_overrides[get_current_user] = lambda: user
            try:
                client = TestClient(app)
                response = client.post(
                    "/api/v1/ai/pairing",
                    json={"herb_ids": [str(herb1_id)]},
                )
            finally:
                app.dependency_overrides.clear()

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 500
        assert "AI 服务暂时不可用" in body["message"]

    def test_pairing_empty_herb_ids_returns_422(self):
        from fastapi.testclient import TestClient
        from app.main import app
        from app.middleware.auth import get_current_user

        user = _mock_user()
        app.dependency_overrides[get_current_user] = lambda: user
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/ai/pairing",
                json={"herb_ids": []},
            )
        finally:
            app.dependency_overrides.clear()
        assert response.status_code == 422

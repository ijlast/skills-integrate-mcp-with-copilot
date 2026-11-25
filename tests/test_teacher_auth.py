import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException
from fastapi.security import HTTPBasicCredentials

from src import app as app_module
from src.teacher_auth import hash_password


class TeacherAuthenticationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.teachers_file = Path(self.temp_dir.name) / "teachers.json"
        salt = b"0123456789abcdef"
        self.teachers_file.write_text(
            json.dumps({
                "teachers": {
                    "teacher": {
                        "salt": salt.hex(),
                        "password_hash": hash_password(
                            "correct horse battery", salt
                        ),
                    }
                }
            }),
            encoding="utf-8",
        )
        self.file_patch = patch.object(
            app_module, "TEACHERS_FILE", self.teachers_file
        )
        self.file_patch.start()

    def tearDown(self):
        self.file_patch.stop()
        self.temp_dir.cleanup()

    def test_valid_teacher_credentials_are_accepted(self):
        credentials = HTTPBasicCredentials(
            username="teacher",
            password="correct horse battery",
        )

        self.assertEqual(app_module.require_teacher(credentials), "teacher")

    def test_invalid_or_missing_credentials_are_rejected(self):
        for credentials in (
            HTTPBasicCredentials(username="teacher", password="wrong password"),
            HTTPBasicCredentials(username="unknown", password="wrong password"),
            None,
        ):
            with self.subTest(credentials=credentials):
                with self.assertRaises(HTTPException) as error:
                    app_module.require_teacher(credentials)
                self.assertEqual(error.exception.status_code, 401)

    def test_missing_teacher_configuration_returns_service_unavailable(self):
        with patch.object(
            app_module,
            "TEACHERS_FILE",
            Path(self.temp_dir.name) / "missing-teachers.json",
        ):
            with self.assertRaises(HTTPException) as error:
                app_module.require_teacher(
                    HTTPBasicCredentials(
                        username="teacher",
                        password="correct horse battery",
                    )
                )

        self.assertEqual(error.exception.status_code, 503)

    def test_mutation_routes_require_teacher_authentication(self):
        protected_paths = {
            "/auth/login",
            "/activities/{activity_name}/signup",
            "/activities/{activity_name}/unregister",
        }
        routes = {
            route.path: route
            for route in app_module.app.routes
            if getattr(route, "path", None) in protected_paths
        }
        self.assertEqual(set(routes), protected_paths)
        for path, route in routes.items():
            dependencies = [
                dependency.call for dependency in route.dependant.dependencies
            ]
            with self.subTest(path=path):
                self.assertIn(app_module.require_teacher, dependencies)

    def test_activity_listing_remains_public(self):
        route = next(
            route for route in app_module.app.routes
            if getattr(route, "path", None) == "/activities"
        )

        self.assertNotIn(
            app_module.require_teacher,
            [dependency.call for dependency in route.dependant.dependencies],
        )


if __name__ == "__main__":
    unittest.main()

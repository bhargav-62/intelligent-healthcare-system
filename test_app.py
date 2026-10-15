
import unittest
import app as medicare_app


class MediCareAPITests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        medicare_app.app.config["TESTING"] = True
        cls.client = medicare_app.app.test_client()

    def test_homepage_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"MediCare AI", response.data)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertIn(response.status_code, [200, 503])

        data = response.get_json()
        self.assertIn("model_loaded", data)
        self.assertIn("feature_count", data)

    def test_models_endpoint(self):
        response = self.client.get("/models")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIn("available_models", data)

    def test_prediction_rejects_empty_symptoms(self):
        response = self.client.post(
            "/predict",
            json={"symptoms": []}
        )
        self.assertEqual(response.status_code, 400)

    def test_prediction_rejects_unknown_symptom(self):
        response = self.client.post(
            "/predict",
            json={"symptoms": ["unknown_fake_symptom"]}
        )
        self.assertEqual(response.status_code, 400)

    def test_prediction_rejects_invalid_format(self):
        response = self.client.post(
            "/predict",
            json={"symptoms": "fever"}
        )
        self.assertEqual(response.status_code, 400)

    def test_prediction_accepts_known_feature(self):
        if medicare_app.model is None:
            self.skipTest("Model is not loaded")

        symptom = medicare_app.feature_names[0]

        response = self.client.post(
            "/predict",
            json={"symptoms": [symptom]}
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertIn("educational_prediction", data)
        self.assertIn("model_scores", data)
        self.assertIn("disclaimer", data)

    def test_prediction_rejects_unknown_feature_mixed_with_valid(self):
        if not medicare_app.feature_names:
            self.skipTest("Feature names are unavailable")

        symptom = medicare_app.feature_names[0]

        response = self.client.post(
            "/predict",
            json={
                "symptoms": [
                    symptom,
                    "unknown_fake_symptom"
                ]
            }
        )

        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main(verbosity=2)

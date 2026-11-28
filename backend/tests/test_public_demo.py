import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from app.main import app


class PublicDemoTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.addCleanup(self.client.close)
        # Anggap database sudah siap agar middleware seed malas tidak menyentuh Neo4j sungguhan.
        siap = patch('app.main._siap', True)
        siap.start()
        self.addCleanup(siap.stop)

    def test_first_api_request_seeds_once_when_not_ready(self):
        with patch('app.main._siap', False), patch('app.main.config.PUBLIC_DEMO', True), \
                patch('app.main.db.run', return_value=[{'n': 63}]), patch('app.main._seed_demo') as seed:
            self.client.get('/api/ready')
            self.client.get('/api/ready')
            seed.assert_called_once()

    def test_health_does_not_trigger_seed(self):
        with patch('app.main._siap', False), patch('app.main.config.PUBLIC_DEMO', True), \
                patch('app.main.siapkan_database') as siapkan, \
                patch('app.main.engine.statistik', return_value={}):
            self.client.get('/api/health')
            siapkan.assert_not_called()

    def test_public_demo_cannot_reset_database(self):
        with patch('app.main.config.PUBLIC_DEMO', True), patch('app.main.ontology.seed') as seed:
            self.assertEqual(self.client.post('/api/seed').status_code, 403)
            seed.assert_not_called()

    def test_disabled_ai_does_not_call_provider(self):
        with patch('app.main.config.LLM_ENABLED', False), patch('app.main.llm.ekstrak') as extract:
            response = self.client.post('/api/llm/ekstrak', json={'teks': 'Contoh cerita untuk demo'})
            self.assertEqual(response.status_code, 503)
            extract.assert_not_called()

    def test_readiness_checks_rule_inventory(self):
        with patch('app.main.db.run', return_value=[{'n': 63}]):
            self.assertEqual(self.client.get('/api/ready').status_code, 200)
        with patch('app.main.db.run', return_value=[{'n': 0}]):
            self.assertEqual(self.client.get('/api/ready').status_code, 503)
        with patch('app.main.db.run', side_effect=RuntimeError('private connection details')):
            response = self.client.get('/api/ready')
            self.assertEqual(response.status_code, 503)
            self.assertNotIn('private connection', response.text)

    def test_spa_routes_and_unknown_api(self):
        from app.main import FRONTEND_DIST
        if not (FRONTEND_DIST / 'index.html').exists():
            self.skipTest('Run npm --prefix frontend run build first')
        for path in ['/', '/cek', '/aturan', '/hasil/demo']:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertIn('text/html', response.headers['content-type'])
        self.assertEqual(self.client.get('/api/not-a-route').status_code, 404)
        self.assertEqual(self.client.get('/.env').status_code, 404)


class AsalTurunanTests(unittest.TestCase):
    def test_every_rule_without_source_has_origin_note(self):
        from app.rules import ASAL_TURUNAN, RULES
        tanpa_sumber = {r['id'] for r in RULES if not r['sumber']}
        self.assertEqual(tanpa_sumber, set(ASAL_TURUNAN))

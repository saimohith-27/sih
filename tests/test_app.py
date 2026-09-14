from app import create_app


def test_home_page_loads():
    app = create_app()
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    assert b'CAPACITY CONNECT' in response.data


def test_login_page_loads():
    app = create_app()
    client = app.test_client()
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Login' in response.data


def test_courses_page_loads():
    app = create_app()
    client = app.test_client()
    response = client.get('/courses/')
    assert response.status_code == 200
    assert b'Courses' in response.data


def test_login_redirects_to_role_dashboard():
    app = create_app()
    client = app.test_client()
    response = client.post(
        '/auth/login',
        data={'email': 'admin@capacityconnect.in', 'password': 'password123', 'role': 'admin'},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert response.headers['Location'] == '/admin/dashboard'


def test_login_rejects_role_mismatch_for_supabase_user(monkeypatch):
    app = create_app()

    class FakeUser:
        id = 'supabase-user-1'
        email = 'trainee@capacityconnect.in'
        user_metadata = {'full_name': 'Aarav Mehta'}

    class FakeProfileResponse:
        data = [{'role': 'trainee', 'full_name': 'Aarav Mehta', 'email': 'trainee@capacityconnect.in'}]

    class FakeTable:
        def select(self, *_args, **_kwargs):
            return self

        def eq(self, *_args, **_kwargs):
            return self

        def limit(self, *_args, **_kwargs):
            return self

        def execute(self):
            return FakeProfileResponse()

    class FakeAuth:
        def sign_in_with_password(self, _payload):
            return type('AuthResponse', (), {'user': FakeUser()})()

    class FakeSupabase:
        auth = FakeAuth()

        def table(self, _name):
            return FakeTable()

    monkeypatch.setattr('app.auth.routes.get_supabase_client', lambda use_service_role=False: FakeSupabase())

    client = app.test_client()
    response = client.post(
        '/auth/login',
        data={'email': 'trainee@capacityconnect.in', 'password': 'Password123!', 'role': 'admin'},
        follow_redirects=False,
    )

    assert response.status_code == 200
    assert b'role' in response.data.lower()
    with client.session_transaction() as session:
        assert 'user' not in session


def test_competency_matching_calculates_percentage():
    from app.competency.routes import match_trainer_for_trainee

    trainee_skills = ['Python', 'Data Analysis']
    trainers = [
        {'name': 'Dr. Ananya Raman', 'skills': ['Python', 'Data Analysis', 'Machine Learning']},
        {'name': 'Mr. Sandeep Iyer', 'skills': ['Python']},
    ]

    recommendations = match_trainer_for_trainee(trainee_skills, trainers)
    assert recommendations[0]['match'] == 100
    assert recommendations[0]['matched_skills'] == ['Python', 'Data Analysis']
    assert recommendations[1]['match'] == 50
    assert recommendations[1]['matched_skills'] == ['Python']


def test_assessment_scoring_returns_percentage_and_pass_status():
    from app.assessments.routes import score_assessment

    selected_answers = {'q1': 'b', 'q2': 'd'}
    result = score_assessment('weather-quiz', selected_answers)

    assert result['score'] == 2
    assert result['percentage'] == 100
    assert result['passed'] is True


def test_course_enrollment_sets_session_record():
    app = create_app()
    client = app.test_client()
    with client.session_transaction() as session:
        session['user'] = {'role': 'trainee', 'email': 'trainee@capacityconnect.in'}

    response = client.post('/courses/enroll/climate-data-analysis', follow_redirects=False)
    assert response.status_code == 302
    assert response.headers['Location'] == '/trainee/courses'

    with client.session_transaction() as session:
        assert 'climate-data-analysis' in session['enrolled_courses']


def test_logged_in_user_is_redirected_from_auth_pages_and_sees_logout():
    app = create_app()
    client = app.test_client()
    with client.session_transaction() as session:
        session['user'] = {'role': 'trainer', 'name': 'Amit Verma', 'email': 'amit@example.com'}

    login_response = client.get('/auth/login', follow_redirects=False)
    assert login_response.status_code == 302
    assert login_response.headers['Location'] == '/trainer/dashboard'

    dashboard_response = client.get('/trainer/dashboard')
    assert dashboard_response.status_code == 200
    assert b'logout' in dashboard_response.data.lower()


def test_trainee_dashboard_uses_session_user_name():
    app = create_app()
    client = app.test_client()
    with client.session_transaction() as session:
        session['user'] = {'role': 'trainee', 'name': 'Aarav Mehta', 'email': 'aarav@example.com'}

    response = client.get('/trainee/dashboard')
    assert response.status_code == 200
    assert b'Aarav Mehta' in response.data
    assert b'Priya Reddy' not in response.data


def test_trainee_dashboard_shows_enrolled_courses_from_session():
    app = create_app()
    client = app.test_client()
    with client.session_transaction() as session:
        session['user'] = {'role': 'trainee', 'name': 'Aarav Mehta', 'email': 'aarav@example.com'}
        session['enrolled_courses'] = ['python-for-operational-meteorology']

    response = client.get('/trainee/dashboard')
    assert response.status_code == 200
    assert b'Python for Operational Meteorology' in response.data


def test_admin_can_create_trainer_and_approve_users_with_password():
    app = create_app()
    client = app.test_client()
    with client.session_transaction() as session:
        session['user'] = {'role': 'admin', 'name': 'Admin User', 'email': 'admin@capacityconnect.in'}

    create_response = client.post('/admin/users', data={
        'name': 'Dr. Meera Singh',
        'email': 'meera@capacityconnect.in',
        'role': 'trainer',
        'password': 'TempPass123!',
        'status': 'Pending',
    }, follow_redirects=True)
    assert create_response.status_code == 200
    assert b'Dr. Meera Singh' in create_response.data
    assert b'Pending' in create_response.data

    approve_response = client.post('/admin/users/4/approve', follow_redirects=True)
    assert approve_response.status_code == 200
    assert b'Approved' in approve_response.data


def test_admin_can_create_trainer_and_approve_users():
    app = create_app()
    client = app.test_client()
    with client.session_transaction() as session:
        session['user'] = {'role': 'admin', 'name': 'Admin User', 'email': 'admin@capacityconnect.in'}

    create_response = client.post('/admin/users', data={
        'name': 'Dr. Meera Singh',
        'email': 'meera@capacityconnect.in',
        'role': 'trainer',
        'password': 'TempPass123!',
        'status': 'Approved',
    }, follow_redirects=True)
    assert create_response.status_code == 200
    assert b'Dr. Meera Singh' in create_response.data

    approve_response = client.post('/admin/users/4/approve', follow_redirects=True)
    assert approve_response.status_code == 200
    assert b'Approved' in approve_response.data


import sqlite3
import os

def cleanup_user(spawner):
    user_name = spawner.user.name
    print(f"Cleaning up user: {user_name}")
    
    db_path = '/home/jh/jupyterhub_project/jupyterhub.sqlite'
    
    if not os.path.exists(db_path):
        print("Database file not found.")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        delete_query = "DELETE FROM users WHERE name = ?"
        cursor.execute(delete_query, (user_name,))
        conn.commit()

        print(f"User {user_name} successfully removed from the database.")
    except sqlite3.Error as e:
        print(f"Failed to delete user {user_name} from database: {e}")
    finally:
        if conn:
            conn.close()

c = get_config()

c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
c.JupyterHub.hub_connect_ip = '172.18.0.1'
c.JupyterHub.port = 8000
c.JupyterHub.services = [
    {
        'name': 'cull-idle',
        'admin': True,
        'command': [
            'python3',
            '-m',
            'jupyterhub_idle_culler',
            '--timeout=2700'  
        ],
    }
]

c.DockerSpawner.image = 'limited-notebook'
c.DockerSpawner.use_internal_ip = True
c.DockerSpawner.network_name = 'jupyterhub'
c.DockerSpawner.remove_containers = True
c.DockerSpawner.extra_host_config = {
    'cap_drop': ['ALL'],
    'cap_add': ['CHOWN', 'SETUID', 'SETGID']
}

c.Spawner.cmd = ['jupyterhub-singleuser']
c.Spawner.args = [
    '--NotebookApp.token=',
    '--NotebookApp.password=',
    '--NotebookApp.allow_origin=*',
    '--ip=0.0.0.0',
    '--port=8888'
]

c.Spawner.environment = {
    'IDLE_WARNING': 'Ваша сессия будет прервана через 45 минут бездействия.'
}


c.Spawner.cpu_limit = 1  # Limit CPU cores
c.Spawner.mem_limit = '256M'  # Limit memory usage
c.Spawner.post_stop_hook = cleanup_user

# Set the default URL to open the notebook
c.Spawner.default_url = '/notebooks/notebook.ipynb'


# Use DummyAuthenticator for simple authentication
c.JupyterHub.authenticator_class = 'dummyauthenticator.DummyAuthenticator'
c.DummyAuthenticator.password = ''
c.Authenticator.allow_all = True

# Increase startup timeout
c.Spawner.start_timeout = 120
c.Spawner.http_timeout = 120



